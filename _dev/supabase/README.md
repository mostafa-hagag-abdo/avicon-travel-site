# Website forms → Supabase

Every form on avicontravel.com posts to one Supabase Edge Function: https://tdpsvcsniftrgnrdyhgi.supabase.co/functions/v1/smooth-worker (project `avicon-travel`, Frankfurt). The source is `functions/submit-request/index.ts`; Supabase auto-named the deployed function `smooth-worker`. The function:
1. saves the request in `public.form_requests`,
2. emails the team through the Hostinger mailbox (SMTP),
3. sends a WhatsApp message through the WhatsApp Cloud API.

This replaced Web3Forms. See `functions/submit-request/index.ts` for the details.

## Parts
| File | What it is |
|---|---|
| `schema.sql` | The table. Run it in Supabase → SQL Editor (safe to re-run). RLS is on with no policies, so only the function writes to it. |
| `functions/submit-request/index.ts` | The endpoint. Deploy it with **Verify JWT off**. |
| `../apply_forms.py <function URL>` | Points every site form at the function, adds `form_type`, removes the Web3Forms fields, and updates GA4 tracking. |

The forms and their `form_type`:
- `booking`: the 31 trip pages (JSON via fetch, then `/thank-you/`)
- `contact`: `/contact/` (JSON via fetch, then a modal)
- `tailor_made`: the home page (multipart via fetch, then an inline note)
- `transfer`: the 3 car pages (a plain form post, answered with a 303 redirect to `/thank-you/`)

## Secrets
Set these in Supabase → Edge Functions → Secrets. The owner enters them; they never go in this repo.
`SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are provided automatically.

| Secret | Notes |
|---|---|
| `SMTP_HOST` | `smtp.hostinger.com` |
| `SMTP_PORT` | `465` (SSL). Supabase blocks outbound ports 25 and 587. |
| `SMTP_USER` | The Hostinger mailbox, e.g. `info@avicontravel.com` |
| `SMTP_PASS` | That mailbox's password (hPanel → Emails) |
| `NOTIFY_EMAIL_TO` | Comma-separated recipients |
| `NOTIFY_EMAIL_FROM` | Optional. Default `"Avicon Website" <SMTP_USER>`; Hostinger only accepts the logged-in mailbox as the sender. |
| `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID` | Meta WhatsApp Cloud API (permanent system-user token) |
| `WHATSAPP_TO` | Comma-separated team numbers with the country code, e.g. `201200555600` |
| `WHATSAPP_TEMPLATE` | Name of the approved template below. Without it, a plain text message is sent, which only arrives within 24 hours of the team number messaging the business number. |
| `WHATSAPP_TEMPLATE_LANG` | Default `en` |
| `WHATSAPP_API_VERSION` | Default `v21.0` |

A channel with missing secrets is skipped and recorded in `notify_error`. That means WhatsApp can be switched on later just by adding its secrets, with no redeploy.

## WhatsApp template (Meta → WhatsApp Manager → Message templates)
- Category **Utility**, name `new_website_request`, language English
- Meta rejects a body that starts or ends with a variable, so keep the last line.
```
New {{1}} from avicontravel.com
Name: {{2}}
Contact: {{3}}
Details: {{4}}
Please reply to the guest soon.
```
Sample values:
- `Booking request #12 (Luxor Hot Air Balloon)`
- `John Smith`
- `+44 7700 900123 · john@example.com`
- `Date 2026-11-02 · 2 adults · First time in Egypt`

## Protection
- Hidden `botcheck` honeypot.
- Name plus a valid email or phone required.
- At most 5 requests per email or phone in 10 minutes.
- 50 KB body limit.
- CORS limited to the site (plus `127.0.0.1:8099` for local previews).

## Local test
`bash test_function.sh` (kept in the session scratchpad) runs the function with Deno against mocks of Supabase, SMTP and WhatsApp.

## Reading requests
Supabase → Table Editor → `form_requests`. Use `status` (new → contacted → booked/closed, or spam) and `notes` to track follow-up.
