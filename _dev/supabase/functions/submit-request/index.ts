// Avicon Travel — public endpoint for every form on avicontravel.com.
// Saves the request in public.form_requests, then notifies the team by email (Hostinger SMTP) and WhatsApp (Cloud API).
//
// Deploy: Supabase → Edge Functions → function name "submit-request", with "Verify JWT" turned OFF (public form).
// Accepts JSON, multipart or url-encoded bodies. A plain <form method="POST"> submit (a page navigation) is
// answered with a redirect to /thank-you/; fetch() calls get JSON {success, message}, the shape the site's scripts expect.
//
// Secrets (Edge Functions → Secrets). SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are provided automatically.
//   Email:    SMTP_HOST (smtp.hostinger.com), SMTP_PORT (465), SMTP_USER (the mailbox, e.g. info@avicontravel.com),
//             SMTP_PASS (that mailbox's password), NOTIFY_EMAIL_TO (comma-separated),
//             NOTIFY_EMAIL_FROM (optional, default "Avicon Website <SMTP_USER>"; Hostinger only accepts the
//             logged-in mailbox as the sender). Use port 465 (SSL): Supabase blocks outbound ports 25 and 587.
//   WhatsApp: WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_TO (comma-separated, digits with country code),
//             WHATSAPP_TEMPLATE (approved template name with 4 body variables, see README), WHATSAPP_TEMPLATE_LANG
//             (default "en"), WHATSAPP_API_VERSION (default "v21.0").
// A channel whose secrets are missing is skipped, so WhatsApp can be switched on later without redeploying.

// @deno-types="npm:@types/nodemailer@6.4.17"
import nodemailer from "npm:nodemailer@6.9.16";

const SITE = "https://avicontravel.com";
const ALLOWED_ORIGINS = new Set([SITE, "https://www.avicontravel.com", "http://127.0.0.1:8099", "http://localhost:8099"]);
const LABELS: Record<string, string> = {
  booking: "Booking request",
  contact: "Contact message",
  tailor_made: "Tailor-made trip request",
  transfer: "Transfer request",
  test: "Test request",
};
// column -> max length (0 = integer)
const COLUMNS: Record<string, number> = {
  tour_package: 200, subject: 200, name: 120, email: 200, phone: 60, travel_date: 40, travel_time: 20,
  adults: 0, children: 0, travelers: 40, destination: 200, pickup: 200, service: 120, estimated_total: 60,
  message: 4000, page_url: 500,
};
const ALIASES: Record<string, string> = { date: "travel_date", preferred_date: "travel_date", time: "travel_time", service_interest: "service" };
const IGNORE = new Set(["access_key", "from_name", "redirect", "botcheck", "form_type", "page_title"]);
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const WHATSAPP_URL = "https://wa.me/201200555600";
// Overridable only to point at a local mock while testing.
const GRAPH_BASE = () => env("WHATSAPP_API_BASE") || "https://graph.facebook.com";

const env = (key: string) => (Deno.env.get(key) ?? "").trim();
const list = (key: string) => env(key).split(",").map((s) => s.trim()).filter(Boolean);

type Fields = Record<string, string>;
type Row = Record<string, string | number | null | Record<string, string>>;

function corsHeaders(origin: string | null): Record<string, string> {
  return {
    "Access-Control-Allow-Origin": origin && ALLOWED_ORIGINS.has(origin) ? origin : SITE,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "content-type, accept",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
  };
}

async function readFields(req: Request): Promise<Fields> {
  const out: Fields = {};
  const type = req.headers.get("content-type") ?? "";
  if (type.includes("application/json")) {
    const body = await req.json().catch(() => null);
    if (body && typeof body === "object") {
      for (const [k, v] of Object.entries(body as Record<string, unknown>)) {
        if (v !== null && v !== undefined && typeof v !== "object") out[k] = String(v);
      }
    }
  } else {
    const form = await req.formData();
    for (const [k, v] of form.entries()) if (typeof v === "string") out[k] = v;
  }
  return out;
}

function guessType(f: Fields): string {
  if (f.form_type && LABELS[f.form_type]) return f.form_type;
  if (f.tour_package) return "booking";
  if (f.pickup) return "transfer";
  if (f.travelers || f.destination) return "tailor_made";
  return "contact";
}

function buildRow(f: Fields, req: Request): Row {
  const row: Row = {};
  const extra: Record<string, string> = {};
  for (const [rawKey, rawValue] of Object.entries(f)) {
    const key = ALIASES[rawKey] ?? rawKey;
    const value = rawValue.replace(/\u0000/g, "").trim();
    if (IGNORE.has(rawKey) || value === "") continue;
    if (key in COLUMNS) {
      if (COLUMNS[key] === 0) {
        const n = parseInt(value, 10);
        if (Number.isFinite(n) && n >= 0 && n < 1000) row[key] = n;
      } else if (row[key] === undefined) {
        row[key] = value.slice(0, COLUMNS[key]);
      }
    } else if (Object.keys(extra).length < 20) {
      extra[rawKey.slice(0, 60)] = value.slice(0, 1000);
    }
  }
  row.form_type = guessType(f);
  row.extra = extra;
  row.user_agent = (req.headers.get("user-agent") ?? "").slice(0, 300);
  if (!row.page_url) row.page_url = (req.headers.get("referer") ?? "").slice(0, 500) || null;
  if (typeof row.email === "string") row.email = row.email.toLowerCase();
  return row;
}

function validate(row: Row): string | null {
  if (typeof row.name !== "string" || row.name.length < 2) return "Please enter your name.";
  const email = typeof row.email === "string" ? row.email : "";
  const phone = typeof row.phone === "string" ? row.phone : "";
  if (!email && !phone) return "Please enter your email or phone number so we can reply.";
  if (email && !EMAIL_RE.test(email)) return "Please enter a valid email address.";
  if (phone && phone.replace(/\D/g, "").length < 6) return "Please enter a valid phone number.";
  return null;
}

function restHeaders(extra: Record<string, string> = {}): Record<string, string> {
  const key = env("SUPABASE_SERVICE_ROLE_KEY");
  const h: Record<string, string> = { apikey: key, "Content-Type": "application/json", ...extra };
  if (key.startsWith("eyJ")) h.Authorization = `Bearer ${key}`;
  return h;
}

const quote = (v: string) => `"${v.replace(/["\\]/g, "")}"`;

async function tooManyRecent(row: Row): Promise<boolean> {
  const filters: string[] = [];
  if (typeof row.email === "string") filters.push(`email.eq.${quote(row.email)}`);
  if (typeof row.phone === "string") filters.push(`phone.eq.${quote(row.phone)}`);
  if (!filters.length) return false;
  const since = new Date(Date.now() - 10 * 60 * 1000).toISOString();
  const url = `${env("SUPABASE_URL")}/rest/v1/form_requests?select=id&limit=5` +
    `&created_at=gte.${encodeURIComponent(since)}&or=${encodeURIComponent(`(${filters.join(",")})`)}`;
  const res = await fetch(url, { headers: restHeaders() });
  if (!res.ok) return false;
  const rows = await res.json();
  return Array.isArray(rows) && rows.length >= 5;
}

async function insertRow(row: Row): Promise<number> {
  const res = await fetch(`${env("SUPABASE_URL")}/rest/v1/form_requests`, {
    method: "POST",
    headers: restHeaders({ Prefer: "return=representation" }),
    body: JSON.stringify(row),
  });
  if (!res.ok) throw new Error(`insert failed ${res.status}: ${(await res.text()).slice(0, 300)}`);
  const [saved] = await res.json();
  return saved.id as number;
}

async function updateRow(id: number, patch: Record<string, unknown>) {
  await fetch(`${env("SUPABASE_URL")}/rest/v1/form_requests?id=eq.${id}`, {
    method: "PATCH",
    headers: restHeaders(),
    body: JSON.stringify(patch),
  }).catch((e) => console.error("update failed", e));
}

const FIELD_ORDER: [string, string][] = [
  ["tour_package", "Trip"], ["service", "Service"], ["destination", "Destination"], ["pickup", "Pickup"],
  ["name", "Name"], ["phone", "Phone"], ["email", "Email"], ["travel_date", "Date"], ["travel_time", "Time"],
  ["adults", "Adults"], ["children", "Children"], ["travelers", "Travelers"], ["estimated_total", "Estimated total"],
  ["message", "Message"], ["page_url", "Page"],
];

function summaryPairs(row: Row, id: number): [string, string][] {
  const pairs: [string, string][] = [["Request #", String(id)]];
  for (const [key, label] of FIELD_ORDER) {
    const v = row[key];
    if (v !== undefined && v !== null && v !== "") pairs.push([label, String(v)]);
  }
  for (const [k, v] of Object.entries((row.extra as Record<string, string>) ?? {})) pairs.push([k, v]);
  return pairs;
}

const esc = (s: string) =>
  s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" } as Record<string, string>)[c]);

let mailer: ReturnType<typeof nodemailer.createTransport> | null = null;

async function sendEmail(row: Row, id: number): Promise<void> {
  const host = env("SMTP_HOST");
  const user = env("SMTP_USER");
  const pass = env("SMTP_PASS");
  const to = list("NOTIFY_EMAIL_TO");
  if (!host || !user || !pass || !to.length) throw new Error("skipped: SMTP_HOST, SMTP_USER, SMTP_PASS or NOTIFY_EMAIL_TO not set");
  const port = Number(env("SMTP_PORT") || "465");
  mailer ??= nodemailer.createTransport({
    host,
    port,
    secure: env("SMTP_SECURE") ? env("SMTP_SECURE") === "true" : port === 465,
    auth: { user, pass },
    connectionTimeout: 15_000,
    greetingTimeout: 15_000,
    socketTimeout: 20_000,
  });
  const label = LABELS[String(row.form_type)] ?? "Website request";
  const topic = row.tour_package ?? row.service ?? row.destination ?? row.subject ?? "";
  const pairs = summaryPairs(row, id);
  const rows = pairs.map(([k, v]) =>
    `<tr><th align="left" style="padding:6px 12px 6px 0;color:#56657d;vertical-align:top;white-space:nowrap">${esc(k)}</th>` +
    `<td style="padding:6px 0;white-space:pre-wrap">${esc(v)}</td></tr>`).join("");
  await mailer.sendMail({
    from: env("NOTIFY_EMAIL_FROM") || `"Avicon Website" <${user}>`,
    to,
    replyTo: typeof row.email === "string" ? row.email : undefined,
    subject: `${label}${topic ? `: ${topic}` : ""} — ${row.name}`,
    text: pairs.map(([k, v]) => `${k}: ${v}`).join("\n"),
    html: `<div style="font-family:Arial,sans-serif;font-size:15px;color:#10233d"><h2 style="margin:0 0 12px">${esc(label)}</h2>` +
      `<table cellspacing="0" cellpadding="0">${rows}</table></div>`,
  });
}

// WhatsApp template parameters cannot contain new lines, tabs or more than 4 spaces in a row.
const waText = (s: string, max = 300) => s.replace(/[\r\n\t]+/g, " · ").replace(/ {2,}/g, " ").trim().slice(0, max) || "-";

async function sendWhatsApp(row: Row, id: number): Promise<void> {
  const token = env("WHATSAPP_TOKEN");
  const phoneId = env("WHATSAPP_PHONE_NUMBER_ID");
  const recipients = list("WHATSAPP_TO");
  if (!token || !phoneId || !recipients.length) throw new Error("skipped: WhatsApp secrets not set");
  const label = LABELS[String(row.form_type)] ?? "Website request";
  const topic = String(row.tour_package ?? row.service ?? row.destination ?? "");
  const contact = [row.phone, row.email].filter(Boolean).join(" · ");
  const people = [
    row.adults != null ? `${row.adults} adults` : "",
    row.children ? `${row.children} children` : "",
    row.travelers ? (/^\d+$/.test(String(row.travelers)) ? `${row.travelers} travelers` : String(row.travelers)) : "",
  ].filter(Boolean).join(", ");
  const details = [
    row.travel_date ? `Date ${row.travel_date}` : "",
    people,
    row.pickup ? `Pickup ${row.pickup}` : "",
    row.message ? String(row.message) : "",
  ].filter(Boolean).join(" · ");
  const params = [`${label} #${id}${topic ? ` (${topic})` : ""}`, String(row.name), contact, details];
  const template = env("WHATSAPP_TEMPLATE");
  const version = env("WHATSAPP_API_VERSION") || "v21.0";
  const errors: string[] = [];
  for (const to of recipients) {
    const message = template
      ? {
        type: "template",
        template: {
          name: template,
          language: { code: env("WHATSAPP_TEMPLATE_LANG") || "en" },
          components: [{ type: "body", parameters: params.map((p) => ({ type: "text", text: waText(p) })) }],
        },
      }
      : { type: "text", text: { body: [`*${params[0]}*`, `Name: ${params[1]}`, `Contact: ${params[2]}`, params[3]].join("\n") } };
    const res = await fetch(`${GRAPH_BASE()}/${version}/${phoneId}/messages`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ messaging_product: "whatsapp", to: to.replace(/\D/g, ""), ...message }),
    });
    if (!res.ok) errors.push(`whatsapp ${to} ${res.status}: ${(await res.text()).slice(0, 200)}`);
  }
  if (errors.length === recipients.length) throw new Error(errors.join(" | "));
  if (errors.length) console.error(errors.join(" | "));
}

async function notify(row: Row, id: number) {
  const [email, whatsapp] = await Promise.allSettled([sendEmail(row, id), sendWhatsApp(row, id)]);
  const problems = [email, whatsapp]
    .filter((r): r is PromiseRejectedResult => r.status === "rejected")
    .map((r) => String(r.reason?.message ?? r.reason));
  for (const p of problems) if (!p.startsWith("skipped")) console.error(p);
  await updateRow(id, {
    email_sent: email.status === "fulfilled",
    whatsapp_sent: whatsapp.status === "fulfilled",
    notify_error: problems.length ? problems.join(" | ").slice(0, 1000) : null,
  });
}

function reply(req: Request, ok: boolean, message: string, status = 200): Response {
  const headers = corsHeaders(req.headers.get("origin"));
  // A plain <form> submit is a page navigation; everything else (fetch, even without an Accept header) gets JSON.
  const mode = req.headers.get("sec-fetch-mode");
  const isNavigation = mode ? mode === "navigate" : (req.headers.get("accept") ?? "").includes("text/html");
  if (!isNavigation) {
    return new Response(JSON.stringify({ success: ok, message }), {
      status,
      headers: { ...headers, "Content-Type": "application/json" },
    });
  }
  if (ok) return new Response(null, { status: 303, headers: { ...headers, Location: `${SITE}/thank-you/` } });
  const page = `<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">` +
    `<title>Avicon Travel</title><body style="font-family:Arial,sans-serif;max-width:560px;margin:60px auto;padding:0 20px;color:#10233d">` +
    `<h1 style="font-size:22px">We could not send your request</h1><p>${esc(message)}</p>` +
    `<p><a href="javascript:history.back()">Go back and try again</a> or message us on <a href="${WHATSAPP_URL}">WhatsApp</a>.</p></body>`;
  return new Response(page, { status, headers: { ...headers, "Content-Type": "text/html; charset=utf-8" } });
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: corsHeaders(req.headers.get("origin")) });
  if (req.method !== "POST") return reply(req, false, "Method not allowed.", 405);
  if (Number(req.headers.get("content-length") ?? "0") > 50_000) return reply(req, false, "Your message is too long.", 413);

  let fields: Fields;
  try {
    fields = await readFields(req);
  } catch {
    return reply(req, false, "We could not read the form. Please try again.", 400);
  }
  // Honeypot: real visitors never fill this hidden field; answer "success" so bots learn nothing.
  if (fields.botcheck && fields.botcheck !== "false") return reply(req, true, "Thank you! We will contact you soon.");

  const row = buildRow(fields, req);
  const invalid = validate(row);
  if (invalid) return reply(req, false, invalid, 422);

  try {
    if (await tooManyRecent(row)) {
      return reply(req, false, "We already received several requests from you. Our team will reply shortly, or message us on WhatsApp.", 429);
    }
    const id = await insertRow(row);
    const job = notify(row, id);
    const runtime = (globalThis as { EdgeRuntime?: { waitUntil(p: Promise<unknown>): void } }).EdgeRuntime;
    if (runtime) runtime.waitUntil(job);
    else await job;
    return reply(req, true, "Thank you! Your request has been sent. We will contact you soon.");
  } catch (err) {
    console.error(err);
    return reply(req, false, "Something went wrong. Please try again or contact us on WhatsApp.", 500);
  }
});
