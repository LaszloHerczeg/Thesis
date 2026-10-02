User Intake & Interaction

Text-based problem submission: Users can describe their legal problem in their own words.

Dynamic Q&A: The system asks structured follow-up questions to gather missing information based on the initial input.

Low-confidence fallback: If the system is uncertain about a classification, it prompts the user for clarification or explicitly states it cannot confidently categorize the issue.

Disclaimer display: Clear product boundaries stating the system provides preliminary screening, not definitive legal advice or interpretation.

Document Processing

PDF text extraction: Native text extraction from digital PDFs.

Conditional OCR: Optical Character Recognition specifically triggered for scanned or image-based documents.

PII detection & masking: Automatic identification and anonymization of sensitive personal data within uploaded documents.

Traceable data extraction: Structured field extraction that shows the user exactly which page or text snippet the information was pulled from.

Human-in-the-loop verification: Prompts requiring user confirmation when document extraction yields low-reliability data.

AI Classification & Recommendation Engine

Case-type classification: Categorizes the user's issue into a predefined taxonomy of 6–8 specific legal areas, accompanied by a confidence score.

Multi-criteria content-based recommendation: Suggests exactly three relevant lawyer profiles based on matching criteria (specialty, location, language, consultation format, availability, and fee model).

Explainable AI (XAI): Displays the specific reasons and matching logic behind why those top three lawyer profiles were recommended.

Administration & Management

Admin interface: A dashboard to manage lawyer profiles and the legal category taxonomy.

Lawyer profile schema: Structured profiles containing specific data points (expertise, location, languages spoken, online/in-person availability, pricing model).

Architecture & Auditing

Modular architecture: Distinct modules for client intake, document processing, classification/recommendation, LLM gateway, and auditing.

Audit and measurement module: Built-in tracking for system performance, including classification accuracy, response times, API costs, error patterns, and task completion rates.

AI usage logging: A tracked log of AI usage during the development process to compare AI-supported workflows against standard development.