# Control panel (avicontravel.com/admin/)

Requests inbox + editor for trips and packages. The website stays static: the panel saves drafts in Supabase, and
**Publish** runs a GitHub workflow that writes the pages and uploads them.

```
admin/ (static page, Supabase Auth)
  ├─ reads/updates  public.form_requests            (website forms, see _dev/supabase/)
  ├─ edits          public.products.data            (draft; product_revisions keeps every previous version)
  ├─ uploads        storage bucket site-images
  └─ Publish ─> Edge Function publish-site ─> .github/workflows/publish-content.yml
                   └─ _dev/cms/sync.py publish: pages + cards + llms.txt + search + sitemap + product_meta.json
                      ─> product_meta.py, schema_products.py, health_check.py ─> commit main ─> deploy.yml
push to main touching trip pages ─> .github/workflows/cms-import.yml ─> sync.py import (repo edits reach the panel)
```

| File | What |
|---|---|
| `blocks.py` | reads/writes the editable blocks of a trip page; `test_blocks.py` (all pages round-trip) |
| `sync.py` | export / import / publish / save / finish; `test_sync.py` runs in a git worktree only |
| `cms.sql` | tables, RLS (team = `public.admins`), revisions trigger, storage bucket |
| `hidden/` | pages of hidden trips (+ where their cards were), restored when a trip is shown again |

## Setup (once)
1. Supabase SQL Editor: run `_dev/supabase/schema.sql` (if not yet) and `_dev/cms/cms.sql`.
2. Supabase Auth → Users → Add user (email + password, auto-confirm). Then SQL:
   `insert into public.admins (user_id, email, name, role) select id, email, 'Name', 'owner' from auth.users where email = 'x@y' on conflict do nothing;`
3. GitHub → Settings → Secrets and variables → Actions: secret `SUPABASE_SERVICE_ROLE_KEY`, variable `SUPABASE_ANON_KEY`.
4. GitHub Actions → "Update control panel from the site" → Run workflow (fills the panel with the 31 trips).
5. GitHub fine-grained token (only this repo, Actions: read and write) → Supabase Edge Functions secret `GITHUB_PUBLISH_TOKEN`;
   deploy `_dev/supabase/functions/publish-site/index.ts` as `publish-site` with "Verify JWT" off.
6. Any push to main (or re-run "Deploy to Hostinger") writes `admin/config.js` with the anon key.

## Local
- `python _dev/cms/test_blocks.py`
- `git -c core.longpaths=true worktree add --detach <dir> HEAD` then `python <dir>/_dev/cms/test_sync.py`
- `python _dev/cms/sync.py export --out admin/demo-data.json`, serve the repo on 127.0.0.1:8099, open `/admin/?demo`
