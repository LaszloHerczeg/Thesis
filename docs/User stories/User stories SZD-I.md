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
| **API** (Application Programming Interface) | A defined way for one piece of software to request something from another, e.g. your backend asking an AI provider to categorize text. |
| **Authentication / Authorisation** | Authentication checks *who* you are (logging in). Authorisation checks *what you are allowed to do* once logged in (e.g. only admins may open the admin page). |
| **Command-line interface (CLI)** | A text-only way of running programs by typing commands into a terminal on the server, instead of clicking in a web page. A "CLI script" is a small program run this way. |
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
| **Prompt injection** | An attack where text given to an AI (e.g. hidden in a document) tries to act as new instructions, such as "ignore your instructions and categorize this as…". |
| **Rate limiting** | Capping how many requests a user or device can make in a given time, to stop bots and misuse. |
| **Retention period** | How long a piece of data is kept before it is automatically deleted. |
| **Role** | The type of account a user has (here: client or administrator), which decides what they may see and do. |
| **Suspension / Ban** | A **suspension** blocks an account temporarily, until a set end date or until an administrator lifts it. A **ban** blocks an account indefinitely: it stays in force until an administrator lifts it. |
| **Session** | The system's record that a browser is currently logged in, usually kept via a small cookie (a piece of data stored by the browser). |
| **Taxonomy** | The fixed list of categories the system sorts cases into (here: a set of legal areas managed by the administrator). |
| **XAI** (Explainable AI) | AI whose outputs come with human-understandable reasons for why that output was produced. |
| **ZIP file** | A single compressed file that contains several other files. |

### User roles

| Role | Who they are |
|---|---|
| **Visitor** | Anyone using the site without being logged in. Visitors can see the start page and privacy policy, and can register or log in, but cannot use the screening service. |
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
- When the description is submitted, it is saved in its original version.

### US-02 · Answer follow-up questions — *Must*
**As a** client, **I want** the system to ask me targeted follow-up questions about information I left out, **so that** my case is understood correctly without me having to guess what matters.

**Acceptance criteria**
- After submission, the system identifies missing key information (e.g. dates, the other party, location/jurisdiction, whether money is involved) and asks about it.
- Questions are structured (pick-one multiple choice, yes/no, date picker, or short text) rather than open-ended where possible.
- No more than a configurable number of questions per round (e.g. 5), and no more than a configurable number of rounds (e.g. 2), to avoid tiring the client.
- The client can skip any question; skipped questions are recorded as "not answered", not as a negative answer.
- Answers are stored the same way as the description (US-01).

### US-03 · Be told honestly when my problem can't be categorized — *Must*
**As a** client, **I want** the system to tell me clearly when it cannot categorize my issue, **so that** I am not misled by a guess.

**Acceptance criteria**
- If the case can not be categorized, the system shows an explicit message: "Your case can not be categorized".
- The case's status is set to "uncategorized".

---

## Epic 2 — Categorization & Recommendation Engine

### US-04 · Get my problem categorized into a legal area — *Must*
**As a** client, **I want** my problem to be sorted into the right legal area, **so that** I know what kind of lawyer I need.

**Acceptance criteria**
- Categorization uses the client's description, follow-up answers as input.
- The output is exactly one category from the current taxonomy.
- If categorization is unsuccessful, US-02 / US-03 apply instead of showing results.
- The input, output, categorization mode and response time are logged.

### US-05 · State my preferences for a lawyer — *Should*
**As a** client, **I want** to state my preferences (location, language, online or in-person consultation, hourly wage), **so that** the recommendations fit my practical situation.

**Acceptance criteria**
- The client can set: location (city), language(s), consultation format (online / in-person / either) and preferred hourly rate.
- The preferences can be given by the client on the screening page, below the description of the case.
- The hourly wage is the maximum price that the client is willing to pay hourly.
- City is free text, language is a list, consultation format is list, preferred hourly rate is free text, and it is in HUF.
- If any of the dereferences is left blank, that means that the client has no preference, so the lawyers will not be filtered by that category.

### US-06 · Receive three lawyer recommendations at most — *Must*
**As a** client, **I want** to receive the three best-matching lawyer profiles, **so that** I have a short, manageable choice instead of a long list.

**Acceptance criteria**
- Matching compares the case category and the client's preferences against lawyer profiles on five criteria: specialty, location, language, consultation format and hourly wage.
- All five criteria is a required match: if they don't match, the lawyer is not recommended.
- The client's preference for hourly wage is the maximum that the client is willing to pay hourly. If the lawyer's hourly wage is lower than the client's preference, that's a match for that criteria.
- Maximum of three profiles are shown. If fewer than three lawyers match all required preferences, only the matching profiles are shown.
- The same input with the same lawyer data always produces the same result (deterministic ranking; ties broken by a fixed rule).
- If there are 0 matches, a message of "There are no matching lawyers" is shown.

### US-07 · Understand why each lawyer was recommended — *Must*
**As a** client, **I want** to see why each lawyer was recommended, **so that** I can trust the recommendation and choose between the three.

**Acceptance criteria**
- Each recommended profile shows a per-criterion breakdown, e.g. ✓ Specialty: tenancy law · ✓ Speaks Hungarian · ✓ Online consultations · ✗ Location.
- A one-sentence plain-language summary explains the main reason for the recommendation.

### US-08 · See the recommended lawyer's contact details — *Could*
**As a** client, **I want** to see the contact details of the lawyer I pick from the three recommendations, **so that** I can get in touch with them directly.

**Acceptance criteria**
- Each of the three recommended profiles are shown instantly
- The client sees the lawyer's name, city, email address, consultation format and hourly wage.
- The client's own details are **not** sent to the lawyer; the client decides whether and how to make contact.

### US-09 · Rule-based Categorization — *Must*
**As a** client, **I want** the system to categorize my case, **so that** I can find the best lawyer for me.

**Acceptance criteria**
- The system chooses a field following the categorization rules according to the data extracted from the client's description.
- The output is sent to the same interface as the LLM-based categorization.
- If the system needs more information, the system gives appropriate answer (e.g "More information needed")
- If the case can not be categorized, the system gives appropriate answer (e.g. "Not supported")

### US-35 . AI Categorization - *Must*
**As a** client, **I want** the system to categorize my case **so that** I can find the most suitable lawyer.
**Acceptance criteria**
- The extracted information from the description is sent to the LLM.
- The LLM is asked to send the category back in a fixed format.
- If the LLM needs more information to categorize the case, follow-up questions are asked.
- If the case can not be categorized, the system gives appropriate answer (e.g. "Not supported")
- The answer is always checked (US-36).

### US-36 · Check that the AI's answer is a real category — *Must*
**As a** client, **I want** the system to check the AI's answer before it is used, **so that** I am never shown a category that doesn't exist or a broken result.

**Acceptance criteria**
- The LLM is asked to answer in a fixed JSON format.
- In the JSON there are 3 name-value pairs:
  - is_successful,
  - category_id
  - follow_up_question.
- If the categorization is successful, the is_successful must be set to true and the category_id must be set to the id of the category in the taxonomy, the follow_up_question must be set to null.
- If follow-up questions are needed, is_successful must be set to false, category_id to null and follow_up_question contains the questions needed to be answered.
- If the case can not be categorized, is_successful must be se to true, both category_id and follow_up_question must be set to null.
- Before the answer is used, the system checks that:
  - the answer can be read in the expected format and has all required fields;
- If the answer is invalid, A message of "Invalid answer from AI" is displayed for the client.

---

## Epic 3 — Administration & Management I.

### US-10 · Access the admin area securely — *Must*
**As an** administrator, **I want** a login-protected admin dashboard, **so that** only authorized staff can change lawyer data, see all the cases and categories.

**Acceptance criteria**
- Only users with the administrator role can access the admin interface (access rules in detail: US-25 to US-27).

### US-11 · Create and edit lawyer profiles — *Should*
**As an** administrator, **I want** to create, edit and view lawyer profiles, **so that** the recommendation engine always works from accurate data.

**Acceptance criteria**
- Profiles can be created, edited, searched and filtered by any schema field.
- Changes take effect in recommendations immediately after saving.

### US-12 · Enforce a structured profile schema — *Should*
**As an** administrator, **I want** every lawyer profile to follow the same structured format, **so that** matching is fair and reliable across all lawyers.

**Acceptance criteria**
- Required fields: name, contact details (email address), areas of expertise (one or more, chosen from the taxonomy), office location (city), languages spoken, consultation formats (online / in-person), and hourly rate.
- Areas of expertise and languages are chosen from fixed lists, not typed freely, to avoid spelling variants.
- A profile cannot be saved if any required field is missing or invalid; the form shows which field is wrong.

### US-13 · Manage the legal category taxonomy — *Should*
**As an** administrator, **I want** to manage the list of legal categories, **so that** the system's categories match the lawyers and case types we actually handle.

**Acceptance criteria**
- Each category has a name and a category identifier both entered in Hungarian.
- A category that is still assigned to lawyers cannot be removed until those lawyers are reassigned; the admin is shown which lawyers are affected.
- Changes to the taxonomy are versioned, and each categorization records which taxonomy version it used (so accuracy can be compared fairly over time).
- The category identifier and the name is typed by the admin.

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
**As an** administrator, **I want** an "All Cases" menu item that lists all existing cases with filters, **so that** I can review cases, find ones that could not be categorized, and check how the system is being used.

**Acceptance criteria**
- Logged-in administrators see "Cases" on the Admin dashboard (US-25). The page follows the same access rules as the admin area: unreachable for visitors and for non-admins (US-27).
- The list shows one row per case, with:
  - the creation date;
  - the case number;
  - the username of the client who created it;
  - the category (the legal term);
  - the status;
  - preferences provided by the client
- The list can be filtered by:
  - the user who created the case (search by username or email address);
  - category;
  - status (including *uncategorized*, US-03);
  - date range;
- The list can be sorted by any column and shows e.g. 50 cases per page, with the total number of matching cases.
- Clicking a case opens it in the client's detail page (US-30), read-only.
- The admin view is read-only: administrators cannot change what a client entered or the results of a case.
- Cases deleted by their owner (US-31) do not appear.

---

## Epic 4 — Architecture & Auditing I.

### US-16 · Measure categorization accuracy — *Must*
**As a** researcher, **I want** to measure how accurately the system categorizes cases, **so that** I can prove it works and track whether changes improve or worsen it.

**Acceptance criteria**
- A labeled test set (example problems with the correct category, decided by a person) can be stored and run against the categorizer.
- The system reports overall accuracy, accuracy per category, and a confusion matrix (a table showing which categories get mixed up with which).
- Each evaluation run is saved with the date, categorization mode and taxonomy version so results can be compared. These data are shown on the metrics page (US-25).

### US-17 · Describe the API in an OpenAPI specification — *Must*
**As a** developer, **I want** the server's whole API described in an OpenAPI specification, **so that** the frontend and backend agree on exact data formats, and the API can be tested and documented automatically.

**Acceptance criteria**
- An OpenAPI 3 document describes every API endpoint the website uses. An endpoint is a single address on the server that the website calls, such as "create a case" or "log in". This covers:
  - accounts and log-in;
  - screening, cases and recommendations;
  - admin functions, cases and metrics.
- For each endpoint, the document states:
  - its address and method (e.g. GET for reading data, POST for sending new data);
  - its inputs and response formats;
  - the errors it can return (e.g. 400, 401, 403, 404, 429);
  - which role may use it: visitor, client or administrator.
- Shared data structures, such as case, category, lawyer profile and recommendation, are defined once and reused.
- The specification is kept in sync with the code: it is either generated from the code, or automated tests check that real API responses match it. The build fails if they don't match.
- An interactive documentation page (e.g. Swagger UI) is available during development. In production, it is switched off or available to administrators only.
- The specification has a version number that is increased whenever the API changes.
- The server-side script (US-14) is not part of the API. The specification confirms that no endpoint creates, promotes or demotes administrators.

---

## Epic 5 — User Accounts & Access Control I.

### US-18 · Require registration or log-in to use the screening service — *Should*
**As a** visitor, **I want** to be told clearly that I need an account to use the legal screening service, and be taken to the login page, **so that** I know what to do next and my data is always linked to an account I control.

**Acceptance criteria**
- The screening service covers every step from describing the problem (US-01) to seeing the recommended lawyers' contact details (US-8), and is available only to logged-in users.
- When a visitor tries to start the screening, or opens any screening page address directly, they are redirected to the login page (US-19).
- A message at the top of the login and the registration page explains why: "To use the legal screening service, please register or log in."
- If the visitor does not have an account, they can switch to the registration page with the "Register" button (US-19).
- After registering (with automatic log-in, US-20) or logging in, the user is taken straight to the start of the screening, not to the home page.
- The check happens on the server. Requests to the screening functions from someone who isn't logged in are refused with a 401 response, even if they bypass the pages.
- The start page and privacy policy stay available to visitors.

### US-19 · Register an account with a secure password — *Should*
**As a** visitor, **I want** to register an account with a secure password, **so that** my cases are saved to my account and protected from other people.

**Acceptance criteria**
- The sign-up form asks for username, email address, password and password confirmation.
- The username is unique, 8–30 characters, letters, numbers and underscores only. The email address is unique and in a valid format.
- Password rules follow modern practice based on NIST guidance (SP 800-63B):
  - Minimum length of 8 characters. The limit is a configurable setting, so it can be raised later without changing the code.
  - Maximum length of 12 characters. Only a-z characters are allowed.
  - **No** forced composition rules such as "must contain an uppercase letter, a number and a symbol". These make passwords harder to remember without making them much stronger.
  - The password is rejected if it appears in a list of known leaked passwords or common passwords, or if it contains the username, the email address or the site's name. The client is told *why* it was rejected.
- A live strength indicator shows how strong the password is while it is typed.
- A "show password" toggle is available, and pasting is allowed so password managers work.
- Passwords are stored only as hashes (Argon2id or bcrypt), never as plain text.
- Every error message names the field that is wrong and how to fix it, and the form keeps everything else the visitor typed.
- The registration page has a clearly visible "Already registered? Log in" button that takes the visitor to the log-in page (US-21). If they came from the screening service (US-18), they are still taken to it after logging in.
- New accounts always get the client role. The administrator role cannot be chosen at sign-up; it can only be given with the server-side script (US-14).

### US-20 · Be logged in automatically after registering — *Could*
**As a** new client, **I want** to be logged in automatically right after I register, **so that** I can continue straight away without typing my details again.

**Acceptance criteria**
- After successful registration, a session is created immediately, with no separate log-in step.
- A short welcome message is shown. If the client was sent to registration from the screening service (US-18), they are taken straight to the start of the screening. Otherwise, they return to the page they were on before signing up (or to the start page).
- The menubar immediately shows the logged-in state (US-23).
- If registration fails, no session is created and no account is saved.

### US-21 · Log in and log out — *Must*
**As a** client or administrator, **I want** to log in with my username or email address and password, and to log out, **so that** I can access my account securely and end my session on shared devices.

**Acceptance criteria**
- A failed log-in shows one general message ("Username/email or password is incorrect") without saying which part was wrong, so attackers can't find out which accounts exist. Non-existent usernames behave the same way.
- Logging out ends the session on the server, not only in the browser, and returns the user to the start page.

### US-22 · See Sign up and Log in when I'm not logged in — *Must*
**As a** visitor, **I want** to see "Sign up" and "Log in" options on the menubar, **so that** I can easily create an account or access my existing one.

**Acceptance criteria**
- When no one is logged in, the menubar shows "Sign up" and "Log in" on every page.
- "Sign up" opens the registration form (US-19); "Log in" opens the log-in form (US-21).
- The menubar does not show the profile button or "Admin".

### US-23 · Use a profile menu when I'm logged in — *Must*
**As a** logged-in user, **I want** a profile button on the menubar, with a dropdown menu for my cases, editing my profile and logging out, instead of "Sign up" and "Log in", **so that** I can see I'm logged in and reach my account options in one place.

**Acceptance criteria**
- When a user is logged in, "Sign up" and "Log in" are not shown on any page. A profile button showing the user's username (and a person icon) is shown instead.
- Hovering the mouse over the profile button opens a dropdown menu with three options: "My cases", "Edit profile" and "Log out".
- The dropdown closes when the mouse leaves it, when the user clicks elsewhere, or when an option is chosen.
- "My cases" opens the list of the user's own cases (US-30).
- "Edit profile" opens the profile page (US-24).
- "Log out" logs the user out (US-21), and the menubar switches back to the logged-out state (US-22).
- Phone and tablet friendly features will not be implemented yet.

### US-24 · Edit my profile and change my password — *Could*
**As a** logged-in user, **I want** to change my profile details, including my password, **so that** my account information stays up to date and secure.

**Acceptance criteria**
- The profile page is reached through "Edit profile" in the profile menu (US-23). Users can only ever see and edit their own profile.
- The user can change their username and their email address. The same rules as at registration apply (US-19): usernames and email addresses must be unique and valid.
- Changing the email address requires entering the current password, to protect the account if someone else gets access to an open session.
- The password is changed in a separate section. The user enters their current password, then the new password twice. The new password must meet the same rules as at registration (US-19), including the live strength indicator.
- After a password change, the user stays logged in on the current device but is logged out everywhere else.
- Changes are saved only when the user clicks "Save", and "Cancel" discards them. Every error names the field that is wrong, and a confirmation message appears after saving.

### US-25 · See the Admin option when I'm an administrator — *Must*
**As an** administrator, **I want** an "Admin" option on the menubar when I'm logged in, **so that** I can reach the admin area quickly.

**Acceptance criteria**
- When the logged-in user has the administrator role, the menubar shows "Admin" (leading to the admin dashboard), in addition to the profile button.
- In the admin  dashboard, 4 options are available: Taxonomy, Create and Edit Lawyer profiles, All Cases and Metrics.

### US-26 · Not see the Admin option when I'm not an administrator — *Must*
**As a** client, **I want** the menubar to show only options I can actually use, **so that** the interface isn't confusing.

**Acceptance criteria**
- When the logged-in user does not have the administrator role, the menubar does not show "Admin".
- Hiding the option is only for convenience; it is **not** the security measure. Access is actually blocked on the server (US-27, US-28).

### US-27 · Block the admin page for visitors who aren't logged in or administrators — *Must*
**As an** administrator, **I want** the admin page to be unreachable for anyone who is not logged in, **so that** lawyer data, metrics and categories cannot be viewed or changed by strangers.

**Acceptance criteria**
- A visitor who types an admin page address directly into the browser is redirected to the log-in page and sees no admin content.
- If they then log in as an administrator, they are taken to the page they originally asked for. If they log in as a client, they see the "Access denied" page described below.
- Every request to the admin functions from outside the pages (e.g. calling the server directly) is refused with a 401 response.
- These checks happen on the server, so they cannot be bypassed by changing anything in the browser.
- A logged-in client who opens an admin page address sees an "Access denied" page (403 response) and no admin content.
- Every request to the admin functions from a non-admin account is refused with a 403 response.

### US-28 · Restrict the metrics page to be available only for administrators — *Must*
**As an** administrator, **I want** the metrics page to be available only to administrators, **so that** internal performance, cost and usage figures are not visible to the public.

**Acceptance criteria**
- The metrics page contains the dashboards from US-16.
- Visitors who are not logged in are redirected to the log-in page (as in US-27). Logged-in non-admins see "Access denied" (as in US-27).

### US-29 · Keep each case private to its owner and administrators — *Must*
**As a** client, **I want** my case and its recommendations to be visible only to me and to administrators, **so that** no other user can see my legal problem or which lawyer I chose.

**Acceptance criteria**
- Every case is linked to the account that created it.
- A case includes everything stored with it:
  - the problem description;
  - follow-up questions and answers;
  - the category;
  - the status;
  - the three recommendations and their explanations;
  - the preferences given by the client.
- A client can open only their own cases (from the "My cases" list, US-30).
- If a client tries to open another user's case, for example by changing the case number in the web address, they get a "Not found" page (404 response).
  - The page reveals nothing about the case, not even that it exists.
- Case numbers in web addresses are long random identifiers (e.g. a UUID, Universally Unique Identifier) rather than 1, 2, 3…, so they cannot be guessed.
- Administrators can open any case from the admin case list (US-15).
- The checks happen on the server for every request: case pages, recommendations, contact details. The browser alone cannot get around them.
- Cases are not shared with the recommended lawyers. The client decides whether to contact a lawyer (US-8).
- The metrics page (US-28) shows only totals and averages, never individual cases.

### US-30 · See a list of my cases — *Must*
**As a** client, **I want** a "My cases" page listing all the cases I have submitted, **so that** I can look at earlier results again, find a lawyer's contact details later, or continue a case I didn't finish.

**Acceptance criteria**
- The page is reached through "My cases" in the profile menu (US-23).
- It lists only the logged-in client's own cases (US-29), newest first, 20 per page.
- Each row shows:
  - the date the case was created;
  - the legal category;
  - the status;
- The possible statuses are:
  - *categorized*
  - *uncategorized*.
- The client can filter the list by status and category.
- Clicking a case opens its detail page, which shows:
  - the problem description and follow-up answers;
  - the category and status;
  - the three recommendations with their explanations (US-7);
  - the preferences
- A "New case" button starts a new screening.
- If the client has no cases yet, the page says so and shows a button to start their first screening.
- Every case in the list has a delete option next to it (US-31).

### US-31 · Delete a single case — *Could*
**As a** client, **I want** a delete option next to each of my cases, **so that** I can remove one case completely without deleting my whole account.

**Acceptance criteria**
- Every case in "My cases" (US-30) has a delete button (a bin icon with the label "Delete") next to it. The same button is also on the case detail page.
- After pressing delete, a confirmation question appears ("Are you sure?") with a yes and no option.
- After confirmation, everything stored for that case is permanently deleted:
  - the description and answers;
  - the category;
  - the status;
  - the recommendations with their explanations;
  - preferences.
- Only that case is affected. The client's other cases and their account stay unchanged.
- The case disappears immediately from the client's list and from the admin case list (US-15).
- Metrics keep only anonymous totals that cannot be traced back to the deleted case.
- The server checks that the case belongs to the user, so nobody can delete another user's case (US-29).

---

# Summary

## SZD-I. Summary

| Epic | Stories | Must | Should | Could |
|---|---|---|---|---|
| 1 · Client Intake & Interaction | US-01 – US-03 | 3 | 0 | 0 |
| 2 · Categorization & Recommendation | US-4 – US-9, US-35 - US-36 | 5 | 1 | 2 |
| 3 · Administration & Management I. | US-10 – US-15 | 2 | 3 | 1 |
| 4 · Architecture & Auditing I. | US-16 – US-17, US-38 | 3 | 0 | 0 |
| 5 · User Accounts & Access Control I. | US-18 – US-31 | 9 | 2 | 3 |
| **Total** | **34** | **22** | **6** | **6** |