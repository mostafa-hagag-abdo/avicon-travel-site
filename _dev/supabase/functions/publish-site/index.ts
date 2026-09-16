// Control panel "Publish" button -> starts the GitHub workflow that writes the website (publish-content.yml).
//
// Deploy: Supabase -> Edge Functions -> Deploy a new function -> name "publish-site", paste this file,
//         and turn OFF "Verify JWT" (this function checks the signed-in user itself).
// Secret (Edge Functions -> Secrets):
//   GITHUB_PUBLISH_TOKEN  fine-grained GitHub token: only repository avicon-travel-site, permission "Actions: Read and write"
// Optional secrets: GITHUB_REPO (owner/name), GITHUB_WORKFLOW (file name)

const REPO = Deno.env.get("GITHUB_REPO") ?? "mostafa-hagag-abdo/avicon-travel-site";
const WORKFLOW = Deno.env.get("GITHUB_WORKFLOW") ?? "publish-content.yml";
const ALLOWED_ORIGINS = [
  "https://avicontravel.com",
  "https://www.avicontravel.com",
  "http://127.0.0.1:8099",
  "http://localhost:8099",
];

function corsHeaders(origin: string): Record<string, string> {
  return {
    "Access-Control-Allow-Origin": ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0],
    "Access-Control-Allow-Headers": "authorization, apikey, content-type, x-client-info",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Vary": "Origin",
  };
}

Deno.serve(async (req) => {
  const cors = corsHeaders(req.headers.get("origin") ?? "");
  const json = (body: unknown, status = 200) =>
    new Response(JSON.stringify(body), { status, headers: { ...cors, "Content-Type": "application/json" } });

  if (req.method === "OPTIONS") return new Response(null, { headers: cors });
  if (req.method !== "POST") return json({ error: "Use POST" }, 405);

  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const anonKey = Deno.env.get("SUPABASE_ANON_KEY") ?? serviceKey;
  const githubToken = Deno.env.get("GITHUB_PUBLISH_TOKEN");

  // 1. who is asking
  const token = (req.headers.get("authorization") ?? "").replace(/^Bearer\s+/i, "");
  if (!token) return json({ error: "Please sign in again." }, 401);
  const userRes = await fetch(`${supabaseUrl}/auth/v1/user`, {
    headers: { apikey: anonKey, Authorization: `Bearer ${token}` },
  });
  if (!userRes.ok) return json({ error: "Please sign in again." }, 401);
  const user = await userRes.json();

  const rest = (path: string, init: RequestInit = {}) =>
    fetch(`${supabaseUrl}/rest/v1/${path}`, {
      ...init,
      headers: {
        apikey: serviceKey,
        ...(serviceKey.startsWith("eyJ") ? { Authorization: `Bearer ${serviceKey}` } : {}),
        "Content-Type": "application/json",
        Prefer: "return=representation",
        ...(init.headers ?? {}),
      },
    });

  const team = await (await rest(`admins?select=user_id&user_id=eq.${encodeURIComponent(user.id)}`)).json();
  if (!Array.isArray(team) || team.length === 0) return json({ error: "This account is not on the team." }, 403);

  if (!githubToken) return json({ error: "Publishing is not set up yet (missing GITHUB_PUBLISH_TOKEN)." }, 500);

  // 2. one publish at a time: return the running one instead of starting another
  const since = new Date(Date.now() - 30 * 60 * 1000).toISOString();
  const busy = await (await rest(
    `publish_jobs?select=*&status=in.(queued,running,deploying)&requested_at=gt.${encodeURIComponent(since)}&order=id.desc&limit=1`,
  )).json();
  if (Array.isArray(busy) && busy.length) return json({ job: busy[0], already_running: true });

  const created = await rest("publish_jobs", { method: "POST", body: JSON.stringify({ requested_by: user.id }) });
  if (!created.ok) return json({ error: "Could not record the publish request." }, 500);
  const [job] = await created.json();

  // 3. start the workflow
  const gh = await fetch(`https://api.github.com/repos/${REPO}/actions/workflows/${WORKFLOW}/dispatches`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${githubToken}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "avicon-control-panel",
    },
    body: JSON.stringify({ ref: "main", inputs: { job_id: String(job.id) } }),
  });
  if (!gh.ok) {
    console.error("GitHub dispatch failed", gh.status, await gh.text());
    const message = gh.status === 401 || gh.status === 403 || gh.status === 404
      ? "GitHub refused to start publishing. The GITHUB_PUBLISH_TOKEN secret is wrong or expired."
      : `GitHub could not start publishing (error ${gh.status}). Try again in a minute.`;
    await rest(`publish_jobs?id=eq.${job.id}`, {
      method: "PATCH",
      body: JSON.stringify({ status: "failed", message, finished_at: new Date().toISOString() }),
    });
    return json({ error: message, job: { ...job, status: "failed", message } }, 502);
  }
  return json({ job });
});
