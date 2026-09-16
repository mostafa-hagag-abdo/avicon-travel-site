// Avicon Travel control panel: a static page (Arabic, RTL) on top of Supabase.
// Requests inbox + trips/packages editor. Saving stores a draft; "Publish" starts the GitHub workflow
// (Edge Function publish-site -> .github/workflows/publish-content.yml -> _dev/cms/sync.py).
import { html, render, useState, useEffect, useMemo, useRef, useCallback } from "https://cdn.jsdelivr.net/npm/htm@3.1.1/preact/standalone.module.js";
import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm";

const CFG = window.AVICON_CMS || {};
const DEMO = /[?&]demo\b/.test(location.search) && /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
const sb = DEMO ? (await import("./demo.js")).createDemoClient() : CFG.url && CFG.key ? createClient(CFG.url, CFG.key) : null;
const LOGO = "/assets/uploads/2026/05/cropped-cropped-Avicon-Travel-1-1.png.webp";

// ------------------------------------------------------------------------------------------------ vocabulary
const SECTIONS = { tours: "رحلات اليوم الواحد", "nile-cruises": "رحلات النيل", packages: "الباقات" };
const REQ_STATUS = { new: ["جديد", "red"], contacted: ["تم التواصل", "blue"], booked: ["تم الحجز", "green"], closed: ["مغلق", ""], spam: ["سبام", "violet"] };
const REQ_TYPE = { booking: "حجز رحلة", contact: "رسالة تواصل", tailor_made: "رحلة مخصصة", transfer: "توصيل", test: "تجربة" };
const JOB_STATUS = { queued: ["في الانتظار", "blue"], running: ["بيجهز الصفحات", "blue"], deploying: ["بيرفع على الموقع", "blue"], success: ["اتنشر", "green"], failed: ["ماكملش", "red"] };
const UNIT_LABELS = {
  "card.name": "الاسم", "blocks.price": "السعر", "blocks.title": "العنوان الكبير", "card.image": "صورة الكارت", "blocks.gallery": "الصور",
  "blocks.hero_image": "صورة الغلاف", "card.summary": "وصف الكارت", "card.location": "المكان", "card.duration": "المدة", "card.style": "النوع",
  "card.badge": "شارة الكارت", "card.home": "الظهور في الرئيسية", "blocks.badge": "الشارة", "blocks.chips": "المعلومات أعلى الصفحة",
  "blocks.overview": "النبذة", "blocks.facts": "مربعات المعلومات", "blocks.highlights": "أبرز المميزات", "blocks.route": "خط السير",
  "blocks.pricing": "جدول الأسعار", "blocks.longform": "الدليل التفصيلي", "blocks.itinerary": "البرنامج", "blocks.faq": "الأسئلة الشائعة",
  "blocks.included": "يشمل", "blocks.excluded": "لا يشمل", "seo.title": "عنوان جوجل", "seo.description": "وصف جوجل",
};
const ICONS = ["fa-clock", "fa-calendar-alt", "fa-calendar-check", "fa-sun", "fa-moon", "fa-user", "fa-users", "fa-user-tie", "fa-language", "fa-star",
  "fa-tag", "fa-tags", "fa-dollar-sign", "fa-gem", "fa-crown", "fa-hotel", "fa-bed", "fa-utensils", "fa-mug-hot", "fa-map-marker-alt", "fa-map-marked-alt",
  "fa-map-pin", "fa-location-dot", "fa-route", "fa-compass", "fa-plane", "fa-plane-departure", "fa-plane-arrival", "fa-car", "fa-van-shuttle", "fa-bus",
  "fa-train", "fa-ship", "fa-sailboat", "fa-anchor", "fa-water", "fa-umbrella-beach", "fa-fish", "fa-person-swimming", "fa-mountain", "fa-mountain-sun",
  "fa-tree", "fa-leaf", "fa-horse", "fa-feather-alt", "fa-paper-plane", "fa-arrow-right", "fa-landmark", "fa-monument", "fa-museum", "fa-ankh", "fa-mosque",
  "fa-place-of-worship", "fa-city", "fa-columns", "fa-palette", "fa-hammer", "fa-camera", "fa-ticket", "fa-shield-halved", "fa-circle-check", "fa-check",
  "fa-hand-holding-heart", "fa-baby", "fa-wheelchair", "fa-wifi"];

// ------------------------------------------------------------------------------------------------ helpers
const clone = (o) => (o == null ? o : JSON.parse(JSON.stringify(o)));
function same(a, b) {
  if (a === b) return true;
  if (a == null || b == null || typeof a !== "object" || typeof b !== "object" || Array.isArray(a) !== Array.isArray(b)) return false;
  const ka = Object.keys(a), kb = Object.keys(b);
  return ka.length === kb.length && ka.every((k) => same(a[k], b[k]));
}
function setIn(obj, path, value) {
  if (!path.length) return value;
  const [k, ...rest] = path;
  const copy = Array.isArray(obj) ? obj.slice() : { ...(obj || {}) };
  copy[k] = setIn(copy[k], rest, value);
  return copy;
}
const decoder = document.createElement("textarea");
const decode = (s) => { decoder.innerHTML = s ?? ""; return decoder.value; };
const encode = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const encodeAttr = (s) => encode(s).replace(/"/g, "&quot;");
const hasTags = (s) => /<\/?[a-z][^>]*>/i.test(s ?? "");
const plain = (s) => decode(String(s ?? "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
const amountOf = (p) => (p && /\d/.test(p.amount || "") ? parseInt(String(p.amount).replace(/[^\d]/g, ""), 10) : null);
const money = (n) => (n == null ? "عند الطلب" : "$" + n.toLocaleString("en-US"));
const rtf = new Intl.RelativeTimeFormat("ar-u-nu-latn", { numeric: "auto" });
const dtf = new Intl.DateTimeFormat("ar-EG-u-nu-latn", { dateStyle: "medium", timeStyle: "short" });
const fmtDate = (iso) => (iso ? dtf.format(new Date(iso)) : "—");
function ago(iso) {
  const s = (new Date(iso) - Date.now()) / 1000;
  for (const [u, sec] of [["year", 31536000], ["month", 2592000], ["week", 604800], ["day", 86400], ["hour", 3600], ["minute", 60]]) {
    if (Math.abs(s) >= sec) return rtf.format(Math.round(s / sec), u);
  }
  return "دلوقتي";
}
const uid = () => "f" + Math.random().toString(36).slice(2, 9);
function tripImage(card, blocks) {
  return card?.image?.src || blocks?.gallery?.[0]?.src || blocks?.hero_image?.src || "";
}
function derive(d) {
  const n = amountOf(d?.blocks?.price);
  const extra = d?.blocks?.facts?.extra;
  if (extra && "Price" in extra) {
    const v = n == null ? "On request" : `From $${n.toLocaleString("en-US")} / person`;
    if (extra.Price !== v) return setIn(d, ["blocks", "facts", "extra", "Price"], v);
  }
  return d;
}
function changedParts(row) {
  if (!row.live_data || !row.live_status) return ["رحلة جديدة"];
  const out = [];
  if (row.status !== row.live_status) out.push(row.status === "hidden" ? "إخفاء من الموقع" : "إظهار على الموقع");
  for (const [k, label] of Object.entries(UNIT_LABELS)) {
    const [a, b] = k.split(".");
    if (!same(row.data?.[a]?.[b], row.live_data?.[a]?.[b])) out.push(label);
  }
  return out;
}
function tripState(r) {
  if (r.status === "hidden" && r.live_status !== "published") return ["مخفية", ""];
  if (!r.live_status || (r.status === "published" && r.live_status !== "published")) return ["جاهزة للنشر", "amber"];
  if (r.status === "hidden") return ["هتتخفي بعد النشر", "amber"];
  if (r.has_changes) return ["تعديلات لم تُنشر", "amber"];
  return ["منشورة", "green"];
}
function validate(d) {
  const out = [], b = d.blocks || {}, n = amountOf(b.price);
  if (!plain(d.card?.name)) out.push("اكتب اسم الرحلة (تبويب الأساسي).");
  if (b.price && n == null && !/request/i.test(b.price.amount || "")) out.push("السعر لازم يكون رقم، أو اختار «عند الطلب».");
  const price = n == null ? "" : "$" + n.toLocaleString("en-US");
  const rawT = d.seo?.title || "", rawD = d.seo?.description || "";
  if (n == null && /\{price\}/.test(rawT + rawD)) out.push("السعر «عند الطلب»: امسح {price} من عنوان ووصف جوجل.");
  const t = rawT.replace("{price}", price), ds = rawD.replace("{price}", price);
  if (!t.trim()) out.push("اكتب عنوان جوجل (تبويب جوجل).");
  else if (t.length > 60) out.push(`عنوان جوجل ${t.length} حرف، والحد الأقصى 60.`);
  if (ds.length < 120 || ds.length > 160) out.push(`وصف جوجل ${ds.length} حرف، ولازم يكون من 120 لـ 160.`);
  (b.gallery || []).forEach((g, i) => {
    if (!g.src) out.push(`الصورة رقم ${i + 1} من غير ملف.`);
    else if (!plain(g.alt)) out.push(`اكتب وصف الصورة رقم ${i + 1} (تبويب الصور).`);
  });
  return out;
}
function go(hash) {
  if (window.__cmsDirty && !confirm("في تعديلات مش محفوظة. تسيبها؟")) return;
  window.__cmsDirty = false;
  location.hash = hash;
}
function guardLink(e) {
  if (window.__cmsDirty && !confirm("في تعديلات مش محفوظة. تسيبها؟")) e.preventDefault();
  else window.__cmsDirty = false;
}
addEventListener("beforeunload", (e) => { if (window.__cmsDirty) { e.preventDefault(); e.returnValue = ""; } });

// global toasts + counts
let showToast = null;
const toast = (msg, bad = false) => showToast && showToast({ msg, bad, id: Date.now() });
let countsNow = { requests: 0, pending: 0 };
const countSubs = new Set();
async function refreshCounts() {
  const [r, p] = await Promise.all([
    sb.from("form_requests").select("id", { count: "exact", head: true }).eq("status", "new"),
    sb.from("products").select("slug", { count: "exact", head: true }).eq("has_changes", true),
  ]);
  countsNow = { requests: r.count || 0, pending: p.count || 0 };
  countSubs.forEach((f) => f(countsNow));
}
function useCounts() {
  const [c, setC] = useState(countsNow);
  useEffect(() => { countSubs.add(setC); return () => countSubs.delete(setC); }, []);
  return c;
}
function useRoute() {
  const [h, setH] = useState(location.hash);
  useEffect(() => {
    const f = () => setH(location.hash);
    addEventListener("hashchange", f);
    return () => removeEventListener("hashchange", f);
  }, []);
  const parts = (h || "#/requests").replace(/^#\/?/, "").split("/").map(decodeURIComponent);
  return parts[0] ? parts : ["requests"];
}

// ------------------------------------------------------------------------------------------------ app
function App() {
  const [session, setSession] = useState(undefined);
  const [member, setMember] = useState(undefined);
  const [recovery, setRecovery] = useState(/type=recovery/.test(location.hash));
  useEffect(() => {
    if (!sb) return;
    sb.auth.getSession().then(({ data }) => setSession(data.session));
    const { data } = sb.auth.onAuthStateChange((event, s) => {
      if (event === "PASSWORD_RECOVERY") setRecovery(true);
      setSession(s);
    });
    return () => data.subscription.unsubscribe();
  }, []);
  useEffect(() => {
    if (!session) { setMember(undefined); return; }
    sb.from("admins").select("*").eq("user_id", session.user.id).maybeSingle().then(({ data, error }) => setMember(error ? null : data || null));
  }, [session?.user?.id]);

  if (!sb) return html`<${Setup} />`;
  if (session === undefined || (session && member === undefined)) return html`<div class="boot">جارٍ التحميل…</div>`;
  if (session && recovery) return html`<${NewPassword} done=${() => { setRecovery(false); location.hash = "#/requests"; }} />`;
  if (!session) return html`<${Login} />`;
  if (!member) return html`<${NotMember} email=${session.user.email} />`;
  return html`<${Shell} member=${member} />`;
}

function Brand() {
  return html`<div class="brand"><img src=${LOGO} alt="" width="34" height="34" /><div><b>Avicon Travel</b><span>لوحة التحكم</span></div></div>`;
}

function Setup() {
  return html`<div class="login"><div class="card"><${Brand} />
    <h1>لوحة التحكم لسه مش متوصلة</h1>
    <p class="muted">ناقص مفتاح Supabase العام في إعدادات GitHub (متغير <span class="ltr">SUPABASE_ANON_KEY</span>). بعد إضافته ونشر الموقع، الصفحة دي هتشتغل.</p>
  </div></div>`;
}

function authError(error) {
  const m = error?.message || "";
  if (/invalid login/i.test(m)) return "الإيميل أو كلمة السر مش صح.";
  if (/rate|too many/i.test(m)) return "محاولات كتير ورا بعض. استنى دقيقة وجرب تاني.";
  if (/password.*(short|least|characters)/i.test(m)) return "كلمة السر لازم تكون 8 حروف على الأقل.";
  return "حصلت مشكلة: " + m;
}

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState("login");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [sent, setSent] = useState(false);
  async function submit(e) {
    e.preventDefault();
    setBusy(true); setErr("");
    if (mode === "reset") {
      const { error } = await sb.auth.resetPasswordForEmail(email, { redirectTo: location.origin + location.pathname });
      setBusy(false);
      error ? setErr(authError(error)) : setSent(true);
      return;
    }
    const { error } = await sb.auth.signInWithPassword({ email, password });
    setBusy(false);
    if (error) setErr(authError(error));
  }
  return html`<div class="login"><form class="card" onSubmit=${submit}>
    <${Brand} />
    <h1>${mode === "login" ? "تسجيل الدخول" : "نسيت كلمة السر"}</h1>
    ${DEMO ? html`<div class="notice"><i class="fas fa-flask"></i><span>وضع التجربة: أي إيميل وكلمة سر هيدخلوك ببيانات تجريبية.</span></div>` : null}
    ${sent ? html`<div class="notice green"><i class="fas fa-envelope"></i><span>بعتنا رابط تغيير كلمة السر على ${email}.</span></div>` : null}
    <div class="field"><label for="em">الإيميل</label><input id="em" type="email" class="en" required autocomplete="username" value=${email} onInput=${(e) => setEmail(e.target.value)} /></div>
    ${mode === "login" ? html`<div class="field"><label for="pw">كلمة السر</label><input id="pw" type="password" class="en" required autocomplete="current-password" value=${password} onInput=${(e) => setPassword(e.target.value)} /></div>` : null}
    ${err ? html`<div class="notice red"><i class="fas fa-circle-exclamation"></i><span>${err}</span></div>` : null}
    <button class="btn primary" disabled=${busy}>${busy ? html`<i class="fas fa-spinner spin"></i>` : null} ${mode === "login" ? "دخول" : "ابعت رابط التغيير"}</button>
    <button type="button" class="btn ghost sm" onClick=${() => { setMode(mode === "login" ? "reset" : "login"); setErr(""); setSent(false); }}>${mode === "login" ? "نسيت كلمة السر؟" : "رجوع لتسجيل الدخول"}</button>
  </form></div>`;
}

function NewPassword({ done }) {
  const [pw, setPw] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    const { error } = await sb.auth.updateUser({ password: pw });
    setBusy(false);
    if (error) return setErr(authError(error));
    toast("اتغيرت كلمة السر ✓");
    done();
  }
  return html`<div class="login"><form class="card" onSubmit=${submit}><${Brand} /><h1>اختار كلمة سر جديدة</h1>
    <div class="field"><label for="np">كلمة السر الجديدة</label><input id="np" type="password" class="en" minlength="8" required autocomplete="new-password" value=${pw} onInput=${(e) => setPw(e.target.value)} /><div class="hint">8 حروف على الأقل.</div></div>
    ${err ? html`<div class="notice red"><span>${err}</span></div>` : null}
    <button class="btn primary" disabled=${busy}>حفظ كلمة السر</button></form><${Toasts} /></div>`;
}

function NotMember({ email }) {
  return html`<div class="login"><div class="card"><${Brand} /><h1>الحساب ده مش ضمن الفريق</h1>
    <p class="muted">دخلت بـ <span class="ltr">${email}</span>، بس الحساب مش متضاف لفريق لوحة التحكم. اطلب من صاحب الحساب الرئيسي يضيفك.</p>
    <button class="btn" onClick=${() => sb.auth.signOut()}>تسجيل الخروج</button></div></div>`;
}

function ThemeButton() {
  const order = ["system", "light", "dark"];
  const read = () => { try { return localStorage.getItem("avicon-admin-theme") || "system"; } catch { return "system"; } };
  const [mode, setMode] = useState(read);
  useEffect(() => {
    if (mode === "system") delete document.documentElement.dataset.theme;
    else document.documentElement.dataset.theme = mode;
    try { localStorage.setItem("avicon-admin-theme", mode); } catch { /* private mode */ }
  }, [mode]);
  const label = { system: "مظهر الجهاز", light: "فاتح", dark: "داكن" }[mode];
  const icon = { system: "fa-circle-half-stroke", light: "fa-sun", dark: "fa-moon" }[mode];
  return html`<button class="btn ghost sm" onClick=${() => setMode(order[(order.indexOf(mode) + 1) % 3])}><i class="fas ${icon}"></i> ${label}</button>`;
}

function Shell({ member }) {
  const route = useRoute();
  const counts = useCounts();
  useEffect(() => {
    refreshCounts();
    const t = setInterval(refreshCounts, 60000);
    addEventListener("cms:changed", refreshCounts);
    return () => { clearInterval(t); removeEventListener("cms:changed", refreshCounts); };
  }, []);
  const view = route[0];
  let page;
  if (view === "trips" && route[1] === "new") page = html`<${NewTrip} />`;
  else if (view === "trips" && route[2]) page = html`<${TripEditor} key=${route[1] + "/" + route[2]} slug=${route[1] + "/" + route[2]} tab=${route[3] || "basics"} />`;
  else if (view === "trips") page = html`<${Trips} section=${route[1] || "all"} />`;
  else if (view === "publish") page = html`<${Publish} />`;
  else page = html`<${Requests} openId=${route[1]} />`;
  const link = (hash, icon, label, extra) => html`<a href=${hash} onClick=${guardLink} aria-current=${view === hash.slice(2) ? "page" : undefined}><i class="fas ${icon}"></i><span>${label}</span>${extra}</a>`;
  return html`<div class="shell">
    <aside class="side">
      <${Brand} />
      <nav class="nav">
        ${link("#/requests", "fa-inbox", "الطلبات", counts.requests ? html`<span class="count num">${counts.requests}</span>` : null)}
        ${link("#/trips", "fa-map-location-dot", "الرحلات والباقات")}
        ${link("#/publish", "fa-cloud-arrow-up", "النشر", counts.pending ? html`<span class="count amber num">${counts.pending}</span>` : null)}
      </nav>
      <div class="side-foot">
        <span class="who ltr" title=${member.email}>${member.name || member.email}</span>
        <${ThemeButton} />
        <button class="btn ghost sm" onClick=${() => { if (!window.__cmsDirty || confirm("في تعديلات مش محفوظة. تخرج؟")) sb.auth.signOut(); }}><i class="fas fa-right-from-bracket"></i> خروج</button>
      </div>
    </aside>
    <main class="main">${page}</main>
    <${Toasts} />
  </div>`;
}

function TopBar({ title, sub, children }) {
  const counts = useCounts();
  return html`<header class="top">
    <div><h1>${title}</h1>${sub ? html`<div class="faint">${sub}</div>` : null}</div>
    <div class="grow"></div>
    ${children}
    <a class="btn ${counts.pending ? "publish" : ""}" href="#/publish" onClick=${guardLink}><i class="fas fa-cloud-arrow-up"></i> نشر${counts.pending ? html` <span class="num">(${counts.pending})</span>` : null}</a>
  </header>`;
}

function Toasts() {
  const [t, setT] = useState(null);
  showToast = setT;
  useEffect(() => {
    if (!t) return;
    const x = setTimeout(() => setT(null), t.bad ? 7000 : 3500);
    return () => clearTimeout(x);
  }, [t?.id]);
  return t ? html`<div class="toast ${t.bad ? "bad" : ""}" role="status">${t.msg}</div>` : null;
}

function Pill({ label, tone }) {
  return html`<span class="pill ${tone || ""}">${label}</span>`;
}

// ------------------------------------------------------------------------------------------------ requests
const REQ_PAGE = 50;

function Requests({ openId }) {
  const [status, setStatus] = useState("all");
  const [type, setType] = useState("all");
  const [term, setTerm] = useState("");
  const [query, setQuery] = useState("");
  const [rows, setRows] = useState(null);
  const [limit, setLimit] = useState(REQ_PAGE);
  const [err, setErr] = useState("");
  useEffect(() => { const t = setTimeout(() => setQuery(term.trim()), 300); return () => clearTimeout(t); }, [term]);
  const load = useCallback(async () => {
    let q = sb.from("form_requests").select("*").order("created_at", { ascending: false }).range(0, limit - 1);
    if (status !== "all") q = q.eq("status", status);
    if (type !== "all") q = q.eq("form_type", type);
    const safe = query.replace(/[,()*%\\]/g, " ").trim();
    if (safe) q = q.or(["name", "email", "phone", "tour_package", "service", "destination"].map((c) => `${c}.ilike.*${safe}*`).join(","));
    const { data, error } = await q;
    if (error) { setErr(error.message); return; }
    setErr(""); setRows(data);
  }, [status, type, query, limit]);
  useEffect(() => { load(); const t = setInterval(load, 60000); return () => clearInterval(t); }, [load]);
  const open = rows?.find((r) => String(r.id) === openId);
  const onSaved = (r) => { setRows((list) => list.map((x) => (x.id === r.id ? r : x))); refreshCounts(); };

  return html`<${TopBar} title="الطلبات" sub="كل اللي بيتبعت من فورمات الموقع">
      <button class="btn ghost" onClick=${load} title="تحديث"><i class="fas fa-rotate"></i></button>
    <//>
    <div class="page">
      <div class="toolbar">
        <div class="seg" role="group" aria-label="الحالة">
          ${[["all", "الكل"], ...Object.entries(REQ_STATUS).map(([k, v]) => [k, v[0]])].map(([k, label]) =>
            html`<button aria-pressed=${status === k} onClick=${() => { setStatus(k); setLimit(REQ_PAGE); }}>${label}</button>`)}
        </div>
        <div class="field" style="flex:0 0 170px"><select aria-label="نوع الطلب" value=${type} onChange=${(e) => setType(e.target.value)}>
          <option value="all">كل الأنواع</option>
          ${Object.entries(REQ_TYPE).map(([k, v]) => html`<option value=${k}>${v}</option>`)}
        </select></div>
        <div class="field search"><i class="fas fa-magnifying-glass"></i><input type="search" placeholder="ابحث بالاسم أو الموبايل أو الرحلة" value=${term} onInput=${(e) => setTerm(e.target.value)} /></div>
      </div>
      ${err ? html`<div class="notice red"><i class="fas fa-circle-exclamation"></i><span>مقدرناش نجيب الطلبات: ${err}</span></div>` : null}
      ${rows === null && !err ? html`<div class="card empty"><i class="fas fa-spinner spin"></i>جارٍ التحميل…</div>` : null}
      ${rows && !rows.length ? html`<div class="card empty"><i class="fas fa-inbox"></i>مفيش طلبات بالشروط دي.</div>` : null}
      ${rows && rows.length ? html`<div class="card req-list">
        <div class="req-head"><span>وصل</span><span>العميل</span><span>الطلب</span><span>النوع</span><span>الحالة</span></div>
        ${rows.map((r) => html`<button key=${r.id} class="req ${r.status === "new" ? "is-new" : ""}" aria-current=${String(r.id) === openId ? "true" : undefined} onClick=${() => { location.hash = `#/requests/${r.id}`; }}>
          <span class="when" title=${fmtDate(r.created_at)}>${ago(r.created_at)}</span>
          <span class="who"><b>${r.name}</b><span class="ltr">${r.phone || r.email || ""}</span></span>
          <span class="what"><b class="ltr">${r.tour_package || r.service || r.destination || r.subject || "—"}</b><span dir="auto">${requestLine(r)}</span></span>
          <span class="type"><span class="pill plain">${REQ_TYPE[r.form_type] || r.form_type}</span></span>
          <span class="status"><${Pill} label=${REQ_STATUS[r.status]?.[0] || r.status} tone=${REQ_STATUS[r.status]?.[1]} /></span>
        </button>`)}
      </div>` : null}
      ${rows && rows.length === limit ? html`<div style="text-align:center;margin-top:16px"><button class="btn" onClick=${() => setLimit(limit + REQ_PAGE)}>عرض طلبات أقدم</button></div>` : null}
    </div>
    ${open ? html`<${RequestDrawer} key=${open.id} r=${open} onSaved=${onSaved} onClose=${() => { location.hash = "#/requests"; }} />` : null}`;
}

function requestLine(r) {
  const bits = [];
  if (r.travel_date) bits.push(r.travel_date);
  const people = [r.adults ? `${r.adults} بالغ` : "", r.children ? `${r.children} طفل` : ""].filter(Boolean).join(" + ") || r.travelers;
  if (people) bits.push(people);
  if (!bits.length && r.message) bits.push(r.message.slice(0, 70));
  return bits.join(" · ");
}

function RequestDrawer({ r, onSaved, onClose }) {
  const [notes, setNotes] = useState(r.notes || "");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    const esc = (e) => e.key === "Escape" && onClose();
    addEventListener("keydown", esc);
    return () => removeEventListener("keydown", esc);
  }, []);
  async function patch(fields, done) {
    setBusy(true);
    const { data, error } = await sb.from("form_requests").update(fields).eq("id", r.id).select("*").single();
    setBusy(false);
    if (error) return toast("ما اتحفظش: " + error.message, true);
    onSaved(data);
    toast(done);
  }
  const digits = (r.phone || "").replace(/[^\d]/g, "").replace(/^00/, "");
  const what = r.tour_package || r.service || r.destination || "your trip";
  const hello = `Hello ${r.name}, thank you for contacting Avicon Travel about ${what}.`;
  const rows = [
    ["الإيميل", r.email && html`<a class="ltr" href=${"mailto:" + r.email}>${r.email}</a>`],
    ["الموبايل", r.phone && html`<a class="ltr" href=${"tel:" + r.phone}>${r.phone}</a>`],
    ["نوع الطلب", REQ_TYPE[r.form_type] || r.form_type],
    ["الرحلة / الخدمة", r.tour_package || r.service ? html`<span class="ltr">${r.tour_package || r.service}</span>` : null],
    ["الموضوع", r.subject && html`<span class="ltr">${r.subject}</span>`],
    ["تاريخ السفر", r.travel_date && html`<span class="ltr">${r.travel_date}${r.travel_time ? " · " + r.travel_time : ""}</span>`],
    ["البالغين", r.adults], ["الأطفال", r.children], ["عدد المسافرين", r.travelers],
    ["الوجهة", r.destination && html`<span class="ltr">${r.destination}</span>`],
    ["مكان الاستلام", r.pickup && html`<span class="ltr">${r.pickup}</span>`],
    ["التكلفة التقديرية", r.estimated_total && html`<span class="ltr">${r.estimated_total}</span>`],
    ["من صفحة", r.page_url && html`<a class="ltr" href=${r.page_url} target="_blank" rel="noopener">${r.page_url.replace(/^https?:\/\/(www\.)?avicontravel\.com/, "")}</a>`],
    ["وصل", fmtDate(r.created_at)],
    ["التنبيهات", html`<span>إيميل ${r.email_sent ? "✓" : "✗"} · واتساب ${r.whatsapp_sent ? "✓" : "✗"}</span>${r.notify_error ? html`<div class="faint ltr">${r.notify_error}</div>` : null}`],
  ].filter(([, v]) => v !== null && v !== undefined && v !== "");
  const extra = r.extra && typeof r.extra === "object" ? Object.entries(r.extra).filter(([, v]) => v !== "" && v != null) : [];
  return html`<div class="drawer-backdrop" onClick=${onClose}></div>
    <aside class="drawer" role="dialog" aria-label=${"طلب " + r.name}>
      <header><h2>${r.name}</h2><${Pill} label=${REQ_STATUS[r.status]?.[0]} tone=${REQ_STATUS[r.status]?.[1]} /><button class="btn ghost icon" onClick=${onClose} aria-label="إغلاق"><i class="fas fa-xmark"></i></button></header>
      <div class="body">
        <div class="quick">
          ${digits ? html`<a class="btn" target="_blank" rel="noopener" href=${`https://wa.me/${digits}?text=${encodeURIComponent(hello)}`}><i class="fab fa-whatsapp"></i> واتساب</a>` : null}
          ${r.phone ? html`<a class="btn" href=${"tel:" + r.phone}><i class="fas fa-phone"></i> اتصال</a>` : null}
          ${r.email ? html`<a class="btn" href=${`mailto:${r.email}?subject=${encodeURIComponent("Avicon Travel: " + what)}&body=${encodeURIComponent(hello + "\n\n")}`}><i class="fas fa-envelope"></i> إيميل</a>` : null}
        </div>
        <div class="field"><span class="label">الحالة</span>
          <div class="seg">${Object.entries(REQ_STATUS).map(([k, v]) => html`<button disabled=${busy} aria-pressed=${r.status === k} onClick=${() => r.status !== k && patch({ status: k }, "اتغيرت الحالة ✓")}>${v[0]}</button>`)}</div>
        </div>
        <dl class="kv">${rows.map(([k, v]) => html`<dt>${k}</dt><dd>${v}</dd>`)}</dl>
        ${r.message ? html`<div class="field"><span class="label">الرسالة</span><div class="msg ltr">${r.message}</div></div>` : null}
        ${extra.length ? html`<div class="field"><span class="label">بيانات إضافية</span><dl class="kv">${extra.map(([k, v]) => html`<dt class="ltr">${k}</dt><dd class="ltr">${typeof v === "object" ? JSON.stringify(v) : String(v)}</dd>`)}</dl></div>` : null}
        <div class="field"><label for="notes">ملاحظات الفريق</label>
          <textarea id="notes" value=${notes} placeholder="مثلاً: كلمته، مستني تأكيد التاريخ" onInput=${(e) => setNotes(e.target.value)}></textarea>
          <div><button class="btn sm" disabled=${busy || notes === (r.notes || "")} onClick=${() => patch({ notes }, "اتحفظت الملاحظات ✓")}>حفظ الملاحظات</button></div>
        </div>
      </div>
    </aside>`;
}

// ------------------------------------------------------------------------------------------------ trips list
const LIST_COLUMNS = "slug,section,status,live_status,has_changes,sort_order,updated_at,published_at,template,card:data->card,price:data->blocks->price,gallery:data->blocks->gallery,hero:data->blocks->hero_image";

function Trips({ section }) {
  const [rows, setRows] = useState(null);
  const [term, setTerm] = useState("");
  const [err, setErr] = useState("");
  useEffect(() => {
    sb.from("products").select(LIST_COLUMNS).order("sort_order").then(({ data, error }) => (error ? setErr(error.message) : setRows(data)));
  }, []);
  const shown = (rows || []).filter((r) => (section === "all" || r.section === section) && (!term || plain(r.card?.name).toLowerCase().includes(term.toLowerCase())));
  return html`<${TopBar} title="الرحلات والباقات" sub="اختار رحلة لتعديلها. التعديلات بتتحفظ كمسودة لحد ما تضغط «نشر».">
      <a class="btn primary" href="#/trips/new"><i class="fas fa-plus"></i> رحلة جديدة</a>
    <//>
    <div class="page">
      <div class="toolbar">
        <div class="seg">${[["all", "الكل"], ...Object.entries(SECTIONS)].map(([k, v]) => html`<button aria-pressed=${section === k} onClick=${() => { location.hash = k === "all" ? "#/trips" : `#/trips/${k}`; }}>${v}${rows ? html` <span class="faint num">${k === "all" ? rows.length : rows.filter((r) => r.section === k).length}</span>` : null}</button>`)}</div>
        <div class="field search"><i class="fas fa-magnifying-glass"></i><input type="search" placeholder="ابحث باسم الرحلة" value=${term} onInput=${(e) => setTerm(e.target.value)} /></div>
      </div>
      ${err ? html`<div class="notice red"><span>مقدرناش نجيب الرحلات: ${err}</span></div>` : null}
      ${rows === null && !err ? html`<div class="card empty"><i class="fas fa-spinner spin"></i>جارٍ التحميل…</div>` : null}
      ${rows && !rows.length ? html`<div class="card empty"><i class="fas fa-map"></i>لسه مفيش رحلات في لوحة التحكم. شغّل «Update control panel from the site» مرة واحدة من GitHub Actions.</div>` : null}
      <div class="trip-grid">
        ${shown.map((r) => {
          const [label, tone] = tripState(r);
          const img = tripImage(r.card, { gallery: r.gallery, hero_image: r.hero });
          return html`<a class="trip" key=${r.slug} href=${"#/trips/" + r.slug}>
            <div class="img">${img ? html`<img src=${img} alt="" loading="lazy" />` : null}<${Pill} label=${label} tone=${tone} /></div>
            <div class="body"><b class="ltr" style="text-align:left">${plain(r.card?.name)}</b>
              <div class="meta"><span>${SECTIONS[r.section]}</span><span class="num">${money(amountOf(r.price))}</span></div></div>
          </a>`;
        })}
      </div>
    </div>`;
}

// ------------------------------------------------------------------------------------------------ new trip
function NewTrip() {
  const [rows, setRows] = useState(null);
  const [section, setSection] = useState("tours");
  const [template, setTemplate] = useState("");
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [slugTouched, setSlugTouched] = useState(false);
  const [busy, setBusy] = useState(false);
  useEffect(() => { sb.from("products").select(LIST_COLUMNS).order("sort_order").then(({ data }) => setRows(data || [])); }, []);
  const options = (rows || []).filter((r) => r.section === section);
  useEffect(() => { setTemplate(options[0]?.slug || ""); }, [section, rows]);
  const autoSlug = name.toLowerCase().normalize("NFKD").replace(/&/g, " and ").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 70);
  const finalSlug = slugTouched ? slug : autoSlug;
  const full = `${section}/${finalSlug}`;
  const problem = !name.trim() ? "اكتب اسم الرحلة بالإنجليزي."
    : !/^[a-z0-9]+(-[a-z0-9]+)*$/.test(finalSlug) ? "الرابط لازم يكون حروف إنجليزي صغيرة وأرقام وشرطة (-) بس."
    : (rows || []).some((r) => r.slug === full) ? "في رحلة تانية بنفس الرابط." : !template ? "اختار رحلة تتنسخ منها الصفحة." : "";
  async function create() {
    setBusy(true);
    const { data: tpl, error } = await sb.from("products").select("*").eq("slug", template).single();
    if (error) { setBusy(false); return toast("مقدرناش نجيب الرحلة الأصلية: " + error.message, true); }
    let data = clone(tpl.data);
    data = setIn(data, ["card", "name"], encode(name.trim()));
    data = setIn(data, ["card", "home"], false);
    data = setIn(data, ["blocks", "title"], encode(name.trim()));
    data = setIn(data, ["seo"], { title: "", description: "" });
    const { error: e2 } = await sb.from("products").insert({ slug: full, section, status: "hidden", template, data, sort_order: (tpl.sort_order || 0) + 5 });
    setBusy(false);
    if (e2) return toast("ما اتعملتش: " + e2.message, true);
    dispatchEvent(new Event("cms:changed"));
    toast("اتعملت الرحلة كنسخة ✓ عدّل بياناتها وبعدين فعّل «ظاهرة على الموقع»");
    location.hash = `#/trips/${full}`;
  }
  return html`<${TopBar} title="رحلة جديدة" sub="الرحلة الجديدة بتبدأ كنسخة من رحلة موجودة (نفس شكل الصفحة)، وبعدين تعدّل محتواها." />
    <div class="page"><div class="group" style="max-width:720px">
      <div class="field"><span class="label">القسم</span><div class="seg">${Object.entries(SECTIONS).map(([k, v]) => html`<button aria-pressed=${section === k} onClick=${() => setSection(k)}>${v}</button>`)}</div></div>
      <div class="field"><label for="tpl">انسخ الصفحة من</label>
        <select id="tpl" value=${template} onChange=${(e) => setTemplate(e.target.value)}>${options.map((r) => html`<option value=${r.slug}>${plain(r.card?.name)}</option>`)}</select>
        <div class="hint">اختار أقرب رحلة شبه الجديدة: كل المحتوى هيتنسخ وإنت تغيّره.</div></div>
      <div class="field"><label for="nm">اسم الرحلة (بالإنجليزي، زي ما هيظهر للعميل)</label><input id="nm" type="text" class="en" placeholder="Luxor Balloon & West Bank Day Tour" value=${name} onInput=${(e) => setName(e.target.value)} /></div>
      <div class="field"><label for="sl">رابط الصفحة</label>
        <div class="row" style="align-items:center;gap:6px"><span class="faint ltr">avicontravel.com/${section}/</span>
          <input id="sl" type="text" class="en" style="flex:1" value=${finalSlug} onInput=${(e) => { setSlugTouched(true); setSlug(e.target.value.trim()); }} /></div>
        <div class="hint">مينفعش يتغير بعد النشر من غير ما نعمل تحويل، فاختاره كويس.</div></div>
      ${problem && name ? html`<div class="notice amber"><i class="fas fa-triangle-exclamation"></i><span>${problem}</span></div>` : null}
      <div class="row"><button class="btn primary" disabled=${busy || !!problem} onClick=${create}>${busy ? html`<i class="fas fa-spinner spin"></i>` : html`<i class="fas fa-copy"></i>`} اعمل الرحلة</button>
        <a class="btn ghost" href="#/trips">إلغاء</a></div>
    </div></div>`;
}

// ------------------------------------------------------------------------------------------------ form parts
function Field({ label, hint, value, onChange, long, attr, placeholder, en = true }) {
  const id = useMemo(uid, []);
  const enc = attr ? encodeAttr : encode;
  let control;
  if (hasTags(value)) control = html`<${Rich} value=${value} onChange=${onChange} />`;
  else if (long) control = html`<textarea id=${id} class=${en ? "en" : ""} placeholder=${placeholder} value=${decode(value)} onInput=${(e) => onChange(enc(e.target.value))}></textarea>`;
  else control = html`<input id=${id} type="text" class=${en ? "en" : ""} placeholder=${placeholder} value=${decode(value)} onInput=${(e) => onChange(enc(e.target.value))} />`;
  return html`<div class="field">${label ? html`<label for=${id}>${label}</label>` : null}${control}${hint ? html`<div class="hint">${hint}</div>` : null}</div>`;
}

const RICH_TAGS = { P: ["class", "style"], BR: [], STRONG: [], EM: [], A: ["href", "target", "rel", "style", "class"], UL: ["class", "style"], OL: ["class", "style"],
  LI: ["class", "style"], H3: ["class", "style"], H4: ["class", "style"], SPAN: ["class", "style"], I: ["class"], SMALL: [], DEL: [], TABLE: ["class", "style"],
  THEAD: [], TBODY: [], TR: [], TH: [], TD: [] };
function sanitize(input, block) {
  const doc = new DOMParser().parseFromString(`<body>${input}</body>`, "text/html");
  const walk = (node) => {
    for (const el of [...node.childNodes]) {
      if (el.nodeType === 3) continue;
      if (el.nodeType !== 1) { el.remove(); continue; }
      walk(el);
      const tag = el.tagName;
      if (tag === "B" || (tag === "I" && !/\bfa/.test(el.className))) {
        const n = doc.createElement(tag === "B" ? "strong" : "em");
        n.append(...el.childNodes);
        el.replaceWith(n);
        continue;
      }
      if (tag === "DIV" && block) {
        const p = doc.createElement("p");
        p.append(...el.childNodes);
        el.replaceWith(p);
        continue;
      }
      if (!RICH_TAGS[tag] || (!block && ["P", "UL", "OL", "LI", "H3", "H4", "TABLE"].includes(tag))) { el.replaceWith(...el.childNodes); continue; }
      for (const a of [...el.attributes]) if (!RICH_TAGS[tag].includes(a.name)) el.removeAttribute(a.name);
      if (tag === "A" && !/^(https?:|mailto:|tel:|\/|#)/i.test(el.getAttribute("href") || "")) el.removeAttribute("href");
    }
  };
  walk(doc.body);
  return doc.body.innerHTML.replace(/ /g, " ").trim();
}

function Rich({ value, onChange, block }) {
  const ref = useRef(null);
  const last = useRef(null);
  useEffect(() => {
    if (ref.current && value !== last.current) { ref.current.innerHTML = value || ""; last.current = value; }
  }, [value]);
  const emit = () => { const clean = sanitize(ref.current.innerHTML, block); last.current = clean; onChange(clean); };
  const cmd = (e, name, arg) => { e.preventDefault(); ref.current.focus(); document.execCommand(name, false, arg); emit(); };
  const link = (e) => {
    e.preventDefault();
    const url = prompt("الرابط (مثال: /tours/luxor-hot-air-balloon/ أو https://…)");
    if (url) { ref.current.focus(); document.execCommand("createLink", false, url.trim()); emit(); }
  };
  const paste = (e) => { e.preventDefault(); document.execCommand("insertText", false, e.clipboardData.getData("text/plain")); };
  return html`<div class="rich ${block ? "block" : ""}">
    <div class="rich-tools">
      <button type="button" title="عريض" onMouseDown=${(e) => cmd(e, "bold")}><i class="fas fa-bold"></i></button>
      <button type="button" title="مائل" onMouseDown=${(e) => cmd(e, "italic")}><i class="fas fa-italic"></i></button>
      <button type="button" title="رابط" onMouseDown=${link}><i class="fas fa-link"></i></button>
      <button type="button" title="شيل الرابط" onMouseDown=${(e) => cmd(e, "unlink")}><i class="fas fa-link-slash"></i></button>
      ${block ? html`
        <button type="button" title="قائمة نقاط" onMouseDown=${(e) => cmd(e, "insertUnorderedList")}><i class="fas fa-list-ul"></i></button>
        <button type="button" title="عنوان فرعي" onMouseDown=${(e) => cmd(e, "formatBlock", "h3")}><i class="fas fa-heading"></i></button>
        <button type="button" title="فقرة عادية" onMouseDown=${(e) => cmd(e, "formatBlock", "p")}><i class="fas fa-paragraph"></i></button>` : null}
    </div>
    <div class="rich-body" ref=${ref} contentEditable="true" dir="ltr" onInput=${emit} onPaste=${paste}
      onKeyDown=${block ? undefined : (e) => { if (e.key === "Enter") e.preventDefault(); }}></div>
  </div>`;
}

function IconPicker({ value, onChange, label }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);
  useEffect(() => {
    if (!open) return;
    const close = (e) => { if (!ref.current?.contains(e.target)) setOpen(false); };
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, [open]);
  return html`<div class="field" style="flex:none">${label ? html`<span class="label">${label}</span>` : null}
    <div class="icon-pick" ref=${ref}>
      <button type="button" class="icon-btn" title="اختار أيقونة" aria-expanded=${open} onClick=${() => setOpen(!open)}><i class="fas ${value || "fa-circle"}"></i></button>
      ${open ? html`<div class="icon-menu">${ICONS.map((ic) => html`<button type="button" title=${ic.replace("fa-", "")} aria-pressed=${ic === value} onClick=${() => { onChange(ic); setOpen(false); }}><i class="fas ${ic}"></i></button>`)}</div>` : null}
    </div></div>`;
}

function Switch({ checked, onChange, label, hint }) {
  return html`<div class="field"><label class="switch"><input type="checkbox" checked=${checked} onChange=${(e) => onChange(e.target.checked)} /><span class="track"></span><span>${label}</span></label>${hint ? html`<div class="hint">${hint}</div>` : null}</div>`;
}

function Items({ items, onChange, make, addLabel, render: renderItem, title, compact }) {
  const list = items || [];
  const set = (i, v) => onChange(list.map((x, j) => (j === i ? v : x)));
  const move = (i, d) => {
    const j = i + d;
    if (j < 0 || j >= list.length) return;
    const c = list.slice();
    [c[i], c[j]] = [c[j], c[i]];
    onChange(c);
  };
  const tools = (i) => html`<div class="item-tools">
    <button type="button" class="btn ghost icon sm" title="لفوق" disabled=${i === 0} onClick=${() => move(i, -1)}><i class="fas fa-arrow-up"></i></button>
    <button type="button" class="btn ghost icon sm" title="لتحت" disabled=${i === list.length - 1} onClick=${() => move(i, 1)}><i class="fas fa-arrow-down"></i></button>
    <button type="button" class="btn ghost icon sm" title="حذف" onClick=${() => confirm("تحذف ده؟") && onChange(list.filter((_, j) => j !== i))}><i class="fas fa-trash-can"></i></button>
  </div>`;
  return html`<div class="items">
    ${list.map((it, i) => compact
      ? html`<div class="inline-item" key=${i}><span class="faint num" style="min-width:18px">${i + 1}</span>${renderItem(it, (v) => set(i, v), i)}${tools(i)}</div>`
      : html`<div class="item" key=${i}><div class="item-head"><span class="n num">${i + 1}</span><div class="grow">${title ? title(it, i) : null}</div>${tools(i)}</div>${renderItem(it, (v) => set(i, v), i)}</div>`)}
    <div><button type="button" class="btn sm" onClick=${() => onChange([...list, make(list)])}><i class="fas fa-plus"></i> ${addLabel}</button></div>
  </div>`;
}

function Group({ title, sub, children }) {
  return html`<section class="group"><h3>${title}${sub ? html` <span class="faint">${sub}</span>` : null}</h3>${children}</section>`;
}

// images
async function shrink(file, max = 2400) {
  if (!/^image\/(jpeg|png|webp)$/.test(file.type)) throw new Error("الصورة لازم تكون JPG أو PNG أو WEBP.");
  const bmp = await createImageBitmap(file);
  if (bmp.width <= max && file.size <= 6 * 1024 * 1024) return { blob: file, w: bmp.width, h: bmp.height };
  const scale = Math.min(1, max / bmp.width);
  const canvas = document.createElement("canvas");
  canvas.width = Math.round(bmp.width * scale);
  canvas.height = Math.round(bmp.height * scale);
  canvas.getContext("2d").drawImage(bmp, 0, 0, canvas.width, canvas.height);
  const blob = await new Promise((res) => canvas.toBlob(res, "image/jpeg", 0.9));
  return { blob, w: canvas.width, h: canvas.height };
}
async function uploadImage(file) {
  const { blob, w, h } = await shrink(file);
  const ext = { "image/png": "png", "image/webp": "webp" }[blob.type] || "jpg";
  const base = file.name.replace(/\.[^.]+$/, "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 50) || "photo";
  const path = `uploads/${new Date().toISOString().slice(0, 10)}/${base}-${Math.random().toString(36).slice(2, 8)}.${ext}`;
  const { error } = await sb.storage.from("site-images").upload(path, blob, { contentType: blob.type, upsert: false });
  if (error) throw error;
  return { src: sb.storage.from("site-images").getPublicUrl(path).data.publicUrl, width: String(w), height: String(h) };
}
function Upload({ onFiles, multiple, label }) {
  const [over, setOver] = useState(false);
  const [busy, setBusy] = useState(false);
  const id = useMemo(uid, []);
  async function handle(files) {
    if (!files?.length) return;
    setBusy(true);
    try {
      const out = [];
      for (const f of [...files].slice(0, multiple ? 12 : 1)) out.push(await uploadImage(f));
      onFiles(out);
      toast(out.length > 1 ? `اترفعت ${out.length} صور ✓` : "اترفعت الصورة ✓");
    } catch (e) {
      toast("ما اترفعتش: " + (e.message || e), true);
    }
    setBusy(false);
  }
  return html`<label for=${id} class="upload ${over ? "over" : ""}"
      onDragOver=${(e) => { e.preventDefault(); setOver(true); }} onDragLeave=${() => setOver(false)}
      onDrop=${(e) => { e.preventDefault(); setOver(false); handle(e.dataTransfer.files); }}>
    <input id=${id} type="file" accept="image/jpeg,image/png,image/webp" multiple=${multiple} hidden onChange=${(e) => { handle(e.target.files); e.target.value = ""; }} />
    ${busy ? html`<i class="fas fa-spinner spin"></i><span>جارٍ الرفع…</span>` : html`<i class="fas fa-cloud-arrow-up"></i><span>${label || "اسحب صورة هنا أو اضغط للاختيار"}</span><span class="faint">JPG أو PNG · هتتحول WebP تلقائياً</span>`}
  </label>`;
}

// ------------------------------------------------------------------------------------------------ trip editor
const TABS = [["basics", "الأساسي"], ["photos", "الصور"], ["overview", "نظرة عامة"], ["itinerary", "البرنامج"], ["inclusions", "يشمل / لا يشمل"], ["faq", "الأسئلة"], ["seo", "جوجل"], ["history", "السجل"]];

function TripEditor({ slug, tab }) {
  const [row, setRow] = useState(null);
  const [draft, setDraft] = useState(null);
  const [status, setStatus] = useState(null);
  const [err, setErr] = useState("");
  const [saving, setSaving] = useState(false);
  const [showProblems, setShowProblems] = useState(false);
  const load = useCallback(async () => {
    const { data, error } = await sb.from("products").select("*").eq("slug", slug).maybeSingle();
    if (error || !data) return setErr(error ? error.message : "الرحلة دي مش موجودة.");
    setRow(data); setDraft(clone(data.data)); setStatus(data.status);
  }, [slug]);
  useEffect(() => { load(); }, [load]);
  const dirty = !!row && (!same(draft, row.data) || status !== row.status);
  useEffect(() => { window.__cmsDirty = dirty; }, [dirty]);
  useEffect(() => () => { window.__cmsDirty = false; }, []);
  const problems = useMemo(() => (draft ? validate(draft) : []), [draft]);

  if (err) return html`<${TopBar} title="تعديل رحلة" /><div class="page"><div class="notice red"><span>${err}</span></div></div>`;
  if (!draft) return html`<${TopBar} title="تعديل رحلة" /><div class="page"><div class="card empty"><i class="fas fa-spinner spin"></i>جارٍ التحميل…</div></div>`;

  const up = (path) => (value) => setDraft((d) => setIn(d, path, value));
  const b = draft.blocks || {};
  async function save() {
    if (problems.length) { setShowProblems(true); return toast("في حاجات ناقصة قبل الحفظ", true); }
    setSaving(true);
    const data = derive(draft);
    const { data: saved, error } = await sb.from("products").update({ data, status }).eq("slug", slug).eq("updated_at", row.updated_at).select("*");
    setSaving(false);
    if (error) return toast("ما اتحفظش: " + error.message, true);
    if (!saved.length) {
      const { data: latest } = await sb.from("products").select("*").eq("slug", slug).single();
      if (latest) setRow(latest);
      return toast("حد تاني عدّل الرحلة دي في نفس الوقت. تعديلاتك لسه هنا: راجعها واحفظ تاني.", true);
    }
    setRow(saved[0]); setDraft(clone(saved[0].data)); setStatus(saved[0].status); setShowProblems(false);
    window.__cmsDirty = false;
    dispatchEvent(new Event("cms:changed"));
    toast("اتحفظ ✓ هيظهر على الموقع بعد ما تضغط «نشر»");
  }
  const [stateLabel, stateTone] = tripState({ ...row, status });
  const name = plain(draft.card?.name) || slug;
  const pageUrl = `https://avicontravel.com/${slug}/`;
  const ctx = { draft, b, up, row, status, setStatus, setDraft, reload: load };
  const body = {
    basics: Basics, photos: Photos, overview: Overview, itinerary: Itinerary, inclusions: Inclusions, faq: Faq, seo: Seo, history: History,
  }[tab] || Basics;

  return html`<${TopBar} title=${name} sub=${SECTIONS[row.section]}>
      ${row.live_status === "published" ? html`<a class="btn ghost" href=${pageUrl} target="_blank" rel="noopener"><i class="fas fa-arrow-up-right-from-square"></i> الصفحة على الموقع</a>` : null}
    <//>
    <div class="page">
      <div class="ed-head">
        <a class="btn ghost sm" href="#/trips" onClick=${guardLink}><i class="fas fa-arrow-right"></i> كل الرحلات</a>
        <div class="grow"></div>
        <${Pill} label=${stateLabel} tone=${stateTone} />
        ${row.published_at ? html`<span class="faint">آخر نشر ${ago(row.published_at)}</span>` : null}
      </div>
      <div class="tabs" role="tablist">
        ${TABS.map(([k, v]) => html`<button role="tab" aria-selected=${tab === k} onClick=${() => { location.hash = `#/trips/${slug}/${k}`; }}>${v}</button>`)}
      </div>
      <div class="stack"><${body} ...${ctx} /></div>
    </div>
    ${dirty ? html`<div class="savebar" role="region" aria-label="حفظ">
      <i class="fas fa-pen"></i><span class="grow">في تعديلات مش محفوظة${showProblems && problems.length ? html`<ul class="problems">${problems.map((p) => html`<li>${p}</li>`)}</ul>` : null}</span>
      <button class="btn ghost sm" onClick=${() => { if (confirm("ترجع لآخر نسخة محفوظة؟")) { setDraft(clone(row.data)); setStatus(row.status); setShowProblems(false); } }}>تراجع</button>
      <button class="btn primary" disabled=${saving} onClick=${save}>${saving ? html`<i class="fas fa-spinner spin"></i>` : html`<i class="fas fa-floppy-disk"></i>`} حفظ</button>
    </div>` : null}`;
}

function Basics({ draft, b, up, status, setStatus, row }) {
  const price = b.price;
  const onRequest = price && amountOf(price) == null;
  const setPriceMode = (req) => up(["blocks", "price"])(req
    ? { ...price, currency: "", amount: "On Request", per: "", style: "font-size:30px", note: "Exact price depends on dates &amp; group size" }
    : { ...price, currency: "$", amount: "", per: "/person", style: "", note: "Starting price per person" });
  return html`
    <${Group} title="الاسم والظهور">
      <div class="grid2">
        <${Field} label="اسم الرحلة" hint="بيظهر في الكروت ونموذج الحجز والإيميل اللي بيوصلك." value=${draft.card?.name} onChange=${up(["card", "name"])} />
        ${b.title != null ? html`<${Field} label="العنوان الكبير أعلى الصفحة" value=${b.title} onChange=${up(["blocks", "title"])} />` : null}
      </div>
      <div class="grid2">
        <${Switch} checked=${status === "published"} onChange=${(v) => setStatus(v ? "published" : "hidden")} label="ظاهرة على الموقع"
          hint=${status === "published" ? "بعد النشر هتبقى في القوائم ونتائج البحث." : row.live_status === "published" ? "بعد النشر الصفحة هتتحول لصفحة القسم وتختفي من كل القوائم (وتقدر ترجّعها بعدين)." : "مش هتظهر لحد ما تفعّلها وتنشر."} />
        <${Switch} checked=${!!draft.card?.home} onChange=${up(["card", "home"])} label="تظهر في الصفحة الرئيسية" />
      </div>
    <//>
    ${price ? html`<${Group} title="السعر" sub="(السعر في صندوق الحجز، ومنه بيتحدث الكارت وجوجل ومربع Price)">
      <div class="seg"><button aria-pressed=${!onRequest} onClick=${() => onRequest && setPriceMode(false)}>سعر محدد</button><button aria-pressed=${onRequest} onClick=${() => !onRequest && setPriceMode(true)}>عند الطلب</button></div>
      <div class="grid3">
        ${!onRequest ? html`<${Field} label="يبدأ من (بالدولار للفرد)" placeholder="95" value=${price.amount} onChange=${(v) => up(["blocks", "price", "amount"])(v.replace(/[^\d,]/g, ""))} />` : null}
        <${Field} label="العنوان فوق السعر" value=${price.label} onChange=${up(["blocks", "price", "label"])} />
        <${Field} label="السطر تحت السعر" value=${price.note} onChange=${up(["blocks", "price", "note"])} />
      </div>
      ${b.pricing ? html`<div class="notice"><i class="fas fa-circle-info"></i><span>لو غيرت السعر، راجع كمان «جدول الأسعار» في تبويب نظرة عامة.</span></div>` : null}
    <//>` : null}
    <${Group} title="الكارت" sub="(في الصفحة الرئيسية وصفحة القسم والرحلات المشابهة)">
      <div class="grid3">
        <${Field} label="المكان" placeholder="Luxor" value=${draft.card?.location} onChange=${up(["card", "location"])} />
        <${Field} label="المدة" placeholder="2.5 To 4 Hours" value=${draft.card?.duration} onChange=${up(["card", "duration"])} />
        <${Field} label="النوع" placeholder="Balloon Ride" value=${draft.card?.style} onChange=${up(["card", "style"])} />
      </div>
      <div class="grid2">
        <${Field} label="الشارة على الصورة" placeholder="Adventure Tour" value=${draft.card?.badge} onChange=${up(["card", "badge"])} />
      </div>
      <${Field} label="وصف قصير" long value=${draft.card?.summary} onChange=${up(["card", "summary"])} hint="جملة أو اتنين." />
    <//>
    ${b.badge || b.chips ? html`<${Group} title="أعلى الصفحة">
      ${b.badge ? html`<div class="row"><${IconPicker} label="أيقونة" value=${b.badge.icon} onChange=${up(["blocks", "badge", "icon"])} /><${Field} label="الشارة" value=${b.badge.text} onChange=${up(["blocks", "badge", "text"])} /></div>` : null}
      ${b.chips ? html`<div class="field"><span class="label">المعلومات السريعة</span>
        <${Items} compact items=${b.chips} onChange=${up(["blocks", "chips"])} addLabel="إضافة معلومة"
          make=${(l) => ({ icon: "fa-star", label: l[0]?.label ? "Info" : "", text: "" })}
          render=${(c, set) => html`<${IconPicker} value=${c.icon} onChange=${(v) => set({ ...c, icon: v })} />
            ${c.label ? html`<${Field} value=${c.label} onChange=${(v) => set({ ...c, label: v })} />` : null}
            <${Field} value=${c.text} onChange=${(v) => set({ ...c, text: v })} />`} /></div>` : null}
    <//>` : null}`;
}

function ImageCard({ img, onChange, onRemove, badge, extra }) {
  return html`<div class="shot">
    <div class="pic">${img.src ? html`<img src=${img.src} alt="" loading="lazy" />` : null}${badge ? html`<${Pill} label=${badge} tone="blue" />` : null}</div>
    <div class="pad">
      <${Field} value=${img.alt} attr onChange=${(v) => onChange({ ...img, alt: v })} placeholder="وصف الصورة بالإنجليزي" />
      <div class="row" style="gap:4px">${extra}${onRemove ? html`<button type="button" class="btn ghost icon sm" title="حذف الصورة" onClick=${() => confirm("تحذف الصورة؟") && onRemove()}><i class="fas fa-trash-can"></i></button>` : null}</div>
    </div>
  </div>`;
}

function Photos({ draft, b, up }) {
  const gal = b.gallery;
  const setGal = up(["blocks", "gallery"]);
  const move = (i, d) => { const c = gal.slice(); [c[i], c[i + d]] = [c[i + d], c[i]]; setGal(c); };
  const cardImg = draft.card?.image;
  return html`
    ${gal ? html`<${Group} title="صور أعلى الصفحة" sub="(الأولى هي الكبيرة)">
      <div class="gallery">
        ${gal.map((img, i) => html`<${ImageCard} key=${i + img.src} img=${img} badge=${i === 0 ? "الرئيسية" : ""}
          onChange=${(v) => setGal(gal.map((x, j) => (j === i ? v : x)))} onRemove=${gal.length > 1 ? () => setGal(gal.filter((_, j) => j !== i)) : null}
          extra=${html`
            <button type="button" class="btn ghost icon sm" title="قبل" disabled=${i === 0} onClick=${() => move(i, -1)}><i class="fas fa-arrow-right"></i></button>
            <button type="button" class="btn ghost icon sm" title="بعد" disabled=${i === gal.length - 1} onClick=${() => move(i, 1)}><i class="fas fa-arrow-left"></i></button>
            <button type="button" class="btn ghost sm" title="استخدمها في الكارت" onClick=${() => { up(["card", "image"])({ ...img }); toast("بقت صورة الكارت ✓"); }}><i class="fas fa-id-card"></i></button>`} />`)}
        <${Upload} multiple onFiles=${(imgs) => setGal([...gal, ...imgs.map((x) => ({ ...x, alt: "" }))])} label="أضف صور" />
      </div>
    <//>` : null}
    ${b.hero_image ? html`<${Group} title="صورة الغلاف">
      <div class="gallery"><${ImageCard} img=${b.hero_image} onChange=${up(["blocks", "hero_image"])} />
        <${Upload} onFiles=${([x]) => up(["blocks", "hero_image"])({ ...b.hero_image, ...x })} label="غيّر صورة الغلاف" /></div>
    <//>` : null}
    <${Group} title="صورة الكارت" sub="(في القوائم والرئيسية)">
      <div class="gallery">
        ${cardImg ? html`<${ImageCard} img=${cardImg} onChange=${up(["card", "image"])} />` : null}
        <${Upload} onFiles=${([x]) => up(["card", "image"])({ alt: plain(draft.card?.name), ...(cardImg || {}), ...x })} label="غيّر صورة الكارت" />
      </div>
    <//>`;
}

function Overview({ b, up }) {
  const extraLabels = { Pickup: "مكان الاستلام", Included: "المشمول", "Best Time": "أفضل وقت" };
  return html`
    ${b.overview ? html`<${Group} title="النبذة">
      <${Field} label="العنوان" value=${b.overview.heading} onChange=${up(["blocks", "overview", "heading"])} />
      <div class="field"><span class="label">الفقرات</span>
        <${Items} items=${b.overview.paragraphs} onChange=${up(["blocks", "overview", "paragraphs"])} addLabel="إضافة فقرة" make=${() => ""}
          render=${(p, set) => html`<${Rich} value=${p} onChange=${set} />`} /></div>
    <//>` : null}
    ${b.facts ? html`<${Group} title="مربعات المعلومات">
      <${Items} compact items=${b.facts.cards} onChange=${up(["blocks", "facts", "cards"])} addLabel="إضافة مربع" make=${() => ({ icon: "fa-star", label: "", value: "" })}
        render=${(c, set) => html`<${IconPicker} value=${c.icon} onChange=${(v) => set({ ...c, icon: v })} />
          <${Field} placeholder="Duration" value=${c.label} onChange=${(v) => set({ ...c, label: v })} />
          <${Field} placeholder="2.5 To 4 Hours" value=${c.value} onChange=${(v) => set({ ...c, value: v })} />`} />
      ${b.facts.extra && Object.keys(b.facts.extra).length ? html`<div class="grid3">
        ${Object.keys(extraLabels).filter((k) => k in b.facts.extra).map((k) => html`<${Field} label=${extraLabels[k]} value=${b.facts.extra[k]} onChange=${up(["blocks", "facts", "extra", k])} />`)}
      </div>${"Price" in b.facts.extra ? html`<div class="faint">مربع «Price» بيتحدث لوحده من السعر.</div>` : null}` : null}
    <//>` : null}
    ${b.highlights ? html`<${Group} title="أبرز المميزات">
      <${Field} label="العنوان" value=${b.highlights.heading} onChange=${up(["blocks", "highlights", "heading"])} />
      ${b.highlights.cards?.length
        ? html`<${Items} compact items=${b.highlights.cards} onChange=${up(["blocks", "highlights", "cards"])} addLabel="إضافة ميزة" make=${() => ({ icon: "fa-star", label: "", value: "" })}
            render=${(c, set) => html`<${IconPicker} value=${c.icon} onChange=${(v) => set({ ...c, icon: v })} /><${Field} value=${c.label} onChange=${(v) => set({ ...c, label: v })} /><${Field} value=${c.value} onChange=${(v) => set({ ...c, value: v })} />`} />`
        : html`<${Items} compact items=${b.highlights.items} onChange=${up(["blocks", "highlights", "items"])} addLabel="إضافة ميزة" make=${() => ""}
            render=${(x, set) => html`<${Field} value=${x} onChange=${set} />`} />`}
    <//>` : null}
    ${b.route ? html`<${Group} title="خط السير">
      <${Field} label="العنوان" value=${b.route.heading} onChange=${up(["blocks", "route", "heading"])} />
      <${Items} items=${b.route.stops} addLabel="إضافة محطة"
        onChange=${(stops) => {
          const con = (b.route.connectors || []).slice(0, Math.max(0, stops.length - 1));
          while (con.length < stops.length - 1) con.push(con[con.length - 1] || "fa-arrow-right");
          up(["blocks", "route"])({ ...b.route, stops, connectors: con });
        }}
        make=${() => ({ icon: "fa-map-marker-alt", name: "", label: "" })}
        title=${(s) => html`<span class="ltr">${plain(s.name)}</span>`}
        render=${(s, set, i) => html`<div class="row">
          ${i > 0 ? html`<${IconPicker} label="الانتقال" value=${b.route.connectors?.[i - 1]} onChange=${(v) => up(["blocks", "route", "connectors", i - 1])(v)} />` : null}
          <${IconPicker} label="أيقونة" value=${s.icon} onChange=${(v) => set({ ...s, icon: v })} />
          <${Field} label="المحطة" value=${s.name} onChange=${(v) => set({ ...s, name: v })} />
          <${Field} label="تحتها" placeholder="Start" value=${s.label} onChange=${(v) => set({ ...s, label: v })} />
        </div>`} />
    <//>` : null}
    ${b.pricing ? html`<${Pricing} p=${b.pricing} set=${up(["blocks", "pricing"])} />` : null}
    ${b.longform != null ? html`<${Group} title="الدليل التفصيلي" sub="(النص الطويل آخر النظرة العامة)">
      <${Rich} block value=${b.longform} onChange=${up(["blocks", "longform"])} />
    <//>` : null}`;
}

function Pricing({ p, set }) {
  if (p.kind === "table") {
    return html`<${Group} title="جدول الأسعار">
      <${Field} label="العنوان" value=${p.title} onChange=${(v) => set({ ...p, title: v })} />
      <div class="table-wrap"><table class="table-edit"><tbody>
        <tr>${p.columns.map((c, i) => html`<td><input aria-label="عنوان العمود" value=${decode(c)} onInput=${(e) => set({ ...p, columns: p.columns.map((x, j) => (j === i ? encode(e.target.value) : x)) })} /></td>`)}<td></td></tr>
        ${p.rows.map((r, ri) => html`<tr>${r.map((c, ci) => html`<td><input value=${decode(c)} onInput=${(e) => set({ ...p, rows: p.rows.map((row, j) => (j === ri ? row.map((x, k) => (k === ci ? encode(e.target.value) : x)) : row)) })} /></td>`)}
          <td><button type="button" class="btn ghost icon sm" title="حذف الصف" onClick=${() => set({ ...p, rows: p.rows.filter((_, j) => j !== ri) })}><i class="fas fa-trash-can"></i></button></td></tr>`)}
      </tbody></table></div>
      <div><button type="button" class="btn sm" onClick=${() => set({ ...p, rows: [...p.rows, p.columns.map(() => "")] })}><i class="fas fa-plus"></i> إضافة صف</button></div>
    <//>`;
  }
  return html`<${Group} title="جدول الأسعار" sub="(المواسم والأسعار حسب عدد الأفراد)">
    <${Field} label="العنوان" value=${p.title} onChange=${(v) => set({ ...p, title: v })} />
    <${Items} items=${p.seasons} onChange=${(seasons) => set({ ...p, seasons })} addLabel="إضافة موسم"
      make=${(l) => ({ icon: l[l.length - 1]?.icon || "fa-calendar-alt", label: "", rows: (l[l.length - 1]?.rows || [["Solo", ""]]).map(([k]) => [k, ""]) })}
      title=${(s) => html`<span class="ltr">${plain(s.label)}</span>`}
      render=${(s, setS) => html`<div class="row"><${IconPicker} label="أيقونة" value=${s.icon} onChange=${(v) => setS({ ...s, icon: v })} /><${Field} label="الموسم" value=${s.label} onChange=${(v) => setS({ ...s, label: v })} /></div>
        <table class="table-edit"><tbody>${s.rows.map(([k, v], ri) => html`<tr>
          <td><input aria-label="الفئة" value=${decode(k)} onInput=${(e) => setS({ ...s, rows: s.rows.map((r, j) => (j === ri ? [encode(e.target.value), r[1]] : r)) })} /></td>
          <td><input aria-label="السعر" value=${decode(v)} onInput=${(e) => setS({ ...s, rows: s.rows.map((r, j) => (j === ri ? [r[0], encode(e.target.value)] : r)) })} /></td>
          <td style="width:40px"><button type="button" class="btn ghost icon sm" title="حذف" onClick=${() => setS({ ...s, rows: s.rows.filter((_, j) => j !== ri) })}><i class="fas fa-trash-can"></i></button></td>
        </tr>`)}</tbody></table>
        <div><button type="button" class="btn sm" onClick=${() => setS({ ...s, rows: [...s.rows, ["", ""]] })}><i class="fas fa-plus"></i> إضافة سعر</button></div>`} />
  <//>`;
}

function Itinerary({ b, up }) {
  const it = b.itinerary;
  if (!it) return html`<div class="card empty">الصفحة دي مفيهاش برنامج.</div>`;
  const word = /^step/i.test(it.days[0]?.label || "") ? "Step" : "Day";
  return html`<${Group} title="البرنامج">
    <div class="grid2"><${Field} label="العنوان" value=${it.heading} onChange=${up(["blocks", "itinerary", "heading"])} /><${Field} label="سطر تحت العنوان" value=${it.intro} onChange=${up(["blocks", "itinerary", "intro"])} /></div>
    <${Items} items=${it.days} onChange=${up(["blocks", "itinerary", "days"])} addLabel=${word === "Step" ? "إضافة خطوة" : "إضافة يوم"}
      make=${(l) => ({ label: it.days[0]?.label ? `${word} ${l.length + 1}` : "", title: "", html: "<p></p>" })}
      title=${(d) => html`<span class="ltr">${plain(d.label)} ${plain(d.title)}</span>`}
      render=${(d, set) => html`<div class="grid2"><${Field} label="الرقم" value=${d.label} onChange=${(v) => set({ ...d, label: v })} /><${Field} label="العنوان" value=${d.title} onChange=${(v) => set({ ...d, title: v })} /></div>
        <${Rich} block value=${d.html} onChange=${(v) => set({ ...d, html: v })} />`} />
  <//>`;
}

function Inclusions({ b, up }) {
  const list = (key, title) => b[key] ? html`<${Group} title=${title}>
    <${Items} compact items=${b[key]} onChange=${up(["blocks", key])} addLabel="إضافة" make=${() => ""} render=${(x, set) => html`<${Field} value=${x} onChange=${set} />`} />
  <//>` : null;
  return html`${list("included", "يشمل")}${list("excluded", "لا يشمل")}`;
}

function Faq({ b, up }) {
  const f = b.faq;
  if (!f) return html`<div class="card empty">الصفحة دي مفيهاش أسئلة.</div>`;
  return html`<${Group} title="الأسئلة الشائعة" sub="(بتظهر في جوجل كمان)">
    <div class="grid2"><${Field} label="العنوان" value=${f.heading} onChange=${up(["blocks", "faq", "heading"])} /><${Field} label="سطر تحت العنوان" value=${f.intro} onChange=${up(["blocks", "faq", "intro"])} /></div>
    <${Items} items=${f.items} onChange=${up(["blocks", "faq", "items"])} addLabel="إضافة سؤال" make=${() => ({ q: "", a: "<p></p>" })}
      title=${(x) => html`<span class="ltr">${plain(x.q)}</span>`}
      render=${(x, set) => html`<${Field} label="السؤال" value=${x.q} onChange=${(v) => set({ ...x, q: v })} /><div class="field"><span class="label">الإجابة</span><${Rich} block value=${x.a} onChange=${(v) => set({ ...x, a: v })} /></div>`} />
  <//>`;
}

function Seo({ draft, b, up, row }) {
  const n = amountOf(b.price);
  const price = n == null ? "" : "$" + n.toLocaleString("en-US");
  const seo = draft.seo || { title: "", description: "" };
  const t = seo.title.replace("{price}", price), d = seo.description.replace("{price}", price);
  const insert = (key) => up(["seo", key])((seo[key] || "") + (seo[key]?.includes("{price}") ? "" : " {price}"));
  const counter = (len, ok, rule) => html`<span class="counter ${ok ? "" : "bad"}">${len} حرف · ${rule}</span>`;
  return html`<${Group} title="الظهور في جوجل">
    <div class="notice"><i class="fas fa-circle-info"></i><span>اكتب بالإنجليزي. <b class="ltr">{price}</b> بيتحط مكانه السعر الحالي تلقائياً، فلو غيرت السعر العنوان يتحدث لوحده.</span></div>
    <div class="field"><label for="st">العنوان</label>
      <input id="st" type="text" class="en" value=${seo.title} onInput=${(e) => up(["seo", "title"])(e.target.value)} />
      <div class="row" style="justify-content:space-between;align-items:center">${counter(t.length, t.length > 0 && t.length <= 60, "الحد 60")}${n != null ? html`<button type="button" class="btn ghost sm" onClick=${() => insert("title")}>أضف {price}</button>` : null}</div></div>
    <div class="field"><label for="sd">الوصف</label>
      <textarea id="sd" class="en" value=${seo.description} onInput=${(e) => up(["seo", "description"])(e.target.value)}></textarea>
      <div class="row" style="justify-content:space-between;align-items:center">${counter(d.length, d.length >= 120 && d.length <= 160, "من 120 لـ 160")}${n != null ? html`<button type="button" class="btn ghost sm" onClick=${() => insert("description")}>أضف {price}</button>` : null}</div></div>
    <div class="field"><span class="label">شكلها في جوجل تقريباً</span>
      <div class="gpreview"><div class="u">avicontravel.com › ${row.slug.replace("/", " › ")}</div><div class="h">${t || "Title"}</div><div class="d">${d || "Description"}</div></div></div>
  <//>`;
}

function History({ row, setDraft, setStatus, reload }) {
  const [revs, setRevs] = useState(null);
  const [team, setTeam] = useState({});
  useEffect(() => {
    sb.from("product_revisions").select("id,created_at,created_by,status,data").eq("slug", row.slug).order("created_at", { ascending: false }).limit(30).then(({ data }) => setRevs(data || []));
    sb.from("admins").select("user_id,name,email").then(({ data }) => setTeam(Object.fromEntries((data || []).map((a) => [a.user_id, a.name || a.email]))));
  }, [row.slug, row.updated_at]);
  const restore = (data, st, label) => { setDraft(clone(data)); if (st) setStatus(st); toast(`اتفتحت ${label}. راجعها واضغط «حفظ» لو تمام.`); };
  async function remove() {
    if (!confirm("تحذف الرحلة دي نهائياً من لوحة التحكم؟ (مش منشورة على الموقع)")) return;
    const { error } = await sb.from("products").delete().eq("slug", row.slug);
    if (error) return toast("ما اتحذفتش: " + error.message, true);
    window.__cmsDirty = false;
    dispatchEvent(new Event("cms:changed"));
    location.hash = "#/trips";
  }
  return html`
    ${row.live_data && row.has_changes ? html`<${Group} title="النسخة المنشورة">
      <p class="muted" style="margin:0">عايز تلغي كل التعديلات اللي لسه ما اتنشرتش وترجع للي على الموقع؟</p>
      <div><button class="btn" onClick=${() => restore(row.live_data, row.live_status, "النسخة المنشورة")}><i class="fas fa-rotate-left"></i> افتح النسخة المنشورة</button></div>
    <//>` : null}
    <${Group} title="النسخ السابقة" sub="(كل حفظ بيحتفظ بالنسخة اللي قبله)">
      ${revs === null ? html`<div class="faint">جارٍ التحميل…</div>` : !revs.length ? html`<div class="faint">لسه مفيش نسخ سابقة.</div>` : html`<div class="table-wrap"><table class="jobs"><thead><tr><th>قبل تعديل</th><th>بواسطة</th><th></th></tr></thead><tbody>
        ${revs.map((r) => html`<tr><td>${fmtDate(r.created_at)}</td><td>${r.created_by ? team[r.created_by] || "عضو في الفريق" : "تحديث من الموقع"}</td>
          <td><button class="btn sm" onClick=${() => restore(r.data, r.status, "نسخة " + fmtDate(r.created_at))}>افتح النسخة دي</button></td></tr>`)}
      </tbody></table></div>`}
    <//>
    ${!row.live_status ? html`<${Group} title="حذف الرحلة"><p class="muted" style="margin:0">الرحلة دي عمرها ما اتنشرت، فينفع تتحذف.</p><div><button class="btn danger" onClick=${remove}><i class="fas fa-trash-can"></i> حذف الرحلة</button></div><//>` : null}`;
}

// ------------------------------------------------------------------------------------------------ publish
function Publish() {
  const [pending, setPending] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [busy, setBusy] = useState(false);
  const load = useCallback(async () => {
    const [p, j] = await Promise.all([
      sb.from("products").select("slug,section,status,live_status,data,live_data,updated_at,sort_order").eq("has_changes", true).order("sort_order"),
      sb.from("publish_jobs").select("*").order("id", { ascending: false }).limit(10),
    ]);
    setPending(p.data || []);
    setJobs((old) => {
      const next = j.data || [];
      if (old.some((o) => ["queued", "running", "deploying"].includes(o.status) && next.find((x) => x.id === o.id && ["success", "failed"].includes(x.status)))) {
        dispatchEvent(new Event("cms:changed"));
      }
      return next;
    });
  }, []);
  useEffect(() => { load(); }, [load]);
  const active = jobs.find((j) => ["queued", "running", "deploying"].includes(j.status) && Date.now() - new Date(j.requested_at) < 30 * 60e3);
  useEffect(() => { if (!active) return; const t = setInterval(load, 5000); return () => clearInterval(t); }, [active?.id, active?.status]);
  const invalid = (pending || []).map((r) => [r, r.status === "published" ? validate(r.data) : []]).filter(([, p]) => p.length);

  async function publish() {
    setBusy(true);
    const { data, error } = await sb.functions.invoke("publish-site", { body: {} });
    setBusy(false);
    if (error) {
      let msg = error.message;
      try { msg = (await error.context.json()).error || msg; } catch { /* not JSON */ }
      toast(msg, true);
    } else {
      toast(data?.already_running ? "في نشر شغال دلوقتي، تابعه هنا." : "بدأ النشر ✓ بياخد حوالي 3 دقايق.");
    }
    load();
  }
  const latest = active || jobs[0];
  return html`<${TopBar} title="النشر على الموقع" sub="التعديلات المحفوظة بتفضل مسودة لحد ما تنشرها هنا." />
    <div class="page stack">
      ${latest ? html`<${JobProgress} job=${latest} />` : null}
      <${Group} title="مستني النشر" sub=${pending ? `(${pending.length})` : ""}>
        ${pending === null ? html`<div class="faint">جارٍ التحميل…</div>` : !pending.length ? html`<div class="empty" style="padding:24px"><i class="fas fa-circle-check"></i>كل حاجة منشورة. مفيش تعديلات مستنية.</div>` : html`
          <div class="changes">${pending.map((r) => html`<a class="card change" href=${"#/trips/" + r.slug} style="text-decoration:none;color:inherit">
            ${tripImage(r.data.card, r.data.blocks) ? html`<img src=${tripImage(r.data.card, r.data.blocks)} alt="" />` : html`<span></span>`}
            <div><b class="ltr">${plain(r.data.card?.name)}</b><div class="what">${changedParts(r).join(" · ")}</div></div>
            <${Pill} label=${tripState({ ...r, has_changes: true })[0]} tone="amber" />
          </a>`)}</div>`}
        ${invalid.length ? html`<div class="notice red"><i class="fas fa-triangle-exclamation"></i><div>لازم تتصلح قبل النشر:<ul class="problems">${invalid.map(([r, p]) => html`<li><a href=${"#/trips/" + r.slug}>${plain(r.data.card?.name)}</a>: ${p.join(" ")}</li>`)}</ul></div></div>` : null}
        <div class="row" style="align-items:center">
          <button class="btn primary" disabled=${busy || !!active || !pending?.length || invalid.length > 0} onClick=${publish}>
            ${busy ? html`<i class="fas fa-spinner spin"></i>` : html`<i class="fas fa-cloud-arrow-up"></i>`} انشر التعديلات على الموقع</button>
          <span class="faint">بيحدّث صفحات الرحلات والكروت والبحث وخريطة الموقع وجوجل مرة واحدة.</span>
        </div>
      <//>
      <${Group} title="آخر عمليات النشر">
        ${!jobs.length ? html`<div class="faint">لسه مفيش.</div>` : html`<div class="table-wrap"><table class="jobs"><thead><tr><th>الوقت</th><th>الحالة</th><th>الرحلات</th><th>تفاصيل</th></tr></thead><tbody>
          ${jobs.map((j) => html`<tr><td>${fmtDate(j.requested_at)}</td><td><${Pill} label=${JOB_STATUS[j.status]?.[0] || j.status} tone=${JOB_STATUS[j.status]?.[1]} /></td>
            <td class="num">${j.changed ? j.changed.length : "—"}</td>
            <td>${j.message ? html`<div>${j.message}</div>` : null}${j.run_url ? html`<a class="faint" href=${j.run_url} target="_blank" rel="noopener">تفاصيل تقنية</a>` : null}</td></tr>`)}
        </tbody></table></div>`}
      <//>
    </div>`;
}

function JobProgress({ job }) {
  const order = ["queued", "running", "deploying", "success"];
  const at = job.status === "failed" ? -1 : order.indexOf(job.status);
  const labels = ["الطلب وصل", "تجهيز الصفحات", "الرفع على الموقع", "تم"];
  const failedStep = job.status === "failed" ? (job.commit_sha ? 2 : job.run_url ? 1 : 0) : -1;
  return html`<section class="group">
    <h3>${job.status === "success" ? "آخر نشر تم بنجاح" : job.status === "failed" ? "آخر نشر ماكملش" : "النشر شغال دلوقتي"} <span class="faint">${ago(job.requested_at)}</span></h3>
    <div class="steps">${labels.map((l, i) => {
      const cls = failedStep >= 0 ? (i < failedStep ? "done" : i === failedStep ? "fail" : "") : i < at || job.status === "success" ? "done" : i === at ? "now" : "";
      const icon = cls === "done" ? html`<i class="fas fa-check"></i>` : cls === "fail" ? html`<i class="fas fa-xmark"></i>` : cls === "now" ? html`<i class="fas fa-spinner spin"></i>` : i + 1;
      return html`<div class="step ${cls}"><span class="dot">${icon}</span>${l}</div>`;
    })}</div>
    ${job.message ? html`<div class="notice ${job.status === "failed" ? "red" : ""}"><span>${job.message}</span></div>` : null}
    ${job.status === "success" && job.changed?.length ? html`<div class="faint">اتحدث: <span class="ltr">${job.changed.join(", ")}</span>. ممكن الصفحات تاخد دقيقة لحد ما تظهر.</div>` : null}
  </section>`;
}

render(html`<${App} />`, document.getElementById("app"));
