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
  - a masked version with personal data replaced by placeholders (US-41).
- The client can edit the description before submitting it.

### US-02 · Answer follow-up questions — *Must*
**As a** client, **I want** the system to ask me targeted follow-up questions about information I left out, **so that** my case is understood correctly without me having to guess what matters.

**Acceptance criteria**
- After submission, the system identifies missing key information (e.g. dates, the other party, location/jurisdiction, whether money is involved) and asks about it.
- Questions are structured (multiple choice, yes/no, date picker, or short text) rather than open-ended where possible.
- No more than a configurable number of questions per round (e.g. 5), and no more than a configurable number of rounds (e.g. 2), to avoid tiring the client.
- The client can skip any question; skipped questions are recorded as "not answered", not as a negative answer.
- Answers are stored in the same two versions (US-41). The masked version is used as input to classification (US-4).

### US-03 · Be told honestly when my problem can't be categorized — *Must*
**As a** client, **I want** the system to tell me clearly when it cannot confidently categorize my issue, **so that** I am not misled by a guess.

**Acceptance criteria**
- If confidence is still below the threshold after clarification, or the problem falls outside all categories, the system shows an explicit message such as: "We couldn't confidently match your problem to one of our legal areas."
- The message suggests a next step (e.g. contact a general legal advice service, or browse all lawyers manually).
- The case is flagged as "unclassified" in the audit module (US-16) for later review.

---

## Epic 2 — Classification & Recommendation Engine

### US-04 · Get my problem classified into a legal area — *Must*
**As a** client, **I want** my problem to be sorted into the right legal area, **so that** I know what kind of lawyer I need and how sure the system is.

**Acceptance criteria**
- Classification uses the client's description, follow-up answers and confirmed document fields as input.
- The output is exactly one category from the current taxonomy.
- If confidence is below the threshold, US-02 / US-03 apply instead of showing results.
- The input, output, confidence, model used, and response time are logged.

### US-05 · State my preferences for a lawyer — *Should*
**As a** client, **I want** to state my preferences (location, language, online or in-person consultation, fee), **so that** the recommendations fit my practical situation.

**Acceptance criteria**
- The client can set: location (city), language(s), consultation format (online / in-person / either) and preferred price.
- Sensible defaults are pre-filled (e.g. the language the client is using the site in).

### US-06 · Receive exactly three lawyer recommendations — *Must*
**As a** client, **I want** to receive the three best-matching lawyer profiles, **so that** I have a short, manageable choice instead of a long list.

**Acceptance criteria**
- Matching compares the case category and the client's preferences against lawyer profiles on five criteria: specialty, location, language, consultation format and fee.
- Specialty is a required match: a lawyer who does not cover the case's category is never recommended.
- Each criterion has a configurable weight; lawyers are ranked by weighted score.
- Only active profiles (see US-45) are considered.
- Maximum of three profiles are shown. If fewer than three lawyers match all required preferences, only the matching profiles are shown
- The same input with the same lawyer data always produces the same result (deterministic ranking; ties broken by a fixed rule).

### US-07 · Understand why each lawyer was recommended — *Could*
**As a** client, **I want** to see why each lawyer was recommended, **so that** I can trust the recommendation and choose between the three.

**Acceptance criteria**
- Each recommended profile shows a per-criterion breakdown, e.g. ✓ Specialty: tenancy law · ✓ Speaks Hungarian · ✓ Online consultations · ✗ Location.
- A one-sentence plain-language summary explains the main reason for the recommendation.

### US-08 · See the chosen lawyer's contact details — *Could*
**As a** client, **I want** to see the contact details of the lawyer I pick from the three recommendations, **so that** I can get in touch with them directly.

**Acceptance criteria**
- Each of the three recommended profiles has a "Choose this lawyer" button. Contact details are not shown before a lawyer is chosen.
- After choosing, the client sees the lawyer's name, office address, phone number and email address, plus a website or booking link if the profile has one.
- The page also repeats the lawyer's consultation formats and fee, so the client knows what to expect when they call.
- The phone number and email address are clickable links (tapping them opens the phone's dialler or the email program).
- The client can go back to the three recommendations and choose a different lawyer.
- The client's own details are **not** sent to the lawyer; the client decides whether and how to make contact.
- The short disclaimer (US-40) stays visible, including a note that the platform does not guarantee the lawyer will take the case.
- If the lawyer was deactivated after the recommendations were shown, the client sees a message saying so and is asked to choose another recommendation. A button is available to re-do the the recommendation.
- The system records which lawyer was chosen, which position they had in the list (1st, 2nd or 3rd), and when. Every change of choice is recorded too. This feeds the task completion metric (US-50) and shows how often clients pick the top-ranked lawyer.

### US-09 · Rule-based Classification — *Must*
**As a** client, **I want** the system to classify my case, **so that** I can find the best lawyer for me.

**Acceptance criteria**
- The system chooses a field following the classification rules according to the data extracted from the client's description and documents.
- The output is sent to the same interface as the LLM-based classification.
- If the case can not be classified, the system gives appropriate answer (e.g. "Not supported")
- If the system needs more information, the system gives appropriate answer (e.g "More information needed")

### US-35 . AI Classification - *Must*
**As a** client, **I want** the system to classify my case **so that** I can find the most suitable lawyer.
**Acceptance criteria**
- The extracted information from the uploaded documents is sent to an LLM.
- The LLM is asked to send the category back in a fixed format.
- The answer is always checked (US-36).
- All important information is logged (US-38) and available for the administrator (US-37).

### US-36 · Check that the AI's answer is a real category — *Must*
**As a** client, **I want** the system to check the AI's classification before it is used, **so that** I am never shown a category that doesn't exist or a broken result.

**Acceptance criteria**
- The LLM is asked to answer in a fixed JSON format containing only the category identifier.
- Before the answer is used, the system checks that:
  - the answer can be read in the expected format and has all required fields;
  - the category identifier matches an **active** category in the current taxonomy (US-13). The check compares identifiers, not category names as free text;
- Every invalid answer is logged with the reason (unknown category, wrong format, missing field or value out of range) and counted in the error statistics (US-39).


---

## Epic 3 — Administration & Management I.

### US-10 · Access the admin area securely — *Must*
**As an** administrator, **I want** a login-protected admin dashboard, **so that** only authorised staff can change lawyer data and categories.

**Acceptance criteria**
- Only users with the administrator role can access the admin interface (access rules in detail: US-25 to US-27).
- Every change made in the admin area is logged with who made it, when, and what changed (before/after values).

### US-11 · Create and edit lawyer profiles — *Should*
**As an** administrator, **I want** to create, edit and view lawyer profiles, **so that** the recommendation engine always works from accurate data.

**Acceptance criteria**
- Profiles can be created, edited, searched and filtered by any schema field.
- Changes take effect in recommendations immediately after saving.

### US-12 · Enforce a structured profile schema — *Should*
**As an** administrator, **I want** every lawyer profile to follow the same structured format, **so that** matching is fair and reliable across all lawyers.

**Acceptance criteria**
- Required fields: name, contact details (phone number, email address; website or booking link optional), areas of expertise (one or more, chosen from the taxonomy), office location (city), languages spoken, consultation formats (online / in-person), and price.
- Areas of expertise and languages are chosen from fixed lists, not typed freely, to avoid spelling variants.
- A profile cannot be saved if any required field is missing or invalid; the form shows which field is wrong.

### US-13 · Manage the legal category taxonomy — *Should*
**As an** administrator, **I want** to manage the list of legal categories, **so that** the system's categories match the lawyers and case types we actually handle.

**Acceptance criteria**
- Each category has a name, a plain-language client-facing description, and example problems, each entered in Hungarian.
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
- The same rules apply as at registration (US-19) for the username, the email address format and the password.
- If any rule fails, the script prints a clear error and creates nothing.
- The script refuses to create the account if the username or the email address is already in use.
- The password is stored only as a hash.
- The new account gets the administrator role and can log in on the website straight away.
- There is no web page, address or server function that creates administrators. The script can only be run by someone with access to the server.
- Each administrator created this way is logged with the username and the time, never the password. The script prints a confirmation message.

### US-15 · Browse and filter all cases as an administrator — *Could*
**As an** administrator, **I want** a "Cases" menu item that lists all existing cases with filters, **so that** I can review cases, find ones that could not be categorised, and check how the system is being used.

**Acceptance criteria**
- Logged-in administrators see "Cases" on the menubar (US-25). The page follows the same access rules as the admin area: unreachable for visitors and for non-admins (US-27).
- The list shows one row per case, with:
  - the creation date;
  - the case number;
  - the username of the client who created it;
  - the category (the legal term);
  - the status;
  - the chosen lawyer, if any;
  - the date of the last change.
- The list can be filtered by:
  - the user who created the case (search by username or email address);
  - category;
  - status (including *Could not be categorised*, US-03);
  - date range;
  - confidence level (e.g. only low-confidence cases);
  - chosen lawyer;
  - whether documents were uploaded.
- Several filters can be combined, and a "Clear filters" button resets them.
- The list can be sorted by any column and shows e.g. 50 cases per page, with the total number of matching cases.
- Clicking a case opens it in the admin view described in US-29. Personal data is masked and original files are not shown. Every opening is logged.
- The admin view is read-only: administrators cannot change what a client entered or the results of a case.
- Cases deleted by their owner (US-31, US-58) do not appear.

---

## Epic 4 — Architecture & Auditing I.

### US-16 · Measure classification accuracy — *Must*
**As a** researcher, **I want** to measure how accurately the system classifies cases, **so that** I can prove it works and track whether changes improve or worsen it.

**Acceptance criteria**
- A labelled test set (example problems with the correct category, decided by a person) can be stored and run against the classifier.
- The system reports overall accuracy, accuracy per category, and a confusion matrix (a table showing which categories get mixed up with which).
- It reports how often the low-confidence fallback was triggered.
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
- The server-side scripts (US-14, US-46, US-47) are not part of the API. The specification confirms that no endpoint creates, promotes or demotes administrators.

### US-38 · Route all AI calls through one gateway — *Must*
**As a** developer, **I want** every LLM call to go through a single LLM gateway, **so that** logging, cost tracking, PII protection, error handling and provider changes are handled in one place.

**Acceptance criteria**
- No module calls an LLM provider directly; code review or an automated check enforces this.
- The gateway refuses to send text that has not passed through PII masking (US-41).
- For each call it records: which module called it, which user's case it was for, model name, input and output token counts (tokens are the small chunks of text LLMs are billed by), cost, response time, and success or error.
- It applies a timeout and a limited number of retries on temporary errors.
- If all retries fail, the site shows a clear error message, e.g. "The analysis could not be completed right now. Please try again."
  - Everything the client has entered or uploaded is kept.
  - A "Try again" button repeats the failed step without the client having to re-enter anything.
  - The failure is logged (US-39).
- The LLM provider and model can be switched through configuration without code changes in other modules.

---

## Epic 5 — User Accounts & Access Control I.

### US-18 · Require registration or log-in to use the screening service — *Should*
**As a** visitor, **I want** to be told clearly that I need an account to use the legal screening service, and be taken to the registration page, **so that** I know what to do next and my data is always linked to an account I control.

**Acceptance criteria**
- The screening service covers every step from describing the problem (US-01) to seeing the chosen lawyer's contact details (US-8), and is available only to logged-in users.
- When a visitor tries to start the screening, or opens any screening page address directly, they are redirected to the registration page (US-19).
- A message at the top of the registration page explains why: "To use the legal screening service, please register or log in."
- If the visitor already has an account, they can switch to the log-in page with the "Already registered? Log in" button (US-19).
- After registering (with automatic log-in, US-20) or logging in, the user is taken straight to the start of the screening, not to the home page.
- The check happens on the server. Requests to the screening functions from someone who isn't logged in are refused with a 401 response, even if they bypass the pages.
- If a session expires during the screening, the user is asked to log in again. Afterwards they continue where they left off, and anything they had already saved is kept.
- The start page, disclaimer, privacy policy and language button stay available to visitors.
- The message appears in the visitor's chosen language (US-60).

### US-19 · Register an account with a secure password — *Should*
**As a** visitor, **I want** to register an account with a secure password, **so that** my cases are saved to my account and protected from other people.

**Acceptance criteria**
- The sign-up form asks for username, email address, password and password confirmation, plus the consent checkbox from US-55.
- The username is unique, 3–30 characters, letters, numbers and underscores only. The email address is unique and in a valid format.
- The email address is checked against the banned-email list (US-48).
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
- The registration page has a clearly visible "Already registered? Log in" button that takes the visitor to the log-in page (US-21). If they came from the screening service (US-18), they are still taken to it after logging in.
- New accounts always get the client role. The administrator role cannot be chosen at sign-up; it can only be given with the server-side scripts (US-14, US-46).

### US-20 · Be logged in automatically after registering — *Could*
**As a** new client, **I want** to be logged in automatically right after I register, **so that** I can continue straight away without typing my details again.

**Acceptance criteria**
- After successful registration, a session is created immediately, with no separate log-in step.
- A short welcome message is shown. If the client was sent to registration from the screening service (US-18), they are taken straight to the start of the screening. Otherwise they return to the page they were on before signing up (or to the start page).
- The menubar immediately shows the logged-in state (US-23).
- If registration fails, no session is created and no account is saved.

### US-21 · Log in and log out — *Must*
**As a** client or administrator, **I want** to log in with my username or email address and password, and to log out, **so that** I can access my account securely and end my session on shared devices.

**Acceptance criteria**
- A failed log-in shows one general message ("Username/email or password is incorrect") without saying which part was wrong, so attackers can't find out which accounts exist.
- After a configured number of failed attempts in a row (e.g. 5), further attempts for that account are delayed for a set time.
- Logging out ends the session on the server, not only in the browser, and returns the user to the start page.
- A session expires after a configured period of inactivity (e.g. 30 minutes).
- The log-in page has a "Forgot your password?" link (US-51).
- When a suspended or banned user logs in with the **correct** password, they are not logged in. Instead they see an account status page:
  - **Suspended by an administrator:** "Your account is suspended until [end date and time]." The date and time are shown in the user's chosen language and date format (US-61).
  - **Suspended automatically (US-52):** "Your account is temporarily suspended while an administrator reviews it." This case has no end date yet.
  - **Banned:** "Your account has been banned." No end date is shown, because a ban lasts until an administrator lifts it.
  - Every version of the page explains how to get in touch if the user thinks it is a mistake.
- The status page is shown **only** after the correct password has been entered. With a wrong password, the normal general error message appears, so nobody can find out an account's status just by trying to log in.
- No session is created for a suspended or banned user, and the menubar stays in the logged-out state (US-22).
- Once a suspension has ended or been lifted, the user can log in normally.
- Each blocked log-in is logged with the time, the username and the account status.

### US-22 · See Sign up and Log in when I'm not logged in — *Must*
**As a** visitor, **I want** to see "Sign up" and "Log in" options on the menubar, **so that** I can easily create an account or access my existing one.

**Acceptance criteria**
- When no one is logged in, the menubar shows "Sign up" and "Log in" on every page.
- "Sign up" opens the registration form (US-19); "Log in" opens the log-in form (US-21).
- The menubar does not show the profile button, "Admin", "Cases", "Users", "Warnings", "Logs" or "Metrics".

### US-23 · Use a profile menu when I'm logged in — *Must*
**As a** logged-in user, **I want** a profile button on the menubar, with a dropdown menu for my cases, editing my profile and logging out, instead of "Sign up" and "Log in", **so that** I can see I'm logged in and reach my account options in one place.

**Acceptance criteria**
- When a user is logged in, "Sign up" and "Log in" are not shown on any page. A profile button showing the user's username (and a person icon) is shown instead.
- Hovering the mouse over the profile button opens a dropdown menu with three options: "My cases", "Edit profile" and "Log out".
- Because touchscreens have no hover, the dropdown also opens when the button is tapped or clicked. It can also be opened and used with the keyboard (Tab to reach it, Enter to open, arrow keys to move, Esc to close).
- The dropdown closes when the mouse leaves it, when the user clicks elsewhere, or when an option is chosen.
- "My cases" opens the list of the user's own cases (US-30).
- "Edit profile" opens the profile page (US-24).
- "Log out" logs the user out (US-21), and the menubar switches back to the logged-out state (US-22).

### US-24 · Edit my profile and change my password — *Could*
**As a** logged-in user, **I want** to change my profile details, including my password, **so that** my account information stays up to date and secure.

**Acceptance criteria**
- The profile page is reached through "Edit profile" in the profile menu (US-23). Users can only ever see and edit their own profile.
- The user can change their username and their email address. The same rules as at registration apply (US-19): usernames and email addresses must be unique and valid, and a new email address must not be on the banned-email list.
- Changing the email address requires entering the current password, to protect the account if someone else gets access to an open session.
- The password is changed in a separate section. The user enters their current password, then the new password twice. The new password must meet the same rules as at registration (US-19), including the live strength indicator.
- After a password change, the user stays logged in on the current device but is logged out everywhere else.
- Changes are saved only when the user clicks "Save", and "Cancel" discards them. Every error names the field that is wrong, and a confirmation message appears after saving.
- The role (client or administrator) is shown but cannot be changed here.
- The same page also shows:
  - the consent status, with the option to withdraw it (US-55);
  - how long uploaded files are kept (US-56), and how long the account can be inactive before it is deleted with all its data (US-57);
  - the "Download my data" option (US-59);
  - the "Delete my account and data" option (US-58).
- Each change is logged with the field changed and the time. Passwords, old or new, are never logged.

### US-25 · See the Admin option when I'm an administrator — *Must*
**As an** administrator, **I want** an "Admin" option on the menubar when I'm logged in, **so that** I can reach the admin area quickly.

**Acceptance criteria**
- When the logged-in user has the administrator role, the menubar shows "Admin" (leading to the admin dashboard), "Cases" (leading to the list of all cases, US-15), "Users" (leading to the user list, US-48), "Warnings" (leading to warnings and suspensions, US-49), "Logs" (leading to the log viewer, US-37) and "Metrics" (leading to the metrics page, US-28), in addition to the profile button.
- If an administrator's role is removed (US-47), these options disappear the next time a page loads.

### US-26 · Not see the Admin option when I'm not an administrator — *Must*
**As a** client, **I want** the menubar to show only options I can actually use, **so that** the interface isn't confusing.

**Acceptance criteria**
- When the logged-in user does not have the administrator role, the menubar does not show "Admin", "Cases", "Users", "Warnings", "Logs" or "Metrics".
- Hiding the option is only for convenience; it is **not** the security measure. Access is actually blocked on the server (US-27, US-28).

### US-27 · Block the admin page for visitors who aren't logged in or administrators — *Must*
**As an** administrator, **I want** the admin page to be unreachable for anyone who is not logged in, **so that** lawyer data and categories cannot be viewed or changed by strangers.

**Acceptance criteria**
- A visitor who types an admin page address directly into the browser is redirected to the log-in page and sees no admin content.
- If they then log in as an administrator, they are taken to the page they originally asked for. If they log in as a client, they see the "Access denied" page described below.
- Every request to the admin functions from outside the pages (e.g. calling the server directly) is refused with a 401 response.
- These checks happen on the server, so they cannot be bypassed by changing anything in the browser.
- A logged-in client who opens an admin page address sees an "Access denied" page (403 response) and no admin content.
- Every request to the admin functions from a non-admin account is refused with a 403 response.
- Each refused attempt is logged with the username, the address requested and the time.

### US-28 · Restrict the metrics page to be available only for administrators — *Must*
**As an** administrator, **I want** the metrics page to be available only to administrators, **so that** internal performance, cost and usage figures are not visible to the public.

**Acceptance criteria**
- The metrics page contains the dashboards and exports from US-16, US-39 and US-50.
- Visitors who are not logged in are redirected to the log-in page (as in US-27). Logged-in non-admins see "Access denied" (as in US-27).
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
- A client can open only their own cases (from the "My cases" list, US-30).
- If a client tries to open another user's case, for example by changing the case number in the web address, they get a "Not found" page (404 response).
  - The page reveals nothing about the case, not even that it exists.
  - The attempt is logged with the username, the case requested and the time.
- Case numbers in web addresses are long random identifiers (e.g. a UUID, Universally Unique Identifier) rather than 1, 2, 3…, so they cannot be guessed.
- Administrators can open any case from the admin case list (US-15).
  - Personal data in the problem description and extracted text is shown masked (US-41).
  - Original uploaded files are not shown to administrators.
- Every time an administrator opens a case, this is logged with the administrator's username, the case and the time.
- The checks happen on the server for every request: case pages, documents, recommendations, contact details and data exports. The browser alone cannot get around them.
- Cases are not shared with the recommended lawyers. The client decides whether to contact a lawyer (US-8).
- The metrics page (US-28) shows only totals and averages, never individual cases.
- When a client deletes their account (US-58), their cases disappear for administrators too.

### US-30 · See a list of my cases — *Must*
**As a** client, **I want** a "My cases" page listing all the cases I have submitted, **so that** I can look at earlier results again, find a lawyer's contact details later, or continue a case I didn't finish.

**Acceptance criteria**
- The page is reached through "My cases" in the profile menu (US-23).
- It lists only the logged-in client's own cases (US-29), newest first, 20 per page.
- Each row shows:
  - the date the case was created;
  - a short title made from the first words of the problem description;
  - the legal category, in plain language with the legal term in smaller text below (as in US-4);
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
  - the three recommendations with their explanations (US-7);
  - the chosen lawyer's contact details (US-8).
- On the detail page, the problem description, answers and document data are shown in their original, unmasked version (US-41).
- Recommendations are shown as they were when the case was completed. If a recommended lawyer has since been deactivated, a note says they no longer accept clients through the platform.
- Once the uploaded files have been deleted after the file retention period (US-56), the case still shows its results and the extracted document data, with a note saying the files were deleted and when.
- Unfinished cases have a "Continue" button that returns the client to the step where they stopped.
- A client who has chosen a lawyer can still choose a different one of the three from the detail page (as in US-8).
- A "New case" button starts a new screening.
- If the client has no cases yet, the page says so and shows a button to start their first screening.
- Every case in the list has a delete option next to it (US-31).
- All text on the page appears in the client's chosen language (US-60).


### US-31 · Delete a single case — *Could*
**As a** client, **I want** a delete option next to each of my cases, **so that** I can remove one case completely without deleting my whole account.

**Acceptance criteria**
- Every case in "My cases" (US-30) has a delete button (a bin icon with the label "Delete") next to it. The same button is also on the case detail page.
- A confirmation dialog names the case by its date and title, lists what will be deleted, and says that deletion cannot be undone.
- After confirmation, everything stored for that case is permanently deleted:
  - the description and answers;
  - the stored uploaded files, extracted text and data;
  - the classification;
  - the recommendations with their explanations;
  - the lawyer choice;
  - the PII mapping for that case.
- Only that case is affected. The client's other cases and their account stay unchanged.
- The case disappears immediately from the client's list and from the admin case list (US-15).
- Metrics keep only anonymous totals that cannot be traced back to the deleted case.
- The deletion is logged with the case ID, the user and the time, never the deleted content.
- The server checks that the case belongs to the user, so nobody can delete another user's case (US-29).

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