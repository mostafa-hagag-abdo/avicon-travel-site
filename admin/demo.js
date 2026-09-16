// Local demo of the control panel without Supabase: http://127.0.0.1:8099/admin/?demo
// Loads admin/demo-data.json (not committed: python _dev/cms/sync.py export --out admin/demo-data.json) and keeps
// every change in memory. Only used on localhost (see app.js).

const wait = (ms) => new Promise((r) => setTimeout(r, ms));
const clone = (o) => (o == null ? o : JSON.parse(JSON.stringify(o)));
function same(a, b) { return JSON.stringify(sortKeys(a)) === JSON.stringify(sortKeys(b)); }
function sortKeys(o) {
  if (Array.isArray(o)) return o.map(sortKeys);
  if (o && typeof o === "object") return Object.fromEntries(Object.keys(o).sort().map((k) => [k, sortKeys(o[k])]));
  return o;
}

function hasChanges(r) {
  if (r.status === "hidden" && (r.live_status || "hidden") === "hidden") return false;
  return r.status !== (r.live_status || "hidden") || !r.live_data || !same(r.data, r.live_data);
}

function pick(row, cols) {
  if (!cols || cols.trim() === "*") return clone(row);
  const out = {};
  for (const part of cols.split(",").map((s) => s.trim()).filter(Boolean)) {
    const [alias, path] = part.includes(":") ? part.split(":") : [null, part];
    const keys = path.split("->");
    let v = row;
    for (const k of keys) v = v == null ? v : v[k];
    out[alias || keys[keys.length - 1]] = clone(v);
  }
  return out;
}

class Query {
  constructor(db, table) {
    Object.assign(this, { db, table, op: "select", cols: "*", filters: [], sorts: [], lim: null, rng: null, one: false, maybe: false, payload: null, head: false, count: null, returning: false });
  }
  select(cols = "*", opts = {}) {
    if (this.op === "select") { this.cols = cols; this.head = !!opts.head; this.count = opts.count || null; } else { this.returning = true; this.cols = cols; }
    return this;
  }
  insert(rows) { this.op = "insert"; this.payload = rows; return this; }
  update(v) { this.op = "update"; this.payload = v; return this; }
  delete() { this.op = "delete"; return this; }
  eq(c, v) { this.filters.push((r) => String(r[c]) === String(v)); return this; }
  in(c, list) { this.filters.push((r) => list.map(String).includes(String(r[c]))); return this; }
  gt(c, v) { this.filters.push((r) => r[c] > v); return this; }
  or(expr) {
    const parts = expr.split(",").map((p) => p.split("."));
    this.filters.push((r) => parts.some(([col, , pat]) => String(r[col] ?? "").toLowerCase().includes(pat.replace(/[*%]/g, "").toLowerCase())));
    return this;
  }
  order(c, { ascending = true } = {}) { c.split(",").forEach((col) => this.sorts.push([col.trim(), ascending])); return this; }
  limit(n) { this.lim = n; return this; }
  range(a, b) { this.rng = [a, b]; return this; }
  single() { this.one = true; return this; }
  maybeSingle() { this.one = true; this.maybe = true; return this; }
  then(ok, fail) { return this.run().then(ok, fail); }

  async run() {
    await wait(120);
    const db = this.db, table = db.tables[this.table];
    if (!table) return { data: null, error: { message: `unknown table ${this.table}` } };
    const match = () => table.filter((r) => this.filters.every((f) => f(db.view(this.table, r))));
    if (this.op === "insert") {
      const rows = (Array.isArray(this.payload) ? this.payload : [this.payload]).map((r) => db.defaults(this.table, clone(r)));
      if (this.table === "products" && rows.some((r) => table.some((x) => x.slug === r.slug))) return { data: null, error: { message: "duplicate key value violates unique constraint" } };
      table.push(...rows);
      return { data: this.returning ? rows.map((r) => pick(db.view(this.table, r), this.cols)) : null, error: null };
    }
    if (this.op === "update") {
      const rows = match();
      for (const r of rows) db.update(this.table, r, clone(this.payload));
      return { data: rows.map((r) => pick(db.view(this.table, r), this.cols)), error: null, ...(this.one ? { data: rows[0] ? pick(db.view(this.table, rows[0]), this.cols) : null } : {}) };
    }
    if (this.op === "delete") {
      const rows = match();
      db.tables[this.table] = table.filter((r) => !rows.includes(r));
      return { data: null, error: null };
    }
    let rows = match().map((r) => db.view(this.table, r));
    for (const [c, asc] of this.sorts.slice().reverse()) rows.sort((a, b) => (a[c] > b[c] ? 1 : a[c] < b[c] ? -1 : 0) * (asc ? 1 : -1));
    const count = rows.length;
    if (this.rng) rows = rows.slice(this.rng[0], this.rng[1] + 1);
    if (this.lim != null) rows = rows.slice(0, this.lim);
    if (this.head) return { data: null, count, error: null };
    rows = rows.map((r) => pick(r, this.cols));
    if (this.one) {
      if (!rows.length && !this.maybe) return { data: null, error: { message: "No rows found" } };
      return { data: rows[0] || null, error: null };
    }
    return { data: rows, count, error: null };
  }
}

export function createDemoClient() {
  const now = () => new Date().toISOString();
  const user = { id: "demo-user", email: "team@avicontravel.com" };
  const listeners = new Set();
  let session = sessionStorage.getItem("demo-session") ? { user } : null;
  const blobs = new Map();

  const db = {
    tables: { products: [], product_revisions: [], publish_jobs: [], admins: [{ user_id: user.id, email: user.email, name: "Demo team", role: "owner" }], form_requests: [] },
    ids: { product_revisions: 1, publish_jobs: 1, form_requests: 1 },
    defaults(table, r) {
      if (table === "products") return { status: "hidden", live_data: null, live_status: null, published_at: null, created_at: now(), updated_at: now(), updated_by: user.id, ...r };
      if (table === "publish_jobs") return { id: this.ids.publish_jobs++, requested_at: now(), status: "queued", ...r };
      return r;
    },
    view(table, r) { return table === "products" ? { ...r, has_changes: hasChanges(r) } : r; },
    update(table, r, patch) {
      if (table === "products" && (("data" in patch && !same(patch.data, r.data)) || ("status" in patch && patch.status !== r.status))) {
        this.tables.product_revisions.push({ id: this.ids.product_revisions++, slug: r.slug, status: r.status, data: clone(r.data), created_at: now(), created_by: user.id });
        patch.updated_at = now();
      }
      Object.assign(r, patch);
    },
  };

  const ready = fetch("demo-data.json").then((res) => res.json()).then((site) => {
    let i = 0;
    for (const [slug, data] of Object.entries(site)) {
      db.tables.products.push({ slug, section: slug.split("/")[0], status: "published", template: null, data: clone(data), live_data: clone(data), live_status: "published", sort_order: (i++) * 10, created_at: now(), updated_at: now(), published_at: "2026-09-10T09:00:00Z" });
    }
    const p = db.tables.products[2];
    if (p) { p.data.blocks.price.amount = String(Number(p.data.blocks.price.amount || 50) + 5); }
    const examples = [
      ["booking", "new", "Example Guest (sample)", "sample.guest@example.com", "+44 7700 900123", "Luxor Hot Air Balloon", "2026-10-12", 2, 0, "Can we be picked up from our Nile cruise boat?"],
      ["tailor_made", "new", "Sample Family (example)", "family@example.com", "+1 202 555 0147", null, "2026-12-20", 2, 2, "10 days in Egypt with kids, Cairo + Nile cruise + Red Sea."],
      ["contact", "contacted", "Test Contact (example)", "contact@example.com", "", null, null, null, null, "Do you offer Arabic-speaking guides?"],
      ["booking", "booked", "Demo Couple (sample)", "couple@example.com", "+49 30 901820", "4 Days Nile Cruise Aswan to Luxor", "2026-11-03", 2, 0, ""],
      ["transfer", "closed", "Airport Sample (example)", "", "+971 50 123 4567", null, "2026-09-30", null, null, "Cairo airport to Giza hotel"],
    ];
    examples.forEach(([form_type, status, name, email, phone, tour, date, adults, children, message], k) => {
      db.tables.form_requests.push({ id: db.ids.form_requests++, created_at: new Date(Date.now() - (k * 7 + 1) * 3600e3).toISOString(), form_type, status, name, email, phone, tour_package: tour,
        travel_date: date, adults, children, message, page_url: tour ? "https://avicontravel.com/tours/luxor-hot-air-balloon/" : "https://avicontravel.com/contact/", email_sent: true, whatsapp_sent: false, notes: "" });
    });
  });

  const from = (table) => {
    const q = new Query(db, table);
    const run = q.run.bind(q);
    q.run = async () => { await ready; return run(); };
    return q;
  };

  return {
    from,
    auth: {
      async getSession() { await ready; return { data: { session } }; },
      onAuthStateChange(cb) { listeners.add(cb); return { data: { subscription: { unsubscribe: () => listeners.delete(cb) } } }; },
      async signInWithPassword() { await wait(300); session = { user }; sessionStorage.setItem("demo-session", "1"); listeners.forEach((cb) => cb("SIGNED_IN", session)); return { data: { session }, error: null }; },
      async signOut() { session = null; sessionStorage.removeItem("demo-session"); listeners.forEach((cb) => cb("SIGNED_OUT", null)); return { error: null }; },
      async resetPasswordForEmail() { await wait(300); return { error: null }; },
      async updateUser() { return { error: null }; },
    },
    storage: {
      from() {
        return {
          async upload(path, blob) { await wait(400); blobs.set(path, URL.createObjectURL(blob)); return { data: { path }, error: null }; },
          getPublicUrl(path) { return { data: { publicUrl: blobs.get(path) || path } }; },
        };
      },
    },
    functions: {
      async invoke() {
        await ready;
        const jobs = db.tables.publish_jobs;
        const busy = jobs.find((j) => ["queued", "running", "deploying"].includes(j.status));
        if (busy) return { data: { job: busy, already_running: true }, error: null };
        const job = db.defaults("publish_jobs", { requested_by: user.id });
        jobs.push(job);
        const pending = db.tables.products.filter(hasChanges);
        setTimeout(() => Object.assign(job, { status: "running", run_url: "https://github.com/" }), 2000);
        setTimeout(() => {
          for (const r of pending) Object.assign(r, { live_data: clone(r.data), live_status: r.status, published_at: now() });
          Object.assign(job, { status: "deploying", changed: pending.map((r) => r.slug), commit_sha: "demo" });
        }, 5000);
        setTimeout(() => Object.assign(job, { status: "success", finished_at: now() }), 9000);
        return { data: { job }, error: null };
      },
    },
  };
}
