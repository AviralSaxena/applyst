# AppLyst

**AppLyst is an AI-powered job application tracker that connects directly to your email inbox and automatically detects the status of your job applications.** Forget manual updates; AppLyst offers a fully automated experience using artificial intelligence and real-time email parsing, helping job seekers stay organized and efficient.

## What It Does

AppLyst scans your inbox for job-related communication, intelligently detects and updates the status of your applications using NLP, and displays all progress in a centralized, user-friendly dashboard. It's built for active job seekers who manage many applications without losing track or wasting time on spreadsheets.

### Key Capabilities:

* **Secure Email Connection:** Integrates securely with Gmail and other inboxes using OAuth 2.0.
* **Intelligent Parsing:** Automatically detects job application emails and extracts key details like company name, position title, application date, and critical status updates (e.g., Interview Scheduled, Offer, Rejection).
* **Automated Tracking:** Adds or updates applications in your dashboard without you lifting a finger.
* **AI-Powered Insights:** Uses AI/NLP to infer application status even when it's not explicitly stated.
* **Smart Notifications:** Sends optional, timely alerts for interview invitations, "ghosting" detection (no response in X days), and status changes.
* **Centralized Dashboard:** Offers a clear, filterable, and searchable view of all your applications.
* **Privacy-First Design:** Engineered with security and user privacy at its core; no email data is stored without explicit consent.

---

## Architecture Overview

AppLyst is a distributed system, breaking down complex tasks into specialized, scalable services:

* **Frontend (`client/`):** The user-facing web application, built with **React.js** and styled with **TailwindCSS**. This is what users interact with directly in their browser.
* **Backend (`server/`):** A core API server built with **Node.js** and **Express**. It handles data requests from the frontend and orchestrates communication with the database and NLP engine.
* **AI/NLP Engine (`nlp-engine/`):** A dedicated **Python microservice** leveraging libraries like `spaCy` or **OpenAI**. Its job is to parse email content and intelligently determine application statuses.
* **Database:** For persistent storage of all application data, AppLyst can utilize either **MongoDB** (for flexible, document-based storage) or **PostgreSQL** (for robust relational data management).
* **Email Integration:** Seamlessly connects to email services like Gmail via their official APIs (e.g., Gmail API) for secure OAuth and message fetching.

---

## Project Structure
applyst/
├── client/                  # (Optional) Frontend UI or client script
│   └── client.py            # Current frontend logic

├── server/                  # Backend application
│   ├── app.py               # Entry point (e.g., FastAPI or Flask app)
│   ├── models.py            # Database models or schemas
│   ├── email_scanner.py     # Email parsing and analysis logic
│   ├── routes/              # API endpoints (e.g., auth.py, user.py)
│   ├── utils/               # Helper utilities (e.g., token_gen.py, validators.py)
│   └── services/            # Business logic (e.g., email_service.py, user_service.py)

├── tests/                   # Unit and integration tests
│   └── test_app.py          # Example test file

├── .gitignore               # Git ignore rules
├── README.md                # Project documentation
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables (never push to Git)

## Installation Instructions

To get AppLyst running on your local machine, you'll need to set up each major component:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/AviralSaxena/applyst.git](https://github.com/AviralSaxena/applyst.git)
    cd applyst
    ```

2.  **Frontend (`client/`) Setup:**
    Navigate into the `client` directory, install its Node.js dependencies, and then start the development server:
    ```bash
    cd client
    npm install
    # If your client needs specific environment variables (e.g., API keys for the backend),
    # create a `.env` file based on a `.env.example` if provided.
    npm start # Or `npm run dev` if you're using a Next.js setup.
    ```

3.  **Backend (`server/`) Setup:**
    Switch to the `server` directory, install your Python dependencies, and set up environment variables before running the server:
    ```bash
    cd ../server
    pip install -r requirements.txt # Assumes a requirements.txt file for Python backend.
    # Create a `.env` file for your backend, mirroring a `.env.example` if available.
    # This will contain sensitive information like database credentials and email server details.
    # Example: `cp .env.example .env`
    # Run your Flask application:
    flask run
    ```

4.  **NLP Engine (`nlp-engine/`) Setup:**
    (If you add this directory for a separate NLP microservice):
    ```bash
    cd ../nlp-engine
    python -m venv venv
    source venv/bin/activate # On Windows, use: `venv\Scripts\activate`
    pip install -r requirements.txt
    cp .env.example .env # Configure any necessary API keys (e.g., OpenAI).
    # Run your NLP service (e.g., `python app.py`).
    ```

5.  **Database Setup:**
    The database setup will depend on your chosen database (MongoDB or PostgreSQL). Refer to the `database/` directory (if you create one) for specific schema and migration instructions. You'll likely need to start your database server separately.

---

## Running the Application

For AppLyst to function fully, all its core services—the Frontend, Backend, NLP Engine, and your Database—need to be running concurrently.

* **Frontend:** `cd client && npm start`
* **Backend:** `cd server && flask run`
* **NLP Engine:** `cd nlp-engine && source venv/bin/activate && python app.py` (or whatever your run command is)

---

## Running Tests

### Frontend End-to-End Tests (Cypress)

From the `client/` directory, you can execute your end-to-end tests to ensure the user interface behaves as expected:

```bash
cd client
npx cypress open # To open the Cypress Test Runner GUI for interactive testing.
# npx cypress run # To run tests headlessly, which is perfect for CI/CD pipelines.
