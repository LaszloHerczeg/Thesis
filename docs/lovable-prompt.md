# Build the frontend: legal problem screening & lawyer matching (mock API)

## 1. Goal

Build the complete **frontend** of a web app where members of the public describe a legal problem in their own words, answer follow-up questions, get the case sorted into one legal category, and see up to three matching lawyers. Administrators manage the category list (taxonomy) and lawyer profiles, browse all cases, and view categorization-accuracy metrics.

There is **no backend yet**. Every screen gets its data through one typed API layer. For now an in-browser **mock server** answers that layer: it stores data in `localStorage` and behaves the way the real server will (HTTP status codes, validation, access checks). Later the mock will be switched off and the same calls will go to a real REST API described by an OpenAPI specification, so keep the API layer clean and easy to swap.

Story IDs (US-xx) refer to the project's user stories. Mention the ID in a code comment where a feature implements a story.

## 2. Hard rules

- Frontend only. Don't add a backend of any kind (no Supabase, Lovable Cloud, database or auth service), and make no real network calls while the mock is on.
- All UI text is **Hungarian**, formal register ("Ön"). Dates and numbers use `hu-HU` formatting (`2026. 10. 11.`, `25 000 Ft`).
- Desktop browsers only. Don't build phone- or tablet-specific features (US-23).
- Nothing in the app (page, button, route or mock endpoint) creates administrators or changes a user's role (US-14, US-17, US-19). Admin accounts exist only in the seed data.
- Values from the stories (lengths, limits, page sizes) come from the config files in section 4, never hard-coded in components.
- Case IDs are random UUIDs (`crypto.randomUUID()`) and appear in URLs (US-29).
- Unfinished cases (still waiting for follow-up answers) never appear in any list.

## 3. Decisions for details the user stories leave open

Implement these as written:

1. Formal Hungarian ("Ön") everywhere. The developer panel (5.6) is in English because it's a developer tool.
2. The product name is the placeholder `[Terméknév]` in `appConfig.APP_NAME`. The start page and the privacy policy are placeholder pages. A footer on every page links to the privacy policy. The start page has a "Felmérés indítása" button.
3. Route paths are English (`/screening`, `/cases`, …). Visitors opening screening pages go to login (US-18). Visitors opening other logged-in pages (`/cases`, `/profile`) go to login and come back afterwards. Admin pages behave as in US-27. Logged-in users opening `/login` or `/register` go to `/`. `returnTo` accepts only internal paths starting with `/`.
4. A screening's follow-up questions and result are shown at `/screening/:caseId`. The same result block is reused on the case detail page.
5. Recommendation cards show all lawyer data at once, with the email as a `mailto:` link. There is no "choose" button.
6. The ✓ breakdown lists the case's category plus each preference the client filled in, with the client's value. Blank preferences aren't listed, and there are no ✗ items.
7. A categorized case with 0 matching lawyers keeps the status *categorized* and shows "Nincs megfelelő ügyvéd."
8. An uncategorized case stores why (`not_supported`, `max_rounds_reached` or `invalid_ai_answer`), so the right message also shows later on the case detail page.
9. Unfinished cases have `status: null`. Opening one at `/cases/:caseId` redirects to `/screening/:caseId`, and admin endpoints return 404 for them.
10. Each follow-up question has a "Kihagyom" button. An empty or skipped answer is sent as `null`. Short-text answers are limited to 200 characters.
11. The description box stops accepting input at 5,000 characters. The too-short message appears on submit. The description is stored exactly as typed, not trimmed.
12. The maximum hourly rate is a text field accepting whole forints greater than 0 (spaces are ignored, e.g. `25 000`). "Mindkettő megfelel" and an empty consultation-format field both mean no format filter.
13. Usernames allow `a–z`, `A–Z`, `0–9` and `_`. Passwords follow US-19 exactly: 8–12 lowercase `a–z` letters.
    - The "contains the username" check is case-insensitive.
    - The "contains the email" check uses the part before `@`.
    - The site name is compared lowercased, without accents or non-letters (`[Terméknév]` → `termeknev`).
    - Passwords that are too long aren't cut off; the field shows an error instead.
14. Taxonomy:
    - The identifier and the name are required free text.
    - The identifier must be unique and can't be changed after creation, because it's the ID the categorizer returns.
    - The page shows the current version number, and every add, rename or removal raises it by 1.
    - Cases keep a snapshot of the category they were given.
15. Lawyer hourly rates are whole forints. New lawyers get UUIDs. Lawyers can't be deleted (no story asks for it).
16. All cases: the client's preferences appear as four sortable columns. The default sort is newest first. The user filter matches username or email (contains, case-insensitive).
17. Metrics: the newest run is preselected. Per-category accuracy appears as a bar chart plus a table. The confusion matrix has an extra "Nem kategorizált" column.
18. Edit profile has two sections, each with its own "Mentés" and "Mégse".
19. API error messages and field errors are Hungarian texts that come from the API. The UI shows each field error under its field.
20. The mock returns fixed results driven by the developer panel. Recommendations always show current lawyer data, passwords are hashed with SHA-256, and demo data can be reset from the developer panel.

## 4. Stack and configuration

**Stack:**
- React, TypeScript, Vite, Tailwind CSS, shadcn/ui, lucide-react icons, React Router.
- TanStack Query for all server state, with no retries on 4xx.
- react-hook-form + zod for all forms.
- `@zxcvbn-ts/core` + `@zxcvbn-ts/language-common` for the password strength meter.
- date-fns with the `hu` locale.
- Recharts for charts.

`src/config/appConfig.ts` is used by the UI and by the mock's validation:

```ts
export const appConfig = {
  APP_NAME: '[Terméknév]',            // placeholder product name
  USE_MOCK_API: true,                 // false = real REST API
  API_BASE_URL: '/api',
  DESCRIPTION_MIN_LENGTH: 30,         // US-01
  DESCRIPTION_MAX_LENGTH: 5000,       // US-01
  SHORT_TEXT_ANSWER_MAX_LENGTH: 200,  // US-02
  USERNAME_MIN_LENGTH: 8,             // US-19
  USERNAME_MAX_LENGTH: 30,            // US-19
  PASSWORD_MIN_LENGTH: 8,             // US-19
  PASSWORD_MAX_LENGTH: 12,            // US-19
  MY_CASES_PAGE_SIZE: 20,             // US-30
  ADMIN_CASES_PAGE_SIZE: 50,          // US-15
};
```

`src/mocks/mockConfig.ts` stands in for the server's configuration file:

```ts
export const mockConfig = {
  CATEGORIZATION_MODE: 'ai' as 'ai' | 'rule_based', // US-04, US-09, US-35: set in the server config, never in the UI
  MAX_QUESTIONS_PER_ROUND: 5,                         // US-02
  MAX_FOLLOW_UP_ROUNDS: 2,                            // US-02
  MAX_RECOMMENDATIONS: 3,                             // US-06
  FIXED_CATEGORY_ID: 'berleti_jog',
  FIXED_RECOMMENDATION_LAWYER_IDS: ['lawyer-01', 'lawyer-02', 'lawyer-03'],
  MOCK_DB_VERSION: 1,                                 // bump to reseed
};
```

`src/constants/languages.ts` holds the fixed language list (US-05, US-12), as code → label: `hu` magyar, `en` angol, `de` német, `fr` francia, `es` spanyol, `it` olasz, `ro` román, `sk` szlovák, `uk` ukrán, `ru` orosz.

## 5. API layer and mock server

### 5.1 Structure

- `src/api/types.ts`: every request and response type (5.3). These become the OpenAPI schemas later.
- `src/api/client.ts`: `apiRequest<T>(method, path, { query?, body? })`.
  - With `USE_MOCK_API` on, it calls `mockServer.handle({ method, path, query, body })` in-process.
  - Otherwise it calls `fetch(API_BASE_URL + path, { method, credentials: 'include', headers: { 'Content-Type': 'application/json' }, body })`.
  - Any non-2xx status throws `ApiError { status, code, message, fieldErrors?, details? }`.
- `src/api/endpoints/*.ts`: one typed function per endpoint (e.g. `casesApi.create`). Pages and hooks use only these, never `apiRequest` or the mock directly.
- `src/mocks/`: `server.ts` (router: method + path pattern → handler), `db.ts`, `seed.ts`, `handlers/*.ts`, `validation.ts`, `devScenario.ts`, `mockConfig.ts`.
- **Sessions:** the mock creates a random token at login and registration and keeps it in `localStorage` under `mock_session_token`. Only the mock reads it. The real server will use a session cookie, so UI code never touches tokens.
- **After mutations,** invalidate the affected queries so everything updates at once. For example, a deleted case disappears from "Ügyeim" and "Összes ügy", and an edited lawyer updates the recommendation cards.

### 5.2 Errors and status codes

Error body: `{ "error": { "code": string, "message": string, "fieldErrors"?: Record<string, string>, "details"?: object } }`.

| Status | Code | When |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Invalid input, including "already in use". Always includes `fieldErrors`. |
| 401 | `UNAUTHENTICATED` | No valid session, on every endpoint except register and login. For `GET /auth/me` this simply means "logged out". |
| 401 | `INVALID_CREDENTIALS` | Failed login. Identical whether or not the account exists (US-21). |
| 403 | `FORBIDDEN` | A logged-in non-admin calls any `/admin/*` endpoint (US-27). |
| 404 | `NOT_FOUND` | Unknown resource, or a case the caller doesn't own. The two responses are identical (US-29). |
| 409 | `CATEGORY_IN_USE` | Removing a category that lawyers still have. Includes `details.affectedLawyers: { id, name }[]` (US-13). |

When any request returns 401 `UNAUTHENTICATED`, clear the cached user so the menubar switches to the logged-out state.

### 5.3 Types

```ts
export type Role = 'client' | 'admin';
export interface User { id: string; username: string; email: string; role: Role; }

export type LanguageCode = 'hu' | 'en' | 'de' | 'fr' | 'es' | 'it' | 'ro' | 'sk' | 'uk' | 'ru';
export type ConsultationFormat = 'online' | 'in_person';
export type ConsultationPreference = ConsultationFormat | 'either';

export interface Category { id: string; name: string; }        // id = identifier typed by the admin (US-13)

export interface Lawyer {                                       // US-12
  id: string;
  name: string;
  email: string;
  categoryIds: string[];                                        // areas of expertise, at least one
  city: string;                                                 // office location
  languages: LanguageCode[];                                    // at least one
  consultationFormats: ConsultationFormat[];                    // at least one
  hourlyRate: number;                                           // whole forints
}
export type LawyerInput = Omit<Lawyer, 'id'>;

export interface Preferences {                                  // US-05: empty = no preference
  city: string | null;
  languages: LanguageCode[];
  consultationFormat: ConsultationPreference | null;
  maxHourlyRate: number | null;                                 // forints
}

export type QuestionType = 'single_choice' | 'yes_no' | 'date' | 'short_text';   // US-02
export interface FollowUpQuestion { id: string; round: number; type: QuestionType; text: string; options?: string[]; }
export interface FollowUpAnswer { questionId: string; value: string | null; }     // null = not answered; yes_no: 'yes' | 'no'; date: 'YYYY-MM-DD'

export type CaseStatus = 'categorized' | 'uncategorized';
export type UncategorizedReason = 'not_supported' | 'max_rounds_reached' | 'invalid_ai_answer';

export interface MatchedCriterion { label: string; value: string; }              // always shown with a ✓
export interface Recommendation {                                                // US-06, US-07, US-08
  rank: number;                                                                  // 1–3
  lawyer: Lawyer;                                                                // current lawyer data
  matchedCriteria: MatchedCriterion[];
  summary: string;                                                               // one sentence
}

export interface Case {
  id: string;                                   // UUID
  ownerUsername: string;
  createdAt: string;                            // ISO date-time
  description: string;                          // exactly as submitted (US-01)
  preferences: Preferences;
  questions: FollowUpQuestion[];                // every question asked so far, all rounds
  answers: FollowUpAnswer[];
  pendingQuestions: FollowUpQuestion[] | null;  // current round while waiting for answers
  status: CaseStatus | null;                    // null while unfinished
  uncategorizedReason: UncategorizedReason | null;
  category: Category | null;                    // snapshot taken when categorized
  taxonomyVersion: number | null;               // taxonomy version used (US-13)
  recommendations: Recommendation[];            // 0–3, ranked
}

export interface CaseSummary { id: string; createdAt: string; category: Category | null; status: CaseStatus; }
export interface AdminCaseRow extends CaseSummary { ownerUsername: string; preferences: Preferences; }
export interface Page<T> { items: T[]; total: number; page: number; pageSize: number; }

export interface EvaluationRunSummary {         // US-16
  id: string;
  runAt: string;
  mode: 'rule_based' | 'ai';
  taxonomyVersion: number;
  testSetSize: number;
  overallAccuracy: number;                      // 0–1
}
export interface EvaluationRun extends EvaluationRunSummary {
  perCategory: { categoryId: string; categoryName: string; correct: number; total: number; accuracy: number }[];
  confusionMatrix: { rowLabels: string[]; columnLabels: string[]; counts: number[][] };  // rows = true category, columns = predicted
}
```

### 5.4 Endpoints

Paths are relative to `API_BASE_URL`.
- "Logged-in" includes admins, who may also run screenings.
- "Owner" means the user who created the case. Anyone else gets 404 on owner endpoints, admins included; admins use `/admin/cases` instead.
- No endpoint creates administrators or changes roles.

| Method | Path | Who | Request | Success | Story |
|---|---|---|---|---|---|
| POST | `/auth/register` | visitor | `{ username, email, password }` | 201 `User`, session started | US-19, US-20 |
| POST | `/auth/login` | visitor | `{ identifier, password }` (username or email) | 200 `User`, session started | US-21 |
| POST | `/auth/logout` | logged-in | — | 204, session ended | US-21 |
| GET | `/auth/me` | anyone | — | 200 `User` (401 when logged out) | US-22, US-23 |
| PATCH | `/me` | logged-in | `{ username?, email?, currentPassword? }` | 200 `User` | US-24 |
| PUT | `/me/password` | logged-in | `{ currentPassword, newPassword }` | 204, other sessions ended | US-24 |
| GET | `/categories` | logged-in | — | 200 `Category[]` (current taxonomy) | US-12, US-30 |
| POST | `/cases` | logged-in | `{ description, preferences }` | 201 `Case` | US-01, US-02, US-05 |
| POST | `/cases/{caseId}/answers` | owner | `{ answers: FollowUpAnswer[] }` | 200 `Case` | US-02 |
| GET | `/cases` | logged-in | `?status&categoryId&page&pageSize` | 200 `Page<CaseSummary>`: own finished cases, newest first | US-30 |
| GET | `/cases/{caseId}` | owner | — | 200 `Case` | US-29, US-30 |
| DELETE | `/cases/{caseId}` | owner | — | 204 | US-31 |
| GET | `/admin/cases` | admin | `?user&categoryId&status&from&to&sort&order&page&pageSize` | 200 `Page<AdminCaseRow>` | US-15 |
| GET | `/admin/cases/{caseId}` | admin | — | 200 `Case` | US-15 |
| GET | `/admin/lawyers` | admin | `?name&email&city&categoryId&language&format&minRate&maxRate` | 200 `Lawyer[]` | US-11 |
| GET | `/admin/lawyers/{lawyerId}` | admin | — | 200 `Lawyer` | US-11 |
| POST | `/admin/lawyers` | admin | `LawyerInput` | 201 `Lawyer` | US-11, US-12 |
| PUT | `/admin/lawyers/{lawyerId}` | admin | `LawyerInput` | 200 `Lawyer` | US-11, US-12 |
| GET | `/admin/taxonomy` | admin | — | 200 `{ version, categories }` | US-13 |
| POST | `/admin/taxonomy/categories` | admin | `{ id, name }` | 201 `{ version, category }` | US-13 |
| PUT | `/admin/taxonomy/categories/{categoryId}` | admin | `{ name }` | 200 `{ version, category }` | US-13 |
| DELETE | `/admin/taxonomy/categories/{categoryId}` | admin | — | 200 `{ version }` (409 if in use) | US-13 |
| GET | `/admin/metrics/evaluation-runs` | admin | — | 200 `EvaluationRunSummary[]`, newest first | US-16, US-28 |
| GET | `/admin/metrics/evaluation-runs/{runId}` | admin | — | 200 `EvaluationRun` | US-16, US-28 |

### 5.5 Mock server behaviour

- **Storage:** one JSON object in `localStorage` under `mock_db`: `{ version, users, sessions, taxonomyVersion, categories, lawyers, cases, evaluationRuns }`. Seed it on first load, or when `version !== MOCK_DB_VERSION`.
- **Passwords:** stored only as SHA-256 hashes made with Web Crypto. This is for the mock only; the real server will use Argon2id or bcrypt. Never store plain text.
- **Validation:** re-validate every request with the same rules as the forms (share the zod schemas). Also check uniqueness and a built-in list of about 30 common or leaked passwords (e.g. `password`, `iloveyou`, `sunshine`, `princess`, `qwertyui`, `asdfghjk`, `abcdefgh`, `jelszavam`, `szeretlek`).
- **Access:** enforce every rule in 5.2 on every request, whatever the pages do (US-18, US-26, US-27, US-29).
- **Sessions:**
  - Logout deletes the session (US-21).
  - A password change deletes all of that user's other sessions (US-24).
  - A failed registration creates no user and no session (US-20).
- **Lists** never contain unfinished cases (`status: null`) or deleted cases (US-15, US-31).
- **Categorization** doesn't analyse the text. Outcomes are fixed and chosen in the developer panel (5.6). Rule-based (US-09) and AI (US-35) categorization use the same response shape, so the UI never needs to know which mode ran.
  - **Follow-up rounds (US-02):** if the scenario needs another round and fewer than `MAX_FOLLOW_UP_ROUNDS` rounds have been asked, return the next round's questions as `pendingQuestions`, with `status: null`. Return at most `MAX_QUESTIONS_PER_ROUND` questions per round. Store all questions and answers with the case.
  - **Still missing information after the last allowed round:** set `status: 'uncategorized'` and `uncategorizedReason: 'max_rounds_reached'`.
  - **Categorized:**
    - The category is `FIXED_CATEGORY_ID`, or the first current category if that one was removed.
    - Store a `{ id, name }` snapshot and the current taxonomy version.
    - Attach the first N lawyers of `FIXED_RECOMMENDATION_LAWYER_IDS`, in that order. N is chosen in the panel and never exceeds `MAX_RECOMMENDATIONS`.
  - **Lawyer data:** store lawyer IDs on the case and fill in the current lawyer data whenever a case is returned, so admin edits show up immediately (US-11). The fixed results may not match the preferences typed in; that's expected in the mock.
  - **`matchedCriteria` (US-07):**
    - First `Szakterület: <category name>`.
    - Then one item per filled-in preference, with the client's value: `Város: Budapest`, `Nyelv: magyar, angol`, `Konzultáció: online` / `személyes` / `online vagy személyes`, `Óradíj: legfeljebb 25 000 Ft`.
    - Leave out blank preferences.
  - **`summary` (US-07):** one sentence: `"{lawyer name} megfelel az Ön által megadott összes feltételnek; szakterülete: {category name}."`
- **Fixed follow-up questions:**
  - Round 1:
    - `r1-1`, date: "Mikor kezdődött a probléma?"
    - `r1-2`, single_choice: "Ki a másik fél az ügyben?" (Magánszemély / Cég / Hatóság vagy intézmény / Egyéb)
    - `r1-3`, yes_no: "Van szó pénzösszegről az ügyben?"
    - `r1-4`, short_text: "Melyik településen történt az eset?"
    - `r1-5`, yes_no: "Van írásos szerződés vagy más dokumentum az ügyben?"
  - Round 2:
    - `r2-1`, single_choice: "Mekkora összegről van szó?" (100 000 Ft alatt / 100 000 – 1 000 000 Ft / 1 000 000 Ft felett / Nem tudom)
    - `r2-2`, short_text: "Mit szeretne elérni az ügyben?"

### 5.6 Developer panel

The panel is shown only while `USE_MOCK_API` is true. A small floating "Dev" button in the bottom-right corner opens it. Settings persist in `localStorage` (`mock_dev_scenario`) and apply to the next screening.

- **Outcome:** Categorized immediately (default) · 1 follow-up round, then categorized · 2 follow-up rounds, then categorized · Still missing info after the last round → uncategorized · Not supported → uncategorized · Invalid AI answer → uncategorized.
- **Matching lawyers:** 3 (default) · 2 · 1 · 0.
- **Read-only info:** the current `CATEGORIZATION_MODE`, and the demo accounts with their passwords.
- **Reset demo data:** wipes `mock_db`, reseeds, logs out and reloads.

### 5.7 Seed data

**Taxonomy**, current version **2** (identifier → name):

| Identifier | Name |
|---|---|
| `berleti_jog` | Bérleti jog |
| `munkajog` | Munkajog |
| `csaladjog` | Családjog |
| `fogyasztovedelem` | Fogyasztóvédelem |
| `oroklesi_jog` | Öröklési jog |
| `ingatlanjog` | Ingatlanjog |
| `szerzodesi_jog` | Szerződési jog |
| `buntetojog` | Büntetőjog |

**Users:**

| Username | Email | Role | Password |
|---|---|---|---|
| demo_admin | admin@example.com | admin | vizimolnar |
| demo_client | kliens@example.com | client | kekfecske |
| demo_client2 | kliens2@example.com | client | zoldalma |

**Lawyers** (fictional):

| ID | Name | Email | Areas of expertise | City | Languages | Formats | Rate (Ft/h) |
|---|---|---|---|---|---|---|---|
| lawyer-01 | dr. Kovács Anna | kovacs.anna@example.com | berleti_jog, ingatlanjog | Budapest | hu, en | online, in_person | 18000 |
| lawyer-02 | dr. Nagy Péter | nagy.peter@example.com | berleti_jog, szerzodesi_jog | Budapest | hu, de | online | 22000 |
| lawyer-03 | dr. Szabó Eszter | szabo.eszter@example.com | berleti_jog, fogyasztovedelem | Debrecen | hu | online, in_person | 15000 |
| lawyer-04 | dr. Tóth Gábor | toth.gabor@example.com | munkajog | Budapest | hu, en | in_person | 30000 |
| lawyer-05 | dr. Horváth Judit | horvath.judit@example.com | munkajog, szerzodesi_jog | Szeged | hu | online | 20000 |
| lawyer-06 | dr. Varga Zoltán | varga.zoltan@example.com | csaladjog | Pécs | hu, de | in_person | 17000 |
| lawyer-07 | dr. Kiss Katalin | kiss.katalin@example.com | csaladjog, oroklesi_jog | Budapest | hu, en, fr | online, in_person | 35000 |
| lawyer-08 | dr. Molnár László | molnar.laszlo@example.com | oroklesi_jog, ingatlanjog | Győr | hu, de | in_person | 25000 |
| lawyer-09 | dr. Németh Réka | nemeth.reka@example.com | fogyasztovedelem | Miskolc | hu | online | 14000 |
| lawyer-10 | dr. Farkas Balázs | farkas.balazs@example.com | buntetojog | Budapest | hu, en | in_person | 45000 |
| lawyer-11 | dr. Balogh Ildikó | balogh.ildiko@example.com | buntetojog, csaladjog | Debrecen | hu, ro | online, in_person | 28000 |
| lawyer-12 | dr. Papp Tamás | papp.tamas@example.com | ingatlanjog, szerzodesi_jog | Szeged | hu, sk | online | 24000 |
| lawyer-13 | dr. Lakatos Mária | lakatos.maria@example.com | munkajog, fogyasztovedelem | Pécs | hu, en | online | 19000 |
| lawyer-14 | dr. Takács Dávid | takacs.david@example.com | szerzodesi_jog | Budapest | hu, en, es | online, in_person | 40000 |
| lawyer-15 | dr. Juhász Orsolya | juhasz.orsolya@example.com | oroklesi_jog | Miskolc | hu, uk | in_person | 16000 |
| lawyer-16 | dr. Mészáros Ádám | meszaros.adam@example.com | berleti_jog | Győr | hu, it | online | 21000 |

**Cases.** All are owned by `demo_client`. `demo_client2` has none, so the empty state can be seen.

1. **2026-10-05**
   - Description: "Tavaly ősszel albérletbe költöztem Budapesten, de a főbérlő most egyik napról a másikra fel akarja mondani a szerződést, és a kauciót sem akarja visszaadni."
   - Preferences: languages `hu`, format online, max 25 000 Ft, city blank.
   - Round 1 answered: `r1-1` 2025-10-01, `r1-2` Magánszemély, `r1-3` yes, `r1-4` Budapest, `r1-5` not answered.
   - Result: categorized as Bérleti jog, taxonomy version 2, recommendations lawyer-01, lawyer-02, lawyer-03.
2. **2026-09-28**
   - Description: "A munkáltatóm három hónapja nem fizeti ki a túlóráimat, és most azzal fenyeget, hogy elbocsát, ha szóvá teszem."
   - Preferences: city Sopron, max 10 000 Ft.
   - No follow-up questions.
   - Result: categorized as Munkajog, version 2, no matching lawyers.
3. **2026-09-15**
   - Description: "Szeretném tudni, hogyan jelenthetek be szabadalmat egy saját fejlesztésű konyhai eszközre."
   - No preferences.
   - Result: uncategorized, `not_supported`.
4. **2026-09-02**
   - Description: "A szomszéd fájának ágai átlógnak a telkemre, és a lehulló ágak megrongálták az autómat."
   - Preferences: city Szeged.
   - Result: uncategorized, `invalid_ai_answer`.

**Evaluation runs.** The test set has 40 labelled examples, 5 per category. The "correct per category" column follows the order of the taxonomy table above.

| Run | Date | Mode | Taxonomy version | Correct per category | Overall |
|---|---|---|---|---|---|
| run-1 | 2026-09-15 | rule_based | 1 | 4, 4, 3, 4, 3, 3, 3, 4 | 28/40 = 70.0% |
| run-2 | 2026-09-29 | ai | 1 | 5, 4, 5, 4, 4, 4, 4, 4 | 34/40 = 85.0% |
| run-3 | 2026-10-06 | ai | 2 | 5, 5, 5, 4, 4, 4, 4, 4 | 35/40 = 87.5% |

In each confusion matrix, every row sums to 5 and the diagonal equals the correct count. Put wrong predictions in a plausible neighbouring category or in the "Nem kategorizált" column. Plausible neighbours: Bérleti jog ↔ Ingatlanjog, Szerződési jog ↔ Fogyasztóvédelem, Családjog ↔ Öröklési jog, Munkajog ↔ Szerződési jog.

## 6. Layout, navigation and access

### 6.1 Menubar (every page)

- **Left:** `appConfig.APP_NAME`, linking to `/`.
- **Visitors** see only "Regisztráció" and "Bejelentkezés": no profile button, no "Admin" (US-22). When either is clicked, pass the current page as `returnTo` (US-20).
- **Logged-in users** don't see "Regisztráció" or "Bejelentkezés" (US-23). Admins see "Admin" (→ `/admin`) (US-25); clients don't (US-26).
- **Profile button:** person icon + username (US-23).
  - Hovering opens a dropdown with "Ügyeim" (→ `/cases`), "Profil szerkesztése" (→ `/profile`) and "Kijelentkezés".
  - It stays open while the pointer is over the button or the menu (allow about 150 ms to cross the gap).
  - It closes when the pointer leaves, on a click elsewhere, or when an option is chosen.
  - It only needs to work with a mouse; a simple custom menu without a portal is fine.

### 6.2 Footer

On every page: a link "Adatvédelmi tájékoztató" (→ `/privacy`).

### 6.3 Routes and guards

| Path | Page | Visitor | Client | Admin |
|---|---|---|---|---|
| `/` | Start page | ✓ | ✓ | ✓ |
| `/privacy` | Privacy policy | ✓ | ✓ | ✓ |
| `/register`, `/login` | Registration, login | ✓ | → `/` | → `/` |
| `/screening`, `/screening/:caseId` | Screening | → `/register?from=screening` | ✓ | ✓ |
| `/cases`, `/cases/:caseId`, `/profile` | My cases, case detail, profile | → `/login?returnTo=…` | ✓ | ✓ |
| `/admin`, `/admin/*` | Admin pages | → `/login?returnTo=…` | Access denied | ✓ |
| anything else | Not found | ✓ | ✓ | ✓ |

Admin sub-routes: `/admin/taxonomy`, `/admin/lawyers`, `/admin/lawyers/new`, `/admin/lawyers/:lawyerId`, `/admin/cases`, `/admin/cases/:caseId`, `/admin/metrics`.

Guards are only for convenience; the mock enforces the same rules on every request (US-26, US-27). Admin pages show a spinner, never admin content, until the user's role is known.

### 6.4 Access denied and Not found

- **Access denied** (US-27, US-28) is rendered at the requested address when a logged-in non-admin opens an admin page, or when any request returns 403.
  - Heading: "Hozzáférés megtagadva"
  - Text: "Ehhez az oldalhoz nincs jogosultsága."
  - Button: "Vissza a kezdőlapra"
- **Not found** (US-29) is used for unknown addresses and every 404 response, including other people's cases. It must reveal nothing about whether a case exists.
  - Heading: "Az oldal nem található"
  - Text: "A keresett oldal nem létezik."
  - Button: "Vissza a kezdőlapra"

## 7. Pages

### 7.1 Start page (placeholder) — US-18

A placeholder hero with:
- the app name;
- one placeholder paragraph: "Ide kerül a kezdőlap szövege.";
- a primary button "Felmérés indítása" (→ `/screening`; the guard sends visitors to registration).

### 7.2 Privacy policy (placeholder)

Title "Adatvédelmi tájékoztató" and one placeholder paragraph: "Ide kerül az adatvédelmi tájékoztató szövege."

### 7.3 Registration — US-18, US-19, US-20

- **Banner:** with `?from=screening`, show at the top: "A jogi problémafelmérő szolgáltatás használatához kérjük, regisztráljon vagy jelentkezzen be." (US-18)
- **Fields:** Felhasználónév, E-mail-cím, Jelszó, Jelszó megerősítése. There is no role field; new accounts are always clients.
- **Rules,** checked on blur and on submit, and again by the mock:
  - Username: 8–30 characters; only `a–z`, `A–Z`, `0–9` and `_`; unique.
  - Email: valid format; unique.
  - Password: 8–12 characters; only lowercase `a–z`; no composition rules. It's rejected if it's on the common/leaked list, or if it contains the username, the part of the email before `@`, or the site name (see decision 13). The message says why.
  - The confirmation must match.
- **Strength meter:** under the password, live. Map the zxcvbn score 0–4 to a coloured bar and a label: Nagyon gyenge, Gyenge, Közepes, Erős, Nagyon erős.
- **Show/hide toggle** (eye icon) on both password fields. Pasting is allowed.
- **Errors:** each appears under its field and says what's wrong and how to fix it. The other fields keep their values. Example texts:
  - "A felhasználónév 8–30 karakter hosszú lehet, és csak betűt (a–z, A–Z), számjegyet és aláhúzásjelet (_) tartalmazhat."
  - "Ez a felhasználónév már foglalt."
  - "Ezzel az e-mail-címmel már regisztráltak."
  - "Adjon meg érvényes e-mail-címet, például nev@example.com."
  - "A jelszó 8–12 karakter hosszú legyen."
  - "A jelszó csak az angol ábécé kisbetűit (a–z) tartalmazhatja; nagybetű, ékezetes betű, szám, szóköz és írásjel nem megengedett."
  - "Ez a jelszó túl gyakori vagy kiszivárgott jelszavak listáján szerepel, válasszon másikat."
  - "A jelszó nem tartalmazhatja a felhasználónevét."
  - "A jelszó nem tartalmazhatja az e-mail-címét."
  - "A jelszó nem tartalmazhatja az oldal nevét."
  - "A két jelszó nem egyezik."
- **Login link:** a clearly visible "Már regisztrált? Jelentkezzen be" button (→ `/login`, keeping `from`/`returnTo`).
- **Success (US-20):**
  - The session starts at once.
  - Cache the user so the menubar switches immediately.
  - Show the toast "Üdvözöljük, {username}! Sikeresen regisztrált."
  - Then go to `/screening` if `from=screening`, else to `returnTo`, else to `/`.

### 7.4 Login and logout — US-18, US-21, US-27

- **Fields:** "Felhasználónév vagy e-mail-cím" and "Jelszó" (with a show/hide toggle).
- **Failure:** any failure shows the same message, also for non-existent users: "Hibás felhasználónév/e-mail-cím vagy jelszó."
- **Success:** go to `/screening` if `from=screening`; else to `returnTo` if present; else to `/`. A client sent back to an admin page sees Access denied there.
- **Registration link:** "Még nincs fiókja? Regisztráljon" (→ `/register`, keeping `from`/`returnTo`).
- **Logout** (from the profile menu): call `/auth/logout`, clear all cached data, go to `/`.

### 7.5 Screening — US-01, US-02, US-04, US-05, US-09, US-35

**`/screening`: description and preferences on one page**

- **Description (US-01):**
  - A textarea labelled "Írja le a problémáját a saját szavaival", with a live counter "{n} / 5000". It stops accepting input at 5,000 characters.
  - If the text is shorter than 30 characters on submit, don't submit. Show this friendly message with an example: "Kérjük, írja le egy kicsit részletesebben a problémáját (legalább 30 karakter). Például: »2025 márciusában lakást béreltem Budapesten. Kiköltözéskor a főbérlő nem adta vissza a 300 000 Ft kauciót, arra hivatkozva, hogy ki kell festeni a falakat. Írásos bérleti szerződésünk van.«"
- **Preferences** go below the description (US-05).
  - Heading: "Elvárások az ügyvéddel kapcsolatban"
  - Hint: "Egyik mező kitöltése sem kötelező. Ha egy mezőt üresen hagy, aszerint nem szűrünk."
  - Fields:
    - Város: free text.
    - Nyelv(ek): checkbox group from the fixed language list.
    - Konzultáció formája: a select with Online / Személyes / Mindkettő megfelel; starts empty.
    - Maximális óradíj (Ft): a text field for whole forints (decision 12).
- **Submit:** "Elküldés" → `POST /cases` → go to `/screening/{caseId}`. The button is disabled while sending.

**`/screening/:caseId`: follow-up questions or result**

- Loads the case; a 404 shows Not found.
- **While `pendingQuestions` is not null (US-02):**
  - Heading: "Néhány kiegészítő kérdés"
  - Text: "Néhány adat hiányzik ahhoz, hogy be tudjuk sorolni az ügyét. Bármelyik kérdést kihagyhatja."
  - Render each question by type:
    - single_choice → radio group;
    - yes_no → radio group "Igen" / "Nem";
    - date → date picker (Popover + Calendar, Hungarian locale);
    - short_text → text input, max 200 characters.
  - Each question has a "Kihagyom" button that clears its answer. Unanswered questions are sent as `null` and later shown as "Nem válaszolt", never as "Nem".
  - "Válaszok elküldése" → `POST /cases/{caseId}/answers` → show the next round or the result.
- **When `status` is set:** show the result block (7.6) with the buttons "Ügyeim" (→ `/cases`) and "Új ügy" (→ `/screening`). There is no retry.

### 7.6 Result block and recommendation cards — US-03, US-04, US-06, US-07, US-08, US-36

This block is shared by `/screening/:caseId` and the case detail page.

- **Categorized:** "Az ügy kategóriája: {category name}" (US-04), then the cards. With 0 recommendations, show "Nincs megfelelő ügyvéd." instead (US-06).
- **Uncategorized with `not_supported` or `max_rounds_reached`:** "Az ügye nem kategorizálható." (US-03)
- **Uncategorized with `invalid_ai_answer`:** "Érvénytelen válasz érkezett a mesterséges intelligenciától." (US-36)
- **Cards:** at most 3, in the returned order, with everything visible at once (US-08):
  - name, email (`mailto:` link), city, areas of expertise, languages, consultation formats, and hourly rate ("{rate} Ft/óra");
  - the ✓ list from `matchedCriteria`, with green check icons (US-07);
  - the one-sentence `summary`.
  - There is no choose button, and nothing is sent to the lawyer.

### 7.7 My cases — US-30, US-31

- **Header:** title "Ügyeim" and a button "Új ügy" (→ `/screening`).
- **Filters:** Státusz (Mind / Kategorizált / Nem kategorizált) and Kategória (Mind + the current categories).
- **Table:** newest first, 20 per page with pagination.
  - Columns: Létrehozva (date), Kategória ("—" if none), Státusz (badge).
  - Every row has a "Törlés" button with a trash icon.
  - Clicking a row opens `/cases/{caseId}`.
- **Empty states:**
  - No cases at all: "Még nincs ügye." with a button "Első felmérés indítása" (→ `/screening`).
  - No results for the filters: "Nincs a szűrésnek megfelelő ügy."
- **Delete (US-31):** a dialog "Biztos benne?" with "Igen" and "Nem". After "Igen", delete the case; the row disappears immediately and the toast "Az ügyet töröltük." appears.

### 7.8 Case detail — US-15, US-29, US-30, US-31

One component with two modes: owner (`/cases/:caseId`) and admin, read-only (`/admin/cases/:caseId`).

- **Header:** "Ügy részletei", the created date and a status badge. In owner mode, a "Törlés" button with the same confirmation; after deleting, go back to `/cases`.
- **"Problémaleírás":** the description exactly as submitted, with line breaks kept.
- **"Kiegészítő kérdések és válaszok":** each question with its answer. Dates use the Hungarian format, yes/no shows as Igen/Nem, and `null` shows as "Nem válaszolt". If there were no questions: "Nem volt kiegészítő kérdés."
- **"Elvárások":** Város, Nyelv(ek), Konzultáció formája, Maximális óradíj. Blank ones show "Nincs megadva".
- **"Eredmény":** the result block (7.6) with the recommendation cards.
- **Admin mode:**
  - adds the case number (full UUID) and the owner's username;
  - has no delete button and nothing editable;
  - has a back link to "Összes ügy".
- **Special cases:** an unfinished case opened here redirects to `/screening/{caseId}`. A case the user may not see shows Not found.

### 7.9 Edit profile — US-24

- **Title:** "Profil szerkesztése". Users see only their own profile; there is no user ID in the URL.
- **Section "Fiókadatok":** Felhasználónév and E-mail-cím, prefilled.
  - When the email differs from the saved one, show the required field "Jelenlegi jelszó".
  - The same rules apply as at registration.
  - "Mentés" → `PATCH /me` → toast "A módosításokat mentettük." The menubar shows the new username.
  - "Mégse" restores the saved values.
- **Section "Jelszó módosítása":** Jelenlegi jelszó, Új jelszó (with the strength meter), Új jelszó megerősítése. The registration rules apply.
  - "Mentés" → `PUT /me/password` → toast "A jelszót módosítottuk. A többi eszközön kijelentkeztettük."
  - "Mégse" clears the fields.
- Nothing is saved without "Mentés", and each error names its field.

### 7.10 Admin dashboard — US-10, US-25

Title "Adminisztráció" and four large link cards:
- "Taxonómia" (→ `/admin/taxonomy`)
- "Ügyvédi profilok létrehozása és szerkesztése" (→ `/admin/lawyers`)
- "Összes ügy" (→ `/admin/cases`)
- "Metrikák" (→ `/admin/metrics`)

Every admin sub-page has a back link to the dashboard.

### 7.11 Taxonomy — US-13

- "Jelenlegi verzió: {n}" at the top.
- **Table:** Azonosító, Név, and the actions "Átnevezés" and "Törlés".
- **"Új kategória" dialog:** Azonosító and Név, both required free text (Hungarian). The identifier must be unique.
- **Rename:** changes only the name; the identifier is read-only.
- **Delete:** confirm with "Biztos benne?". If the API returns 409, show "A kategória nem törölhető, mert a következő ügyvédekhez van rendelve:" followed by the affected lawyers' names, each linking to their edit page.
- After each successful change, the version number updates.

### 7.12 Lawyer profiles — US-11, US-12

- **List "Ügyvédi profilok"** with a button "Új ügyvéd".
  - Search and filters for every field:
    - Név, E-mail, Város: text, contains, case-insensitive;
    - Szakterület, Nyelv, Konzultáció formája: selects;
    - Óradíj: min–max (Ft).
  - Columns: Név, E-mail, Szakterületek, Város, Nyelvek, Konzultáció, Óradíj.
  - Clicking a row opens the edit page.
- **Create/edit form** (one component). All fields are required (US-12):
  - Név
  - E-mail-cím (valid format)
  - Szakterületek: checkboxes from the current taxonomy, at least one
  - Iroda helye (város)
  - Beszélt nyelvek: checkboxes from the fixed list, at least one
  - Konzultáció formája: checkboxes Online / Személyes, at least one
  - Óradíj (Ft): whole number greater than 0
- Saving with a missing or invalid field is blocked, and that field shows what's wrong. After saving: a toast, then back to the list.
- Changes apply immediately everywhere lawyer data is shown, including existing recommendations (US-11).

### 7.13 All cases — US-15

- **Title:** "Összes ügy".
- **Filters:** Felhasználó (username or email, contains, case-insensitive), Kategória, Státusz (Kategorizált / Nem kategorizált), Dátumtól and Dátumig (date pickers).
- **Table:** 50 per page, with "Találatok száma: {total}".
  - Every column is sortable by clicking its header; the default is newest first.
  - Columns: Létrehozva, Ügyszám (full UUID), Felhasználó, Kategória, Státusz, Város, Nyelvek, Konzultáció, Max. óradíj.
  - The last four are the client's preferences; blank values show "—".
- Clicking a row opens `/admin/cases/{caseId}` (read-only).
- Deleted and unfinished cases never appear.

### 7.14 Metrics — US-16, US-28

- **Title:** "Metrikák". The page is view only: no test-set editing, no starting runs, no comparison of runs, and no cost or usage figures.
- **Runs table** (newest first): Dátum, Kategorizálási mód (Szabályalapú / AI-alapú), Taxonómia verzió, Tesztkészlet mérete, Összpontosság (%). Clicking a row selects it; the newest is selected at first.
- **Selected run:**
  - "Összpontosság" as a large percentage.
  - "Kategóriánkénti pontosság": a bar chart plus a table (Kategória, Helyes / Összes, Pontosság %).
  - "Tévesztési mátrix": rows are the valódi kategória, columns the becsült kategória, plus a "Nem kategorizált" column. Cells are shaded by count, with the diagonal highlighted.
- The page shows totals and averages only, never individual cases (US-29).

## 8. Out of scope: don't build

- Any real backend, database, auth provider, network calls, or server-side logging (US-04).
- The OpenAPI document and the Swagger UI page (US-17). They come later and will be based on section 5.
- Any way to create admins or change roles (US-14).
- Handling for failed requests or network errors beyond section 5.2. The developer will add it later.
- Phone or tablet layouts and a language switcher.
- Choosing a lawyer, deleting lawyers, restoring categories, and taxonomy history.
- Managing the test set, starting evaluation runs, comparing runs, and cost or usage metrics.
- Showing unfinished cases.

## 9. Before you finish, check these

1. A visitor clicks "Felmérés indítása" → the registration page shows the US-18 message → "Már regisztrált? Jelentkezzen be" → logging in as `demo_client` lands on `/screening`.
2. Registration rejects `jelszavam` (common), `Kekfecske` (uppercase) and any password containing the username. A valid password logs the user in at once, shows the welcome toast and switches the menubar.
3. A wrong password and an unknown username give the same message.
4. With the panel set to "2 follow-up rounds, then categorized", skip a question in each round. The result shows the category and three cards, with ✓ items only for filled-in preferences. The case appears in "Ügyeim", and its detail page shows "Nem válaszolt" for the skipped questions.
5. Panel outcomes give the right results:
   - "0 matching lawyers" → "Nincs megfelelő ügyvéd."
   - "Not supported" and "Still missing info…" → "Az ügye nem kategorizálható."
   - "Invalid AI answer" → the US-36 message.
   - The last three cases are listed as "Nem kategorizált".
6. A screening left on the question step doesn't appear in "Ügyeim" or "Összes ügy".
7. `demo_client2` sees the empty state, and opening one of `demo_client`'s case URLs shows the plain Not found page.
8. Deleting a case removes it from "Ügyeim" and "Összes ügy" at once.
9. A visitor opens `/admin/metrics` and is sent to login. `demo_admin` then lands on the metrics page; `demo_client` sees Access denied. Clients never see "Admin".
10. Removing "Bérleti jog" is blocked and lists its lawyers. Adding and then removing a new category raises the version each time.
11. Changing lawyer-01's city shows up on case 1's recommendation card.
12. "Összes ügy": every filter works, every column sorts, there are 50 rows per page, and the total count is shown.
13. Profile: changing the email requires the current password, and the password section uses the registration rules and the strength meter.
14. "Reset demo data" restores the seed data.
