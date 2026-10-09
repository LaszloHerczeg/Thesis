# User Stories — Legal Problem Screening & Lawyer Matching System

## How to read this document

Each **user story** describes one feature from the point of view of the person who benefits from it, in the form:

> **As a** [type of user], **I want** [some capability], **so that** [some benefit].

Under each story are **acceptance criteria** — concrete, testable conditions that must all be true before the story counts as finished. Stories are grouped into **epics** (a large body of work made up of several related stories), one epic per feature area.

Each story has a **priority** using the **MoSCoW** method:
- **Must** — the system does not work or fails its purpose without it
- **Should** — important, but the system is still usable without it
- **Could** — nice to have if time allows

Numbers such as "70%" or "10 seconds" are suggested starting values. They should be stored as configuration settings, not written directly into the code, so you can tune them later.

### Glossary

| Term | Meaning |
|---|---|
| **API** (Application Programming Interface) | A defined way for one piece of software to request something from another, e.g. your backend asking an AI provider to classify text. |
| **Authentication / Authorisation** | Authentication checks *who* you are (logging in). Authorisation checks *what you are allowed to do* once logged in (e.g. only admins may open the admin page). |
| **Command-line interface (CLI)** | A text-only way of running programs by typing commands into a terminal on the server, instead of clicking in a web page. A "CLI script" is a small program run this way. |
| **Confidence score** | A number between 0 and 1 (or 0–100%) expressing how sure the classifier is that its answer is correct. |
| **EXIF metadata** | Hidden information a camera or phone stores inside a photo, e.g. the GPS location where it was taken, the date and the device model. |
| **Epic** | A group of related user stories that together deliver one larger feature. |
| **GDPR** (General Data Protection Regulation) | The European Union's data protection law. It governs how personal data is collected, stored and processed. |
| **Hashing** | Turning a password into a scrambled fixed-length value that cannot be turned back into the password. Only the hash is stored, so a database leak does not reveal passwords. Argon2id and bcrypt are hashing methods designed for passwords. |
| **HTTP status codes 401 / 403** | Standard web response codes. **401 Unauthorized** means "you are not logged in"; **403 Forbidden** means "you are logged in, but not allowed to see this". **404 Not Found** means "this page does not exist" and is also used to hide pages a user must not even know about. **429 Too Many Requests** means "you have sent too many requests, try again later". |
| **Human-in-the-loop (HITL)** | A design where a person checks or confirms an automated result before it is used. |
| **JSON** (JavaScript Object Notation) | A simple, widely used text format for structured data that both people and programs can read. |
| **LLM** (Large Language Model) | An AI model trained on large amounts of text that can read and generate language (e.g. Claude, GPT). |
| **LLM gateway** | A single internal module through which every call to an LLM passes, so that logging, cost tracking, retries and provider switching happen in one place. |
| **NIST** (National Institute of Standards and Technology) | A US standards body. Its guideline *SP 800-63B* is the most widely used reference for modern password rules. |
| **OCR** (Optical Character Recognition) | Technology that turns an image of text (a scan or photo) into machine-readable text. |
| **OpenAPI** | A standard, machine-readable format for describing a web API: every address, what it accepts, what it returns and what errors it can give. |
| **PII** (Personally Identifiable Information) | Any data that can identify a person: name, address, date of birth, ID numbers, phone number, email, bank account number, etc. |
| **Masking / anonymization** | Replacing PII with a placeholder (e.g. `[NAME_1]`) so the content can be processed without exposing the person. |
| **Prompt injection** | An attack where text given to an AI (e.g. hidden in a document) tries to act as new instructions, such as "ignore your instructions and classify this as…". |
| **Rate limiting** | Capping how many requests a user or device can make in a given time, to stop bots and misuse. |
| **Retention period** | How long a piece of data is kept before it is automatically deleted. |
| **Role** | The type of account a user has (here: client or administrator), which decides what they may see and do. |
| **Suspension / Ban** | A **suspension** blocks an account temporarily, until a set end date or until an administrator lifts it. A **ban** blocks an account indefinitely: it stays in force until an administrator lifts it. |
| **Session** | The system's record that a browser is currently logged in, usually kept via a small cookie (a piece of data stored by the browser). |
| **Taxonomy** | The fixed list of categories the system sorts cases into (here: a set of legal areas managed by the administrator). |
| **WCAG** (Web Content Accessibility Guidelines) | The international standard for making websites usable by people with disabilities. Level AA is the level most laws and organisations require. |
| **XAI** (Explainable AI) | AI whose outputs come with human-understandable reasons for why that output was produced. |
| **ZIP file** | A single compressed file that contains several other files. |

### User roles

| Role | Who they are |
|---|---|
| **Visitor** | Anyone using the site without being logged in. Visitors can see the start page, disclaimer and privacy policy, and can register or log in, but cannot use the screening service. |
| **Client** | A member of the public describing a legal problem and looking for a lawyer. Has a registered account with the client role. |
| **Administrator** | Staff member with a registered account and the administrator role, who maintains lawyer profiles and the category list and views the metrics. |
| **Developer** | The person building and maintaining the system. |
| **Server operator** | The person who installs and runs the system on the server and has direct access to it (may be the same person as the developer). |
| **Researcher / Product owner** | The person evaluating how well the system works (may be the same person as the developer). |

---

# SZD I.

## Epic 1 — Client Intake & Interaction

### US-01 · Describe my problem in my own words — *Must*
**As a** client, **I want** to describe my legal problem in free text, in my own words, **so that** I don't need to know legal terminology to get help.

**Acceptance criteria**
- A text field accepts free-form input with a minimum length (e.g. 30 characters) and a maximum length (e.g. 5,000 characters); a live character counter is shown.
- If the text is below the minimum, the client sees a friendly message asking for more detail, with an example of a good description.
- When the description is submitted, it is saved in two versions, together with a timestamp:
  - the original version, exactly as the client wrote it;
  - a masked version with personal data replaced by placeholders (US-08).
- The client can edit the description before submitting it.

### US-02 · Answer follow-up questions — *Must*
**As a** client, **I want** the system to ask me targeted follow-up questions about information I left out, **so that** my case is understood correctly without me having to guess what matters.

**Acceptance criteria**
- After submission, the system identifies missing key information (e.g. dates, the other party, location/jurisdiction, whether money is involved) and asks about it.
- Questions are structured (multiple choice, yes/no, date picker, or short text) rather than open-ended where possible.
- No more than a configurable number of questions per round (e.g. 5), and no more than a configurable number of rounds (e.g. 2), to avoid tiring the client.
- The client can skip any question; skipped questions are recorded as "not answered", not as a negative answer.
- Answers are stored in the same two versions (US-08). The masked version is used as input to classification (US-11).

### US-03 · Be told honestly when my problem can't be categorized — *Must*
**As a** client, **I want** the system to tell me clearly when it cannot confidently categorize my issue, **so that** I am not misled by a guess.

**Acceptance criteria**
- If confidence is still below the threshold after clarification, or the problem falls outside all categories, the system shows an explicit message such as: "We couldn't confidently match your problem to one of our legal areas."
- The message suggests a next step (e.g. contact a general legal advice service, or browse all lawyers manually).
- The case is flagged as "unclassified" in the audit module (US-31) for later review.

---

## Epic 2 — Classification & Recommendation Engine

### US-4 · Get my problem classified into a legal area — *Must*
**As a** client, **I want** my problem to be sorted into the right legal area, **so that** I know what kind of lawyer I need and how sure the system is.

**Acceptance criteria**
- Classification uses the client's description, follow-up answers and confirmed document fields as input.
- The output is exactly one category from the current taxonomy.
- If confidence is below the threshold, US-03 / US-04 apply instead of showing results.
- The input, output, confidence, model used, and response time are logged.

### US-5 · State my preferences for a lawyer — *Should*
**As a** client, **I want** to state my preferences (location, language, online or in-person consultation, budget / fee model, how soon I need an appointment), **so that** the recommendations fit my practical situation.

**Acceptance criteria**
- The client can set: location (city or region, plus maximum distance for in-person), language(s), consultation format (online / in-person / either), preferred fee model (e.g. fixed fee, hourly, free first consultation), and urgency.
- Each preference can be marked as "required" or "nice to have".
- Sensible defaults are pre-filled (e.g. the language the client is using the site in).

### US-6 · Receive exactly three lawyer recommendations — *Must*
**As a** client, **I want** to receive the three best-matching lawyer profiles, **so that** I have a short, manageable choice instead of a long list.

**Acceptance criteria**
- Matching compares the case category and the client's preferences against lawyer profiles on six criteria: specialty, location, language, consultation format, availability and fee model.
- Specialty is a required match: a lawyer who does not cover the case's category is never recommended.
- Each criterion has a configurable weight; lawyers are ranked by weighted score.
- Only active profiles (see US-19) are considered.
- Maximum of three profiles are shown. If fewer than three lawyers match all required preferences, only the matching profiles are shown
- The same input with the same lawyer data always produces the same result (deterministic ranking; ties broken by a fixed rule).

### US-7 · Understand why each lawyer was recommended — *Could*
**As a** client, **I want** to see why each lawyer was recommended, **so that** I can trust the recommendation and choose between the three.

**Acceptance criteria**
- Each recommended profile shows a per-criterion breakdown, e.g. ✓ Specialty: tenancy law · ✓ Speaks Hungarian · ✓ Online consultations · ✗ 45 km away (you asked for 20 km).
- A one-sentence plain-language summary explains the main reason for the recommendation.

### US-8 · See the chosen lawyer's contact details — *Could*
**As a** client, **I want** to see the contact details of the lawyer I pick from the three recommendations, **so that** I can get in touch with them directly.

**Acceptance criteria**
- Each of the three recommended profiles has a "Choose this lawyer" button. Contact details are not shown before a lawyer is chosen.
- After choosing, the client sees the lawyer's name, office address, phone number and email address, plus a website or booking link if the profile has one.
- The page also repeats the lawyer's consultation formats and fee model, so the client knows what to expect when they call.
- The phone number and email address are clickable links (tapping them opens the phone's dialler or the email program).
- The client can go back to the three recommendations and choose a different lawyer.
- The client's own details are **not** sent to the lawyer; the client decides whether and how to make contact.
- The short disclaimer (US-05) stays visible, including a note that the platform does not guarantee the lawyer will take the case.
- If the lawyer was deactivated after the recommendations were shown, the client sees a message saying so and is asked to choose another recommendation. A button is available to re-do the the recommendation.
- The system records which lawyer was chosen, which position they had in the list (1st, 2nd or 3rd), and when. Every change of choice is recorded too. This feeds the task completion metric (US-33) and shows how often clients pick the top-ranked lawyer.

### US-9 · Rule-based Classification — *Must*
**As a** client, **I want** the system to classify my case, **so that** I can find the best lawyer for me.

**Acceptance criteria**
- The system chooses a field according to the data extracted from the client's description and documents following the classification rules.
- The output is sent to the same interface as the LLM-based classification.
- If the case can not be classified, the system gives appropriate answer (e.g. "Not supported")
- If the system needs more information, the system gives appropriate answer (e.g "More information needed")

### US-35 . AI Classification - *Must*
**As a** client, **I want** the system to classify my case **so that** I can find the most suitable lawyer.
**Acceptance criteria**
- The extracted information from the uploaded documents is sent to an LLM.
- The LLM is asked to send the category back in a fixed format.
- The answer is always checked (US-35).
- All important information is logged (US-39) and available for the administrator (US-37).

### US-36 · Check that the AI's answer is a real category — *Must*
**As a** client, **I want** the system to check the AI's classification before it is used, **so that** I am never shown a category that doesn't exist or a broken result.

**Acceptance criteria**
- The LLM is asked to answer in a fixed JSON format containing only the category identifier.
- Before the answer is used, the system checks that:
  - the answer can be read in the expected format and has all required fields;
  - the category identifier matches an **active** category in the current taxonomy (US-21). The check compares identifiers, not category names as free text;
- If any check fails, the request is repeated once, with a reminder of the required format.
- If the second answer is also invalid, the case is treated as "could not be categorised" (US-04). The client never sees an invalid answer.
- Every invalid answer is logged with the reason (unknown category, wrong format, missing field or value out of range) and counted in the error statistics (US-32).


---

## Epic 3 — Administration & Management I.

### US-10 · Access the admin area securely — *Must*
**As an** administrator, **I want** a login-protected admin dashboard, **so that** only authorised staff can change lawyer data and categories.

**Acceptance criteria**
- Only users with the administrator role can access the admin interface (access rules in detail: US-43 to US-46).
- Every change made in the admin area is logged with who made it, when, and what changed (before/after values).

### US-11 · Create and edit lawyer profiles — *Should*
**As an** administrator, **I want** to create, edit and view lawyer profiles, **so that** the recommendation engine always works from accurate data.

**Acceptance criteria**
- Profiles can be created, edited, searched and filtered by any schema field.
- Changes take effect in recommendations immediately after saving.

### US-12 · Enforce a structured profile schema — *Should*
**As an** administrator, **I want** every lawyer profile to follow the same structured format, **so that** matching is fair and reliable across all lawyers.

**Acceptance criteria**
- Required fields: name, contact details (phone number, email address; website or booking link optional), areas of expertise (one or more, chosen from the taxonomy), office location (address and coordinates), languages spoken, consultation formats (online / in-person), availability (e.g. next free slot or "accepting new clients" plus typical waiting time), and pricing model.
- Areas of expertise and languages are chosen from fixed lists, not typed freely, to avoid spelling variants.
- A profile cannot be saved if any required field is missing or invalid; the form shows which field is wrong.

### US-13 · Manage the legal category taxonomy — *Should*
**As an** administrator, **I want** to manage the list of legal categories, **so that** the system's categories match the lawyers and case types we actually handle.

**Acceptance criteria**
- Each category has a name, a plain-language client-facing description, and example problems, each entered in English, Hungarian and German (US-60).
- A category that is still assigned to active lawyers cannot be removed until those lawyers are reassigned; the admin is shown which lawyers are affected.
- Changes to the taxonomy are versioned, and each classification records which taxonomy version it used (so accuracy can be compared fairly over time).

### US-14 · Create the first administrator with a server-side script — *Must*
**As a** server operator, **I want** to create the first administrator account with a command-line script on the server, **so that** the system can be set up without any admin-creation function being exposed on the web.

**Acceptance criteria**
- The script is run in a terminal on the server. Username and email address are given in the command.
- The script then asks for the password twice.
  - Nothing is shown on screen while it is typed.
  - The password is never given as part of the command itself, because commands are saved in the terminal's history.
- If the two passwords don't match, the script says so and asks again.
- The same rules apply as at registration (US-36) for the username, the email address format and the password.
- If any rule fails, the script prints a clear error and creates nothing.
- The script refuses to create the account if the username or the email address is already in use.
- The password is stored only as a hash.
- The new account gets the administrator role and can log in on the website straight away.
- There is no web page, address or server function that creates administrators. The script can only be run by someone with access to the server.
- Each administrator created this way is logged with the username and the time, never the password. The script prints a confirmation message.

### US-15 · Browse and filter all cases as an administrator — *Could*
**As an** administrator, **I want** a "Cases" menu item that lists all existing cases with filters, **so that** I can review cases, find ones that could not be categorised, and check how the system is being used.

**Acceptance criteria**
- Logged-in administrators see "Cases" on the menubar (US-43). The page follows the same access rules as the admin area: unreachable for visitors (US-45) and for non-admins (US-46).
- The list shows one row per case, with:
  - the creation date;
  - the case number;
  - the username of the client who created it;
  - the category (plain language with the legal term below);
  - the confidence level;
  - the status;
  - the chosen lawyer, if any;
  - the date of the last change.
- The list can be filtered by:
  - the user who created the case (search by username or email address);
  - category;
  - status (including *Could not be categorised*, US-04);
  - date range;
  - confidence level (e.g. only low-confidence cases);
  - chosen lawyer;
  - whether documents were uploaded.
- Several filters can be combined, and a "Clear filters" button resets them.
- The list can be sorted by any column and shows e.g. 50 cases per page, with the total number of matching cases.
- Clicking a case opens it in the admin view described in US-48. Personal data is masked and original files are not shown. Every opening is logged.
- The admin view is read-only: administrators cannot change what a client entered or the results of a case.
- Cases deleted by their owner (US-49, US-56) do not appear.

---

## Epic 4 — Architecture & Auditing I.

### US-16 · Measure classification accuracy — *Must*
**As a** researcher, **I want** to measure how accurately the system classifies cases, **so that** I can prove it works and track whether changes improve or worsen it.

**Acceptance criteria**
- A labelled test set (example problems with the correct category, decided by a person) can be stored and run against the classifier.
- The system reports overall accuracy, accuracy per category, and a confusion matrix (a table showing which categories get mixed up with which).
- It reports how often the low-confidence fallback was triggered and how often the confidence score matched reality (i.e. whether high-confidence answers really are right more often).
- Each evaluation run is saved with the date, model version and taxonomy version so results can be compared.

### US-17 · Describe the API in an OpenAPI specification — *Must*
**As a** developer, **I want** the server's whole API described in an OpenAPI specification, **so that** the frontend and backend agree on exact data formats, and the API can be tested and documented automatically.

**Acceptance criteria**
- An OpenAPI 3 document describes every API endpoint the website uses. An endpoint is a single address on the server that the website calls, such as "create a case" or "log in". This covers:
  - accounts and log-in, including password reset;
  - screening, uploads, cases and recommendations;
  - the data download;
  - admin functions, cases, logs and metrics.
- For each endpoint, the document states:
  - its address and method (e.g. GET for reading data, POST for sending new data);
  - its inputs and response formats;
  - the errors it can return (e.g. 400, 401, 403, 404, 429);
  - which role may use it: visitor, client or administrator.
- Shared data structures, such as case, category, lawyer profile and recommendation, are defined once and reused.
- The specification is kept in sync with the code: it is either generated from the code, or automated tests check that real API responses match it. The build fails if they don't match.
- An interactive documentation page (e.g. Swagger UI) is available during development. In production it is switched off or available to administrators only.
- The specification has a version number that is increased whenever the API changes.
- The server-side scripts (US-22, US-23, US-24) are not part of the API. The specification confirms that no endpoint creates, promotes or demotes administrators.

### US-38 · Route all AI calls through one gateway — *Must*
**As a** developer, **I want** every LLM call to go through a single LLM gateway, **so that** logging, cost tracking, PII protection, error handling and provider changes are handled in one place.

**Acceptance criteria**
- No module calls an LLM provider directly; code review or an automated check enforces this.
- The gateway refuses to send text that has not passed through PII masking (US-08).
- For each call it records: which module called it, which user's case it was for, model name, input and output token counts (tokens are the small chunks of text LLMs are billed by), cost, response time, and success or error.
- It applies a timeout and a limited number of retries on temporary errors.
- If all retries fail, the site shows a clear error message, e.g. "The analysis could not be completed right now. Please try again."
  - Everything the client has entered or uploaded is kept.
  - A "Try again" button repeats the failed step without the client having to re-enter anything.
  - The failure is logged (US-32).
- The LLM provider and model can be switched through configuration without code changes in other modules.

---

## Epic 5 — User Accounts & Access Control I.

### US-18 · Require registration or log-in to use the screening service — *Should*
**As a** visitor, **I want** to be told clearly that I need an account to use the legal screening service, and be taken to the registration page, **so that** I know what to do next and my data is always linked to an account I control.

**Acceptance criteria**
- The screening service covers every step from describing the problem (US-01) to seeing the chosen lawyer's contact details (US-16), and is available only to logged-in users.
- When a visitor tries to start the screening, or opens any screening page address directly, they are redirected to the registration page (US-36).
- A message at the top of the registration page explains why: "To use the legal screening service, please register or log in."
- If the visitor already has an account, they can switch to the log-in page with the "Already registered? Log in" button (US-36).
- After registering (with automatic log-in, US-37) or logging in, the user is taken straight to the start of the screening, not to the home page.
- The check happens on the server. Requests to the screening functions from someone who isn't logged in are refused with a 401 response, even if they bypass the pages.
- If a session expires during the screening, the user is asked to log in again. Afterwards they continue where they left off, and anything they had already saved is kept.
- The start page, disclaimer, privacy policy and language button stay available to visitors.
- The message appears in the visitor's chosen language (US-59).

### US-19 · Register an account with a secure password — *Should*
**As a** visitor, **I want** to register an account with a secure password, **so that** my cases are saved to my account and protected from other people.

**Acceptance criteria**
- The sign-up form asks for username, email address, password and password confirmation, plus the consent checkbox from US-53.
- The username is unique, 3–30 characters, letters, numbers and underscores only. The email address is unique and in a valid format.
- The email address is checked against the banned-email list (US-27).
  - The list contains the email addresses of currently banned accounts, and hashes of the addresses of banned accounts that have since been deleted.
  - Before comparing, the address is normalised: spaces are trimmed and capital letters are made lower-case, so "Name@Mail.com " and "name@mail.com" count as the same address.
  - If the address is on the list, the account is not created. The visitor sees: "This email address cannot be used to register. Please contact us if you think this is a mistake."
  - Each blocked attempt is logged with the email address, the time and the IP address.
- Password rules follow modern practice based on NIST guidance (SP 800-63B):
  - Minimum length of 8 characters. The limit is a configurable setting, so it can be raised later without changing the code.
  - Maximum length of at least 64 characters. All characters are allowed, including spaces and accented letters (á, ő, ü, ß).
  - **No** forced composition rules such as "must contain an uppercase letter, a number and a symbol". These make passwords harder to remember without making them much stronger.
  - The password is rejected if it appears in a list of known leaked passwords or common passwords, or if it contains the username, the email address or the site's name. The client is told *why* it was rejected.
- A live strength indicator shows how strong the password is while it is typed.
- A "show password" toggle is available, and pasting is allowed so password managers work.
- Passwords are stored only as hashes (Argon2id or bcrypt), never as plain text.
- Every error message names the field that is wrong and how to fix it, and the form keeps everything else the visitor typed.
- The registration page has a clearly visible "Already registered? Log in" button that takes the visitor to the log-in page (US-38). If they came from the screening service (US-35), they are still taken to it after logging in.
- New accounts always get the client role. The administrator role cannot be chosen at sign-up; it can only be given with the server-side scripts (US-22, US-23).

### US-20 · Be logged in automatically after registering — *Could*
**As a** new client, **I want** to be logged in automatically right after I register, **so that** I can continue straight away without typing my details again.

**Acceptance criteria**
- After successful registration, a session is created immediately, with no separate log-in step.
- A short welcome message is shown. If the client was sent to registration from the screening service (US-35), they are taken straight to the start of the screening. Otherwise they return to the page they were on before signing up (or to the start page).
- The menubar immediately shows the logged-in state (US-41).
- If registration fails, no session is created and no account is saved.

### US-21 · Log in and log out — *Must*
**As a** client or administrator, **I want** to log in with my username or email address and password, and to log out, **so that** I can access my account securely and end my session on shared devices.

**Acceptance criteria**
- A failed log-in shows one general message ("Username/email or password is incorrect") without saying which part was wrong, so attackers can't find out which accounts exist.
- After a configured number of failed attempts in a row (e.g. 5), further attempts for that account are delayed for a set time.
- Logging out ends the session on the server, not only in the browser, and returns the user to the start page.
- A session expires after a configured period of inactivity (e.g. 30 minutes).
- The log-in page has a "Forgot your password?" link (US-39).
- When a suspended or banned user logs in with the **correct** password, they are not logged in. Instead they see an account status page:
  - **Suspended by an administrator:** "Your account is suspended until [end date and time]." The date and time are shown in the user's chosen language and date format (US-60).
  - **Suspended automatically (US-50):** "Your account is temporarily suspended while an administrator reviews it." This case has no end date yet.
  - **Banned:** "Your account has been banned." No end date is shown, because a ban lasts until an administrator lifts it.
  - Every version of the page explains how to get in touch if the user thinks it is a mistake.
- The status page is shown **only** after the correct password has been entered. With a wrong password, the normal general error message appears, so nobody can find out an account's status just by trying to log in.
- No session is created for a suspended or banned user, and the menubar stays in the logged-out state (US-40).
- Once a suspension has ended or been lifted, the user can log in normally.
- Each blocked log-in is logged with the time, the username and the account status.

### US-22 · See Sign up and Log in when I'm not logged in — *Must*
**As a** visitor, **I want** to see "Sign up" and "Log in" options on the menubar, **so that** I can easily create an account or access my existing one.

**Acceptance criteria**
- When no one is logged in, the menubar shows "Sign up" and "Log in" on every page.
- "Sign up" opens the registration form (US-36); "Log in" opens the log-in form (US-38).
- The menubar does not show the profile button, "Admin", "Cases", "Users", "Warnings", "Logs" or "Metrics".

### US-23 · Use a profile menu when I'm logged in — *Must*
**As a** logged-in user, **I want** a profile button on the menubar, with a dropdown menu for my cases, editing my profile and logging out, instead of "Sign up" and "Log in", **so that** I can see I'm logged in and reach my account options in one place.

**Acceptance criteria**
- When a user is logged in, "Sign up" and "Log in" are not shown on any page. A profile button showing the user's username (and a person icon) is shown instead.
- Hovering the mouse over the profile button opens a dropdown menu with three options: "My cases", "Edit profile" and "Log out".
- Because touchscreens have no hover, the dropdown also opens when the button is tapped or clicked. It can also be opened and used with the keyboard (Tab to reach it, Enter to open, arrow keys to move, Esc to close).
- The dropdown closes when the mouse leaves it, when the user clicks elsewhere, or when an option is chosen.
- "My cases" opens the list of the user's own cases (US-49).
- "Edit profile" opens the profile page (US-42).
- "Log out" logs the user out (US-38), and the menubar switches back to the logged-out state (US-40).

### US-24 · Edit my profile and change my password — *Could*
**As a** logged-in user, **I want** to change my profile details, including my password, **so that** my account information stays up to date and secure.

**Acceptance criteria**
- The profile page is reached through "Edit profile" in the profile menu (US-41). Users can only ever see and edit their own profile.
- The user can change their username and their email address. The same rules as at registration apply (US-36): usernames and email addresses must be unique and valid, and a new email address must not be on the banned-email list.
- Changing the email address requires entering the current password, to protect the account if someone else gets access to an open session.
- The password is changed in a separate section. The user enters their current password, then the new password twice. The new password must meet the same rules as at registration (US-36), including the live strength indicator.
- After a password change, the user stays logged in on the current device but is logged out everywhere else.
- Changes are saved only when the user clicks "Save", and "Cancel" discards them. Every error names the field that is wrong, and a confirmation message appears after saving.
- The role (client or administrator) is shown but cannot be changed here.
- The same page also shows:
  - the consent status, with the option to withdraw it (US-53);
  - how long uploaded files are kept (US-54), and how long the account can be inactive before it is deleted with all its data (US-55);
  - the "Download my data" option (US-58);
  - the "Delete my account and data" option (US-56).
- Each change is logged with the field changed and the time. Passwords, old or new, are never logged.

### US-25 · See the Admin option when I'm an administrator — *Must*
**As an** administrator, **I want** an "Admin" option on the menubar when I'm logged in, **so that** I can reach the admin area quickly.

**Acceptance criteria**
- When the logged-in user has the administrator role, the menubar shows "Admin" (leading to the admin dashboard), "Cases" (leading to the list of all cases, US-25), "Users" (leading to the user list, US-27), "Warnings" (leading to warnings and suspensions, US-28), "Logs" (leading to the log viewer, US-26) and "Metrics" (leading to the metrics page, US-47), in addition to the profile button.
- If an administrator's role is removed (US-24), these options disappear the next time a page loads.

### US-26 · Not see the Admin option when I'm not an administrator — *Must*
**As a** client, **I want** the menubar to show only options I can actually use, **so that** the interface isn't confusing.

**Acceptance criteria**
- When the logged-in user does not have the administrator role, the menubar does not show "Admin", "Cases", "Users", "Warnings", "Logs" or "Metrics".
- Hiding the option is only for convenience; it is **not** the security measure. Access is actually blocked on the server (US-45, US-46, US-47).

### US-27 · Block the admin page for visitors who aren't logged in or administrators — *Must*
**As an** administrator, **I want** the admin page to be unreachable for anyone who is not logged in, **so that** lawyer data and categories cannot be viewed or changed by strangers.

**Acceptance criteria**
- A visitor who types an admin page address directly into the browser is redirected to the log-in page and sees no admin content.
- If they then log in as an administrator, they are taken to the page they originally asked for. If they log in as a client, US-46 applies.
- Every request to the admin functions from outside the pages (e.g. calling the server directly) is refused with a 401 response.
- These checks happen on the server, so they cannot be bypassed by changing anything in the browser.
- A logged-in client who opens an admin page address sees an "Access denied" page (403 response) and no admin content.
- Every request to the admin functions from a non-admin account is refused with a 403 response.
- Each refused attempt is logged with the username, the address requested and the time.

### US-28 · Restrict the metrics page to be available only for administrators — *Must*
**As an** administrator, **I want** the metrics page to be available only to administrators, **so that** internal performance, cost and usage figures are not visible to the public.

**Acceptance criteria**
- The metrics page contains the dashboards and exports from US-31 to US-33.
- Visitors who are not logged in are redirected to the log-in page (as in US-45). Logged-in non-admins see "Access denied" (as in US-46).
- Data exports (e.g. CSV downloads) follow the same rules and cannot be downloaded through a direct link by non-admins.

### US-29 · Keep each case private to its owner and administrators — *Must*
**As a** client, **I want** my case and its recommendations to be visible only to me and to administrators, **so that** no other user can see my legal problem, my documents or which lawyer I chose.

**Acceptance criteria**
- Every case is linked to the account that created it.
- A case includes everything stored with it:
  - the problem description and follow-up answers;
  - uploaded documents and extracted data;
  - the classification;
  - the three recommendations and their explanations;
  - the chosen lawyer and their contact details.
- A client can open only their own cases (from the "My cases" list, US-49).
- If a client tries to open another user's case, for example by changing the case number in the web address, they get a "Not found" page (404 response).
  - The page reveals nothing about the case, not even that it exists.
  - The attempt is logged with the username, the case requested and the time.
- Case numbers in web addresses are long random identifiers (e.g. a UUID, Universally Unique Identifier) rather than 1, 2, 3…, so they cannot be guessed.
- Administrators can open any case from the admin case list (US-25).
  - Personal data in the problem description and extracted text is shown masked (US-08).
  - Original uploaded files are not shown to administrators.
- Every time an administrator opens a case, this is logged with the administrator's username, the case and the time.
- The checks happen on the server for every request: case pages, documents, recommendations, contact details and data exports. The browser alone cannot get around them.
- Cases are not shared with the recommended lawyers. The client decides whether to contact a lawyer (US-16).
- The metrics page (US-47) shows only totals and averages, never individual cases.
- When a client deletes their account (US-56), their cases disappear for administrators too.

### US-30 · See a list of my cases — *Must*
**As a** client, **I want** a "My cases" page listing all the cases I have submitted, **so that** I can look at earlier results again, find a lawyer's contact details later, or continue a case I didn't finish.

**Acceptance criteria**
- The page is reached through "My cases" in the profile menu (US-41).
- It lists only the logged-in client's own cases (US-48), newest first, 20 per page.
- Each row shows:
  - the date the case was created;
  - a short title made from the first words of the problem description;
  - the legal category, in plain language with the legal term in smaller text below (as in US-03);
  - the status;
  - the chosen lawyer's name, if one has been chosen.
- The possible statuses are:
  - *In progress*;
  - *Waiting for your answers*;
  - *Recommendations ready*;
  - *Lawyer chosen*;
  - *Could not be categorised*.
- The client can filter the list by status and category.
- Clicking a case opens its detail page, which shows:
  - the problem description and follow-up answers;
  - the confirmed document data;
  - the category and confidence;
  - the three recommendations with their explanations (US-15);
  - the chosen lawyer's contact details (US-16).
- On the detail page, the problem description, answers and document data are shown in their original, unmasked version (US-08).
- Recommendations are shown as they were when the case was completed. If a recommended lawyer has since been deactivated, a note says they no longer accept clients through the platform.
- Once the uploaded files have been deleted after the file retention period (US-54), the case still shows its results and the extracted document data, with a note saying the files were deleted and when.
- Unfinished cases have a "Continue" button that returns the client to the step where they stopped.
- A client who has chosen a lawyer can still choose a different one of the three from the detail page (as in US-16).
- A "New case" button starts a new screening.
- If the client has no cases yet, the page says so and shows a button to start their first screening.
- Every case in the list has a delete option next to it (US-57).
- All text on the page appears in the client's chosen language (US-59).


### US-31 · Delete a single case — *Could*
**As a** client, **I want** a delete option next to each of my cases, **so that** I can remove one case completely without deleting my whole account.

**Acceptance criteria**
- Every case in "My cases" (US-49) has a delete button (a bin icon with the label "Delete") next to it. The same button is also on the case detail page.
- A confirmation dialog names the case by its date and title, lists what will be deleted, and says that deletion cannot be undone.
- After confirmation, everything stored for that case is permanently deleted:
  - the description and answers;
  - the stored uploaded files, extracted text and data;
  - the classification;
  - the recommendations with their explanations;
  - the lawyer choice;
  - the PII mapping for that case.
- Only that case is affected. The client's other cases and their account stay unchanged.
- The case disappears immediately from the client's list and from the admin case list (US-25).
- Metrics keep only anonymous totals that cannot be traced back to the deleted case.
- The deletion is logged with the case ID, the user and the time, never the deleted content.
- The server checks that the case belongs to the user, so nobody can delete another user's case (US-48).




# SZD II.

## Epic 6 — Document Processing I.

### US-32 · Upload PDF documents — *Should*
**As a** client, **I want** to upload PDF documents related to my case (e.g. a contract, a letter), **so that** the system can use their contents without me retyping them.

**Acceptance criteria**
- Accepted file types:
  - PDF;
- Limits are configurable, for example:
  - 30 pages per PDF;
  - 10 files per case.
- Other file types and files over the limits are rejected with a clear message explaining why. The security checks are described in US-51.
- For PDFs that contain a text layer (i.e. created digitally, not scanned), text is extracted directly, page by page, keeping the page number for each piece of text. Photos and scanned PDF pages are read with OCR (US-08).
- If extraction fails, the client is told and offered to try again with a higher quality scanned document or picture. If extraction fails again. client is told and offered to change their description of the case and can continue without the document.

### US-33 · Upload photos — *Could*
**As a** client, **I want** to upload photos related to my case (e.g. a photo of a letter taken with my phone), **so that** the system can use their contents without me retyping them.

**Acceptance criteria**
- Accepted file types:
  - photos in JPG, PNG, HEIC (the default photo format on iPhones) and WebP.
- Limits are configurable, for example:
  - 10 MB per file before conversion;
  - 10 files per case.
- Other file types and files over the limits are rejected with a clear message explaining why. The security checks are described in US-51.
- After upload, each photo is resized so that its longer side is at most a configured size (e.g. 2,000 pixels). This keeps text readable for OCR while making the file much smaller.
- Each photo is then converted to JPG, which is compact for ordinary photos. It is converted to PNG instead when that gives a smaller file or keeps text sharper, e.g. for screenshots.
- Only the converted version is kept; the original upload is discarded.
- During conversion:
  - hidden EXIF metadata (e.g. the GPS location where the photo was taken) is removed;
  - photos taken sideways on a phone are rotated the right way up.
- Several photos can be uploaded as one document (e.g. a three-page letter photographed page by page). The client can put them in order, and each photo counts as one page for page references (US-09).
- If extraction fails, the client is told and offered to try again with a higher quality scanned document or picture. If extraction fails again. client is told and offered to change their description of the case and can continue without the document.

### US-34 · Have scanned documents read automatically — *Could*
**As a** client, **I want** scanned or photographed documents to be read too, **so that** I can use paper documents I only have as scans.

**Acceptance criteria**
- The system detects pages with no (or too little) extractable text, e.g. fewer than a configured number of characters per page, and runs OCR **only on those pages**.
- OCR is not run on pages that already have a usable text layer (saves time and cost). Photos (US-06) have no text layer, so they always go through OCR.
- Each page records which method was used (native extraction or OCR) and, for OCR, the OCR engine's confidence value.
- Pages with very low OCR confidence are marked as low-reliability and feed into US-10.

### US-41 · Have my personal data masked — *Should*
**As a** client, **I want** my personal data in uploaded documents, in my description, in the follow-up questions and answers to be automatically detected and masked, **so that** my sensitive information is not exposed to AI services or to people who don't need to see it.

**Acceptance criteria**
- The system detects at least: person names, addresses, phone numbers, email addresses, dates of birth, national ID / tax / social-security numbers, and bank account numbers (IBAN — International Bank Account Number).
- Detected items are replaced with consistent placeholders (e.g. the same person is always `[PERSON_1]`) so the text still makes sense.
- Masking happens **before** any text is sent to an external LLM (enforced in the LLM gateway, US-30).
- The mapping between placeholders and original values (the PII mapping) is stored separately from the masked text and encrypted. Only the parts of the system that need it can read it, e.g. masking new text consistently within a case, and deletion.
- The problem description (US-01), follow-up answers (US-02) and extracted document data are stored in two versions: the original (unmasked) version and the masked version.
- The two versions are used in different places:
  - the **masked** version is the only one sent to an LLM, shown to administrators (US-48), written to logs or used in metrics;
  - the **original** version is stored encrypted and is only ever shown to the client who owns the case.
- When clients view their own case (US-49), they see the original, unmasked version.
- When a case is deleted (US-56, US-57, US-55), both versions and the PII mapping are deleted together.

---

## Epic 7 — Administration & Management II.

### US-37 · View all logged events as an administrator — *Must*
**As an** administrator, **I want** a "Logs" menu item where I can view everything the system has logged, **so that** I can investigate problems, security incidents and misuse in one place.

**Acceptance criteria**
- Logged-in administrators see "Logs" on the menubar (US-43). The page follows the same access rules as the admin area (US-45, US-46).
- The log viewer shows all logged event types:
  - log-ins, failed log-ins, log-outs, password reset requests and resets (US-38, US-39);
  - refused access attempts (US-46, US-48);
  - changes made in the admin area and administrators opening cases (US-17, US-48);
  - administrators created, promoted or demoted with the server scripts (US-22, US-23, US-24);
  - AI calls, including which user they were made for (US-30, US-50);
  - rate-limit hits, warnings, suspensions, bans and review decisions (US-50, US-27, US-28);
  - rejected uploads and suspected prompt injection (US-51, US-52);
  - errors (US-32);
  - automatic and user-requested deletions, and data downloads (US-54, US-56, US-57, US-58).
- Each entry shows the time, event type, user (if any), severity (information, warning or error) and a short description. Clicking an entry shows its full details.
- Entries can be filtered by event type, user, severity and date range, and searched by free text. Filters can be combined.
- The newest entries are shown first, e.g. 100 per page.
- The log viewer is read-only. Log entries cannot be changed or deleted through the website.
- Logs never contain passwords, reset codes or unmasked personal data, so the log viewer cannot expose them.
- Filtered results can be exported as a CSV file. Each export is logged with the administrator's username and the time.

---

## Epic 8 — Architecture & Auditing II.



### US-39 · Track performance, cost and errors — *Must*
**As a** product owner, **I want** to track response times, API costs and error patterns, **so that** I can spot problems and keep the system fast and affordable.

**Acceptance criteria**
- Response time is recorded per step (intake, extraction, OCR, masking, classification, matching) and per whole request; the dashboard shows the average and the 95th percentile (the time within which 95% of requests finish).
- API cost is shown per case, per day and per module.
- Errors are grouped by type (e.g. OCR failure, LLM timeout, invalid upload) and by module, with counts over time.

---


# Later

## Epic 9 — Client Intake & Interaction III.

### US-40 · See clear disclaimers — *Should*
**As a** client, **I want** to see clearly that the system provides preliminary screening and not legal advice, **so that** I understand its limits and don't rely on it as a substitute for a lawyer.

**Acceptance criteria**
- A disclaimer is shown on the start page and must be acknowledged (checkbox) before the client can submit a problem.
- A short version of the disclaimer is shown on the results page next to the category and the recommendations.
- The disclaimer text is editable by an administrator without a code change, in all three interface languages (US-60).
- The acknowledgement (yes/no plus timestamp) is stored with the case.

---

## Epic 10 — Document Processing II.

### US-42 · Review masked documents and description — *Should*
**As a** client, **I want** to be able to review the masked documents and description and change it if personal data can be found, **so that** my sensitive information is not exposed to AI services or to people who don't need to see it.

**Acceptance criteria**
- The client sees a preview of what was masked and can mark missed items for masking or un-mask items wrongly masked (e.g. the name of a company that is the other party). It is displayed on the page that all unmasked data will be sent to an AI maintained by a thrid-party organization.

### US-43 · See where extracted information came from — *Could*
**As a** client, **I want** to see exactly which page and passage each extracted piece of information came from, **so that** I can check it is correct.

**Acceptance criteria**
- The system extracts a defined set of structured fields (e.g. document type, date, parties involved, amounts, deadlines).
- Every extracted field shows its source: page number and the text snippet it was taken from.
- Clicking or tapping a field highlights or displays the source snippet.
- Fields with no source found are shown as "not found", never filled in by guessing.

### US-44 · Confirm uncertain extracted data — *Should*
**As a** client, **I want** to be asked to confirm or correct information the system extracted with low reliability, **so that** mistakes in reading my documents don't lead to a wrong result.

**Acceptance criteria**
- Each extracted field has a reliability score; fields below a configured threshold are shown to the client for review, with the source snippet (US-09) next to them.
- The client can confirm, correct, or reject each flagged field.
- Only confirmed or corrected values are used in classification and matching.
- The system logs the original value, the client's action, and the final value (for the audit module, US-31).

---




## Epic 11 — Administration & Management II.

### US-45 · Deactivate a lawyer without deleting them — *Could*
**As an** administrator, **I want** to deactivate a lawyer profile instead of deleting it, **so that** past recommendations and audit records stay intact.

**Acceptance criteria**
- Deactivated profiles are excluded from new recommendations but remain visible in historical cases and logs.
- A deactivated profile can be reactivated.

### US-46 · Promote an existing user to administrator with a server-side script — *Should*
**As a** server operator, **I want** to give an existing user the administrator role with a command-line script on the server, **so that** new administrators can be added without an admin-granting function on the web.

**Acceptance criteria**
- The script is run in a terminal on the server with the username or email address of an existing account.
- Before changing anything, it shows the account's username and email address and asks for confirmation (yes / no).
- If no account matches, the script prints an error and changes nothing. If the user is already an administrator, it says so and changes nothing.
- After promotion, the user sees the admin options (US-43) the next time a page loads.
- There is no web page, address or server function that grants the administrator role. The script can only be run by someone with access to the server.
- Each promotion is logged with the promoted username and the time.

### US-47 · Remove the administrator role with a server-side script — *Should*
**As a** server operator, **I want** to take the administrator role away from a user with a command-line script on the server, **so that** administrator access can be withdrawn without an admin-management function on the web.

**Acceptance criteria**
- The script is run in a terminal on the server with the username or email address of an existing account.
- Before changing anything, it shows the account's username and email address and asks for confirmation (yes / no).
- If no account matches, the script prints an error and changes nothing. If the user is not an administrator, it says so and changes nothing.
- The script refuses to remove the role from the last remaining administrator, so the system is never left without one.
- After the change, the account becomes a normal client account.
  - The admin options disappear from its menubar (US-43).
  - The very next request it makes to an admin page or function is refused (US-46), even if an admin page is already open.
- There is no web page, address or server function that removes the administrator role. The script can only be run by someone with access to the server.
- Each removal is logged with the username and the time.

### US-48 · List and manage all users as an administrator — *Must*
**As an** administrator, **I want** a "Users" menu item that lists all registered users, **so that** I can find any account, see how much it uses the AI, and suspend or ban it if needed.

**Acceptance criteria**
- Logged-in administrators see "Users" on the menubar (US-43). The page follows the same access rules as the admin area (US-45, US-46).
- The list shows one row per user, with:
  - username and email address;
  - registration date;
  - number of AI calls (last 30 days and in total);
  - role;
  - account status (*Active*, *Suspended* or *Banned*).
- The list can be filtered by username, email address, registration date range, number of AI calls (e.g. more than 100) and status. Filters can be combined.
- The list can be sorted by any column, e.g. most AI calls first. It shows e.g. 50 users per page.
- Clicking a user opens their detail page, which shows:
  - username and email address;
  - number of AI calls (and their cost);
  - account status;
  - the user's warnings and suspensions, with a link to each entry (US-28);
  - a **Suspend** button and a **Ban** button.
- Both buttons ask for confirmation before doing anything, e.g. "Are you sure you want to suspend *username*?".
  - The administrator must give a reason.
  - When suspending, they also choose the length of the suspension. Quick options are offered (e.g. 1, 7 or 30 days), or any end date and time can be entered. The end date must be in the future.
- **Suspended** users:
  - are logged out immediately;
  - cannot log in until the end date;
  - see the account status page with the end date when they try to log in (US-38);
  - receive an email saying they have been suspended and until when.
- **Banned** users:
  - are logged out immediately and cannot log in for as long as the ban lasts. A ban has no end date and stays in force until an administrator lifts it. When they try to log in, they see the account status page (US-38);
  - receive an email saying their account has been banned;
  - cannot use their email address to register a new account, because it is added to the banned-email list (US-36).
- A suspension or ban can be lifted early with a "Lift" button, which also asks for confirmation and a reason.
  - After a lift, the user can log in again and receives an email saying so.
  - Lifting a ban also removes the email address from the banned-email list.
- A suspension ends automatically at its end date. The user can then log in again, and this is logged.
- Administrators cannot suspend or ban themselves or other administrators. An administrator's role must first be removed with the server script (US-24).
- If a banned account is later deleted (US-56, US-55), its email address is kept on the banned-email list only as a hash, so the ban still works without keeping the person's data.
- Every suspension, ban and lift is logged with:
  - the time;
  - the affected user's username;
  - the administrator's username;
  - the reason;
  - the length: the number of days and the end date for a suspension, or "indefinite" for a ban.
- The same details are shown in the user's history on their detail page.

### US-49 · Review warnings and suspensions — *Must*
**As an** administrator, **I want** a "Warnings" menu item that lists all automatic warnings and suspensions, **so that** I can review suspicious accounts and decide whether to suspend them.

**Acceptance criteria**
- Logged-in administrators see "Warnings" on the menubar (US-43), with a count of entries not yet reviewed. The page follows the same access rules as the admin area (US-45, US-46).
- The list shows one row per entry, with:
  - the date;
  - the username;
  - the type (*Warning* or *Automatic suspension*);
  - the reason, e.g. "120 AI calls in 24 hours (warning threshold: 50)";
  - the status (*Open*, *Reviewed – no action*, *Suspended*, *Suspension lifted* or *Banned*).
- The list can be filtered by username, type, status and date range. Filters can be combined, and open entries are shown first.
- Opening an entry shows:
  - the user's username and email address;
  - the number of warnings and suspensions this user has had so far, with the date of each;
  - a list of all cases the user has submitted.
- Clicking one of those cases opens it in the admin view, with personal data masked (US-48).
- Every entry page has two options:
  - **No action:** marks the entry as reviewed without suspending the user. For an automatic suspension this means lifting it.
  - **Suspend:** suspends the user (or keeps the automatic suspension) for a length of time the administrator chooses, as in US-27.
- Pressing **Suspend** asks for confirmation first, e.g. "Are you sure you want to suspend *username* for 7 days?", together with a required reason.
- The entry page also links to the user's detail page (US-27), where a ban is possible.
- Each decision is logged with the time, the affected user's username, the administrator's username, the decision, the reason and, for a suspension, its length and end date.

---


## Epic 12 — Architecture & Auditing III.

### US-50 · Measure task completion — *Must*
**As a** product owner, **I want** to see how many clients complete the full flow and where they drop out, **so that** I can find confusing or frustrating steps.

**Acceptance criteria**
- Each case records which steps it reached: submitted, follow-ups answered, documents confirmed, classified, recommendations shown, lawyer chosen and contact details shown (US-16).
- The dashboard shows the completion rate and the drop-off rate at each step.
- Metrics can be filtered by date range and exported (e.g. CSV — Comma-Separated Values, a plain spreadsheet-compatible format).

---

## Epic 13 — User Accounts & Access Control II.

### US-51 · Reset a forgotten password by email — *Must*
**As a** client or administrator who has forgotten my password, **I want** to get a reset link by email and set a new password, **so that** I can get back into my account without contacting anyone.

**Acceptance criteria**
- The log-in page (US-38) has a "Forgot your password?" link. It opens a page asking only for an email address.
- After the email address is submitted, the same message is always shown: "If an account exists for this email address, we have sent a link to reset your password."
  - This applies whether or not the address belongs to an account. The page never says that an email address is unknown or wrong, so nobody can use it to find out who is registered.
  - The page responds equally fast in both cases, because the email is sent in the background.
- If the address belongs to an account, an email is sent in the user's preferred language (US-59). It contains a reset link with a long random code that cannot be guessed.
  - Only a hash of the code is stored, not the code itself (see *Hashing* in the glossary).
- The link expires after a short, configurable time (e.g. 30 minutes) and works only once. Requesting a new link makes all earlier links for that account invalid.
- Opening a valid link shows a form for entering the new password twice. The same password rules and strength indicator apply as at registration (US-36).
- An expired, used or invalid link shows a neutral message with an option to request a new one. It reveals nothing about the account.
- After a successful reset:
  - the new password is stored as a hash;
  - the account is logged out on all devices;
  - the user is taken to the log-in page with a success message;
  - a second email confirms that the password was changed, so the owner notices if they didn't do it themselves.
- Reset requests are limited (e.g. 3 per email address per hour). Extra requests show the same neutral message but send no email.
- Requests and successful resets are logged with the account and the time. Reset codes and passwords are never logged.

---

## Epic 14 — Security

### US-52 · Limit request rates, flag heavy users and suspend extreme ones automatically — *Must*
**As a** server operator, **I want** limits on how often requests can be made, and automatic warnings and suspensions for unusually heavy AI usage, **so that** bots can't overload the system or run up AI costs, and administrators have time to review suspicious accounts.

**Acceptance criteria**
- Configurable rate limits apply to:
  - registration and log-in attempts per IP address (the internet address of the device making the request);
  - password reset requests (US-39);
  - new screenings and AI calls per user, per hour and per day (e.g. 5 screenings per hour, 20 per day);
  - uploads per user.
- When a limit is reached, the user gets a 429 response. They see a message in their language saying the limit was reached and when they can try again. Anything they had entered is kept.
- Every AI call is logged with the user it was made for, the time, the module, the token counts and the cost (US-30).
- There are two configurable usage thresholds, each measured over a set time window (e.g. AI calls in the last 24 hours):
  - **Warning threshold:** a user who goes over it is flagged. A warning is created and listed for administrators (US-28). The user is not blocked.
  - **Suspension threshold** (higher): a user who goes over it is **automatically and temporarily suspended**. This gives an administrator time to review the account. A suspension entry is created and listed for administrators (US-28).
- An automatically suspended user is logged out immediately and cannot log in.
  - When they try to log in, they see the account status page saying the account is temporarily suspended pending review (US-38).
  - They also receive an email saying the same.
- An automatic suspension stays in place until an administrator reviews it (US-28). The administrator can lift it or replace it with a longer suspension or a ban.
- Administrator accounts are never suspended automatically. If one goes over a threshold, only a warning is created.
- Rate-limit hits and warnings are logged with the user, the time and which threshold was exceeded.
- Automatic suspensions are logged with the time, the user's username, the reason (which threshold was exceeded) and the length ("until reviewed by an administrator").

### US-53 · Check uploaded files for security risks — *Must*
**As a** server operator, **I want** every uploaded file to be checked and handled safely, **so that** uploads cannot be used to attack the server or other users.

**Acceptance criteria**
- Only the file types listed in US-06 are accepted.
- Both the file extension and the actual file content are checked. The first bytes of a file (its "magic bytes") show its real type, and they must match the extension. A mismatched file, such as a program renamed to ".pdf", is rejected.
- Size, page-count and image-dimension limits are enforced on the server, not only in the browser.
- Images with extremely large pixel dimensions are rejected before they are opened. This blocks "decompression bombs": small files that expand to a huge size in memory.
- PDFs that are password-protected, damaged, or contain embedded JavaScript or embedded files are rejected with an explanation.
- Every file is scanned with a virus scanner (e.g. ClamAV, a free open-source scanner) before processing. Infected files are deleted immediately and the event is logged.
- Files are saved on the server under random names. The original file name is kept only as text, with unsafe characters removed.
- Files are stored outside any publicly reachable folder and can only be opened through the permission-checked case pages (US-48).
- Conversion, text extraction and OCR run with time and memory limits, so one bad file cannot slow down or crash the system.
- Photos are fully re-encoded during conversion (US-06), which also discards any hidden content.
- Every rejected upload is logged with the user, the file type, the reason and the time.

### US-54 · Protect the AI against prompt injection — *Should*
**As a** server operator, **I want** the system to resist prompt injection, **so that** text in a problem description or document cannot manipulate the classification, the recommendations or the system's behaviour.

**Acceptance criteria**
- Client text and document text are always sent to the LLM as clearly marked data, separate from the system's own instructions. The instructions tell the model to treat this data only as content to analyse, never as instructions.
- The LLM cannot take actions. It has no tools, no database access and no access to other cases. It only returns text in the fixed format checked by US-12, so a successful injection can at worst produce a wrong category. The validation and the confidence rules (US-03, US-04) limit even that.
- AI-generated text shown to the client, such as follow-up questions, is displayed as plain text. Any HTML, links or scripts in it are not rendered.
- Known injection patterns are detected, such as "ignore previous instructions" or attempts to change the AI's role.
  - Affected cases are flagged in the logs (US-26) and in the admin case list (US-25).
  - They are otherwise processed normally.
- A test set of injection attempts, in all three languages, is part of the automated tests and must pass before each release.

---


## Epic 15 — Privacy & Data Protection (GDPR)

### US-55 · Give explicit consent to data processing — *Must*
**As a** client, **I want** to be clearly asked for my consent before my data is processed, **so that** I know what happens to my information and can decide for myself.

**Acceptance criteria**
- Consent is asked at registration. Because only logged-in users can use the screening service (US-35), nobody can submit a problem without having given consent.
- The consent checkbox is **not** ticked in advance and is separate from the disclaimer acknowledgement (US-05).
- Next to the checkbox, a short plain-language summary explains:
  - what data is collected;
  - why it is collected;
  - which outside services receive masked text (e.g. the LLM provider);
  - how long each type of data is kept.
- A link opens the full privacy policy.
- If a client has withdrawn consent, they cannot submit a problem or upload documents until they give it again, and the page explains why.
- The system stores when consent was given and which version of the privacy text was accepted. If the text changes, the client is asked again the next time they log in.
- A logged-in client can withdraw consent on their profile page (US-42). Withdrawing stops any further processing of their data and offers deletion (US-56).

### US-56 · Delete uploaded files after a short retention period — *Must*
**As a** client, **I want** my uploaded files to be kept only for a short time, **so that** copies of my sensitive documents don't stay on the server longer than needed.

**Acceptance criteria**
- The file retention period is a configurable setting, shorter than the account inactivity period (e.g. 30 days after upload). It is stated in the privacy policy.
- The upload page tells the client how long files are kept. The case detail page (US-49) shows the date when the files will be, or were, deleted.
- An automatic job, running at least once a day, permanently deletes stored uploaded files whose retention period has ended.
- The data extracted from the files and confirmed by the client (US-10) stays part of the case. Only the files themselves are deleted.
- Each deletion is logged with the case ID, the file and the time, never the file content.

### US-57 · Delete inactive accounts and all their data automatically — *Must*
**As a** client, **I want** my account and all my data to be deleted automatically if I stop using the service, **so that** my information is not kept longer than necessary.

**Acceptance criteria**
- The inactivity period is a configurable setting (e.g. 6 months without logging in) and is stated in the privacy policy. It is counted from the user's last log-in.
- A configured time before the deletion date (e.g. 14 days), the user gets an email in their preferred language (US-59). The email says:
  - that their account and all their data will be deleted;
  - on which date;
  - that logging in before that date keeps the account.
- Logging in before the deletion date cancels the deletion and restarts the inactivity period.
- On the deletion date, an automatic job (running at least once a day) permanently deletes:
  - the user account;
  - all of the user's cases, in both their original and masked versions;
  - uploaded files, extracted data and PII mappings;
  - recommendations and lawyer choices.
  This is the same set of data as a manual account deletion (US-56).
- The metrics (US-31 to US-33) keep only anonymous totals that cannot be traced back to the person.
- A last email confirms that the deletion has been done. It is sent before the email address itself is deleted.
- Administrator accounts are not deleted automatically. Their role must first be removed with the server script (US-24).
- If the account was banned, only a hash of the email address is kept on the block list (US-27).
- Each deletion is logged with an anonymous account reference and the time, never the deleted content.

### US-58 · Delete my account and all my data — *Must*
**As a** logged-in client, **I want** to start the deletion of my account and all my data myself, **so that** I can use my right to be forgotten without having to contact anyone.

**Acceptance criteria**
- The profile page (US-42) has a "Delete my account and data" option.
- Before anything is deleted, a confirmation screen explains:
  - what will be deleted (account, cases, problem descriptions, answers, documents, extracted data, PII mapping, preferences, lawyer choices);
  - that deletion cannot be undone.
- The client confirms by entering their password again.
- Deletion happens straight away, or at most within one month (the GDPR limit). Records needed for the metrics are kept only in a form that can no longer identify the person.
- Afterwards, the client is logged out and sees a confirmation that the deletion was done.
- The last remaining administrator account cannot be deleted this way, so that the system is never left without an administrator.

### US-59 · Download all my data — *Must*
**As a** client, **I want** to download a copy of all the data the system holds about me, **so that** I can see what is stored and use my GDPR rights to access my data and move it elsewhere.

**Acceptance criteria**
- The profile page (US-42) has a "Download my data" button. For security, the user enters their password again before the download is prepared.
- The download is a ZIP file containing:
  - a JSON file with all the data in machine-readable form, so it can be moved to another service;
  - a human-readable version of the same data (e.g. an HTML page or a PDF);
  - any uploaded documents that are still stored.
- The data included:
  - account details: username, email address, language, role and registration date. The password hash is not included;
  - consent history (US-53);
  - all cases, with descriptions, answers and document data in their original, unmasked version (US-08);
  - extracted document data, categories and confidence scores;
  - recommendations with their explanations, and lawyer choices;
  - log-in history.
- Only the user's own data is included, never another user's.
- If preparing the file takes longer than a few seconds, the user gets an email when it is ready.
- The download link works for a short configured time only (e.g. 24 hours), and only when logged in as that user.
- Text in the file is in the user's chosen language.
- Each download is logged with the user and the time.

### US-64 Following GDPR rules - *Must*
**As a** client, **I want** the system to follow GDPR rules, **so that** my personal data is safe.

**Acceptance criteria**
- Read GDPR thorougly and learn all the criteria.
- Implement all feature needed to meet the criteria.

### US-65 Follow EU AI Act rules
**As a** client, **I want** the system to follow EU AI Act rules, **so that** my personal data is safe and I get all the information I need.

**Acceptance criteria**
- Read the EU AI Act thorougly and learn all the criteria.
- Implement all feature needed to meet the criteria.

### US-66 Following the law specific to legal services
**As a** client, **I want** the system to follow the law specific to legal services, **so that** my personal data is safe and I get all the information I need.

**Acceptance criteria**
- Read the law specific to legal services thorougly and learn all the criteria.
- Implement all feature needed to meet the criteria.

---

## Epic 16 — Multilingual Interface

### US-60 · Choose the interface language — *Could*
**As a** client or visitor, **I want** to switch the interface between English, Hungarian and German using a button, **so that** I can use the service in the language I understand best.

**Acceptance criteria**
- A language button is shown on the menubar on every page, whether or not the user is logged in.
- It offers English, Magyar and Deutsch, each written in its own language, and shows which language is currently selected.
- Switching the language updates all interface text immediately, without losing anything the user has already typed or uploaded.
- The choice is remembered: for logged-in users on their account, for visitors in the browser.
- On a first visit, the language is chosen from the browser's language settings. If that is not one of the three languages, English is used.

### US-61 · Get all client-facing content in my chosen language — *Could*
**As a** client, **I want** everything I see and read to be in my chosen language, **so that** I don't miss or misunderstand anything important.

**Acceptance criteria**
- The following are available in all three languages:
  - all interface text and error messages;
  - follow-up questions (US-02);
  - the disclaimer (US-05);
  - the consent text and privacy policy (US-53);
  - category descriptions (US-21);
  - recommendation explanations (US-15).
- Interface texts are stored in separate translation files, not written into the code, so they can be corrected without changing the program.
- If a translation is missing, the English text is shown and the missing entry is logged so it can be fixed.
- Dates and numbers use the chosen language's format (e.g. 2026. 09. 30. in Hungarian, 30.09.2026 in German, 30/09/2026 in English).
- The client can write their problem description in any of the three languages. Classification (US-11) works regardless of which one was used.
- The classification test set (US-31) contains examples in all three languages, so that accuracy can be reported per language.
- The admin interface itself may stay in English only.

---

## Epic 17 — Accessibility & Mobile

### US-62 · Meet the Web Content Accessibility Guidelines — *Should*
**As a** client with a disability (e.g. someone who uses a screen reader or only a keyboard), **I want** the site to meet WCAG 2.2 level AA, **so that** I can use the screening service like anyone else.

**Acceptance criteria**
- Every function can be used with the keyboard alone, with a clearly visible focus indicator and a logical order. This includes the profile dropdown (US-41), file upload and page ordering (US-06), and all dialogs.
- Screen readers (software that reads the screen aloud) are supported:
  - all form fields have labels;
  - images and icons have text alternatives;
  - the ✓ / ✗ marks in recommendation explanations (US-15) are also given as text;
  - error and status messages are announced.
- Each page declares its language (US-59), so screen readers pronounce the text correctly.
- Text contrast is at least 4.5:1 for normal text, and 3:1 for large text and interface elements.
- Information is never shown by colour alone. For example, confidence levels and statuses are also written out.
- Text can be enlarged to 200% without content being cut off or overlapping.
- Users are warned before a session expires (US-38) and can extend it.
- Clickable and tappable elements are at least 24 × 24 pixels, the WCAG 2.2 minimum.
- The admin pages meet the same standard.
- Automated accessibility checks (e.g. axe) run as part of the tests. Before each release, the main flow is tested manually with a screen reader (e.g. NVDA on Windows, VoiceOver on iPhone).

### US-63 · Use the site comfortably on a mobile phone — *Should*
**As a** client, **I want** the site to work well on my phone, **so that** I can describe my problem and photograph my documents wherever I am.

**Acceptance criteria**
- The layout adapts to every screen width from 320 pixels (a small phone) up to a large desktop monitor. There is no sideways scrolling, and body text is at least 16 pixels.
- On small screens, the menubar collapses into a menu button (the "three lines" icon). The language button, profile menu and admin items remain reachable.
- The profile dropdown opens on tap (US-41).
- On small screens, tables become stacked cards or scroll within their own area. This covers "My cases" (US-49), the admin case list (US-25) and the log viewer (US-26).
- On phones, the upload lets the client take a photo directly with the camera or choose one from the gallery (US-06).
- Tap targets on mobile are at least 44 × 44 pixels.
- Form fields bring up the right phone keyboard, e.g. the email keyboard for email fields.
- The site is tested on a current iPhone (Safari), a current Android phone (Chrome), and the common desktop browsers (Chrome, Firefox, Safari, Edge).
- The start page loads within about 3 seconds on a typical mobile (4G) connection.

---

# Summary

## SZD-I. Summary

| Epic | Stories | Must | Should | Could |
|---|---|---|---|---|
| 1 · Client Intake & Interaction | US-01 – US-03 | 3 | 0 | 0 |
| 2 · Classification & Recommendation | US-4 – US-9, US-35 - US-36 | 5 | 1 | 2 |
| 3 · Administration & Management I. | US-10 – US-15 | 2 | 3 | 1 |
| 4 · Architecture & Auditing I. | US-16 – US-17, US-38 | 3 | 0 | 0 |
| 5 · User Accounts & Access Control I. | US-18 – US-31 | 9 | 2 | 3 |
| **Total** | **34** | **22** | **6** | **6** |

## SZD-II. Summary

| Epic | Stories | Must | Should | Could |
|---|---|---|---|---|
| 6 · Document Processing I. | US-32 – US-34 | 0 | 1 | 2 |
| 7 · Administration & Management II. | US-37 – US-37 | 1 | 0 | 0 |
| 8 · Architecture & Auditing II. | US-38 – US-39 | 2 | 0 | 0 |
| **Total** | **6** | **3** | **1** | **2** |

## Later Summary

| Epic | Stories | Must | Should | Could |
|---|---|---|---|---|
| 9 · Client Intake & Interaction III. | US-40 – US-40 | 1 | 0 | 0 |
| 10 · Document Processing II. | US-42 – US-44 | 0 | 2 | 1 |
| 11 · Administration & Management II. | US-45 – US-49 | 2 | 2 | 1 |
| 12 · Architecture & Auditing III. | US-50 – US-50 | 1 | 0 | 0 |
| 13 · User Accounts & Access Control II. | US-51 – US-51 | 1 | 0 | 0 |
| 14 · Security | US-52 – US-54 | 2 | 1 | 0 |
| 15 · Privacy & Data Protection (GDPR) | US-55 – US-59 | 7 | 0 | 0 |
| 16 · Multilingual Interface | US-60 – US-61 | 2 | 0 | 2 |
| 17 · Accessibility & Mobile | US-62 – US-65 | 0 | 2 | 0 |
| **Total** | **27** | **16** | **7** | **4** |
