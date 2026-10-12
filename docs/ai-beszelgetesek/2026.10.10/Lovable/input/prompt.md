Build ONLY the frontend of a web app called "Legal Problem Screening & Lawyer Matching". The user stories pasted below this prompt (SZD-I, US-01 to US-38) are the source of truth for features and acceptance criteria. There is no backend yet: every request returns mock data. Later a Python FastAPI backend will replace the mocks, and pages or components must not need any changes when that happens.

TECH
- React + TypeScript (Vite). All code in .ts/.tsx files. No .js/.jsx files. TypeScript strict mode, no "any".
- Styling: plain CSS only. Use CSS Modules plus one global stylesheet with CSS custom properties for colours, spacing and fonts. No Tailwind, no CSS-in-JS, no UI component libraries.
- Keep dependencies minimal (react-router is fine). Do NOT use Supabase, Lovable Cloud, any auth provider or any database.

CONFIGURATION
- One file, src/config.ts, reads the environment variables:
  VITE_API_BASE_URL (default "http://localhost:8000/api/v1")
  VITE_USE_MOCKS ("true"/"false", default "true")
- Add a .env.example. Switching to the real backend must only require changing these two values.
- Do not hard-code tunable business values in components. These are: description min/max length (30/5000), follow-up questions per round (5), max rounds (2), page sizes, password minimum length (8) and inactivity timeout (30 min). Load them from GET /config. The mock returns these defaults.

API LAYER (all data access goes through it)
- src/api/http.ts is the single fetch wrapper. Every request:
  - uses credentials: "include", JSON bodies and the base URL from config;
  - normalises errors into one ApiError type {status, code, message, field_errors?};
  - maps FastAPI's 422 validation format ({"detail":[{"loc":[...],"msg":"..."}]}) to per-field errors.
- The wrapper handles these responses:
  - 401: redirect to log-in, remembering the page the user was on;
  - 403: show "Access denied";
  - 404: show "Not found";
  - 429: show a "try again later" message and respect the Retry-After header;
  - 5xx: show a general error message.
- src/api/types.ts holds all request and response types.
  - Field names are snake_case, exactly as the backend JSON will be, so no mapping is needed later.
  - Dates are ISO 8601 strings.
  - Enums are string unions:
    - case status: in_progress | waiting_for_answers | recommendations_ready | lawyer_chosen | unclassified;
    - role: client | admin;
    - account status: active | suspended | suspended_auto | banned;
    - classification result: classified | needs_more_info | not_supported.
- Create one service module per area: auth, config, cases (screening, follow-up questions, documents, classification, recommendations, lawyer choice), lawyers, categories, admin, metrics and account. Each exports typed async functions.
- Pages and components never call fetch directly and never import mocks.
- Each service has a real implementation (calling http.ts) and a mock implementation with the identical interface. config.ts selects which one is used.
- Mocks:
  - Use an in-memory store, persisted to sessionStorage so a page refresh keeps state.
  - Seed it with realistic Hungarian data: about 12 lawyers, 8 legal categories, one client and one admin test account, and a few cases in every status.
  - Add a 300–800 ms simulated delay to every response.
  - Mocks must enforce the same rules a real server would, so every error state can be tested:
    - opening another user's case returns 404;
    - admin-only endpoints return 403 for clients;
    - invalid input returns 422;
    - duplicate usernames or email addresses are rejected;
    - addresses on a banned-email list are rejected;
    - passwords on a small "leaked passwords" list are rejected;
    - suspended or banned accounts get the correct status at log-in.

IDENTIFIERS
- Every object has a UUID v4 string id, generated with crypto.randomUUID() in the mocks. This covers users, cases, lawyers, categories, documents, follow-up questions, recommendations and taxonomy versions.
- Treat ids as opaque strings: never numeric, never sequential, never parsed.
- URLs use the UUID (e.g. /cases/:caseId). Where a short "case number" is shown, display the first 8 characters.

SECURITY
- The session is an HttpOnly cookie set by the server. The frontend never stores tokens, passwords or session data in localStorage or sessionStorage (the mock database is the only exception).
- CSRF (Cross-Site Request Forgery) protection:
  - When the app starts, and after every log-in, log-out and registration, call GET /auth/csrf. It returns {csrf_token}.
  - Keep the token in memory only, and send it in the X-CSRF-Token header on every POST, PUT, PATCH and DELETE request.
  - If a request fails with 403 and code "csrf_invalid", fetch a new token and retry once.
  - The header name and the endpoint path are constants in config.ts.
  - The mock issues tokens and rejects state-changing requests that don't send a valid one.
- Route guards (visitor / client / admin) are for convenience only; the server will enforce access.
  - Admin routes opened by non-admins show "Access denied".
  - Another user's case shows "Not found" and reveals nothing about it.
- Never render user-supplied text as HTML.

PAGES / ROUTES
- Public:
  - start page, disclaimer and privacy policy;
  - register and log-in;
  - forgot password (placeholder);
  - account status page (suspended by an admin with an end date, suspended automatically, or banned).
- Client: screening wizard, My cases (list and detail), Edit profile.
- Admin:
  - Admin dashboard;
  - Lawyers (list, create, edit);
  - Categories (the taxonomy);
  - Cases (list and read-only detail);
  - Metrics: accuracy evaluation from US-16, i.e. overall and per-category accuracy, confusion matrix, low-confidence fallback rate and saved evaluation runs.
  - Users, Warnings and Logs: placeholder pages only (later stories).
- The menubar follows US-22, US-23, US-25 and US-26 exactly. The profile dropdown works with mouse hover, tap/click and keyboard.

SCREENING WIZARD (US-01 to US-09, US-35, US-36)
Steps:
1. Describe the problem.
   - Show a live character counter.
   - Validate against the min/max length; below the minimum, show a friendly message with an example of a good description.
2. Optional document upload. The mock returns extracted fields, which the client confirms or corrects.
3. Follow-up questions.
   - Types: multiple choice, yes/no, date and short text.
   - Every question can be skipped; a skipped question is sent as "not_answered", not as a negative answer.
4. Classification result. The backend can return:
   - classified: category plus confidence;
   - needs_more_info: go to another round of questions;
   - not_supported: honest message with suggested next steps (US-03).
5. Preferences: city, languages, online / in-person / either, and price. The language is pre-filled with the UI language.
6. Recommendations.
   - Show up to 3 lawyers, each with a per-criterion ✓/✗ breakdown and a one-sentence summary.
   - "Choose this lawyer" reveals the contact details, with clickable tel: and mailto: links.
   - The client can change their choice.
   - If the backend says the chosen lawyer was deactivated, show the message with a "Re-do recommendation" button.
Rules for the whole wizard:
- Show the short disclaimer on every step.
- Save progress after each step, so "Continue" in My cases resumes where the client stopped, including after a session expiry.
- If the analysis fails, show the US-38 error with a "Try again" button that repeats only the failed step and keeps everything entered.
- The frontend never calls an AI provider; it only calls the backend.

ADMIN
- Lawyer form: enforces the US-12 schema. Areas of expertise and languages come from fixed lists, and errors are shown inline next to the wrong field.
- Categories: managed per US-13.
  - Each category has a Hungarian name, description and example problems.
  - Blocked removal shows the affected lawyers.
  - The taxonomy version number is visible.
- Cases list: works per US-15.
  - Combinable filters and a "Clear filters" button.
  - Sortable columns, 50 cases per page, total count shown.
  - Filtering, sorting and pagination are sent to the API as query parameters, not done in the browser.
- Case detail: masked text only, no original files, fully read-only.

ACCOUNT
- Registration: per US-19.
  - Consent checkbox, live password strength indicator and show-password toggle.
  - Pasting is allowed. No composition rules (no "must contain a number").
  - Errors name the field that is wrong, and the form keeps everything else that was typed.
- After registering:
  - log in automatically (US-20);
  - return to the screening if the visitor came from there (US-18).
- Log-in: per US-21, with a generic error message and a lockout message after repeated failures.
- Edit profile: per US-24.
  - Includes consent withdrawal and retention information.
  - Has "Download my data" and "Delete my account and data", both calling API stubs. Deletion needs a confirmation dialog.
- Delete a single case: per US-31, with a confirmation dialog naming the case.

CROSS-CUTTING
- Languages:
  - Hungarian (default) and English, with a language switcher visible to everyone.
  - All UI text lives in translation files, none hard-coded in components.
  - Dates, times and numbers are formatted with Intl for the chosen language.
- Accessibility: WCAG 2.2 AA.
  - Semantic HTML and a label on every input.
  - Visible focus, and keyboard support for dialogs and dropdowns.
  - Sufficient colour contrast, and error messages announced to screen readers.
- Layout: responsive from 360 px phone width to desktop.
- Every data view has loading, empty and error states.
- Visual style: calm, trustworthy and professional. Users are often stressed people with a legal problem.

DELIVERABLES
- Folder structure: src/api, src/api/mock, src/pages, src/components, src/i18n, src/styles.
- README containing:
  - setup steps;
  - how to switch from mocks to the real API;
  - the mock test accounts;
  - a list of every endpoint, so it can be turned into the OpenAPI spec (US-17). For each endpoint give the method, path, request body, response, possible error codes and required role (visitor / client / admin).