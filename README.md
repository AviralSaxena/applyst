# AppLyst

**AppLyst** is an AI-powered job application tracker that connects directly to your email inbox and automatically detects the status of your job applications. Unlike traditional tracking tools that require constant manual updates, AppLyst offers a fully automated experience using artificial intelligence and real-time email parsing.

It helps job seekers stay organized, informed, and efficient throughout the application process — eliminating the guesswork, clutter, and repetition.

---
## What It Does

AppLyst scans your inbox for job-related communication, detects and updates the status of your applications using NLP, and displays all progress in a centralized, user-friendly dashboard. It is designed for active job seekers who need to manage dozens of applications without losing track or wasting time updating spreadsheets.

---

## Key Capabilities

- Connects securely to Gmail or other inboxes using OAuth 2.0
- Detects job application emails and parses content for:
  - Company name
  - Position title
  - Application date
  - Status updates (e.g., Interview Scheduled, Offer, Rejection)
- Automatically adds or updates applications in your dashboard
- Uses AI/NLP to infer status when not explicitly stated
- Sends optional smart notifications for:
  - Interview invitations
  - Ghosting detection (no response in X days)
  - Status changes
- Centralized dashboard view with filters and search
- Secure and privacy-conscious design; no email data stored without consent

---

## Architecture Overview

- **Frontend:** React.js with TailwindCSS for responsive UI
- **Backend:** Node.js with Express for RESTful API services
- **AI/NLP Engine:** Python microservice using spaCy or OpenAI for parsing email contents
- **Database:** MongoDB or PostgreSQL for storing application data
- **Email Integration:** Gmail API for OAuth and message fetching

---

## Project Structure

```bash
AppLyst/
├── client/           # Frontend application (React)
├── server/           # Backend services (Node.js + Express)
├── nlp-engine/       # NLP model and logic (Python)
├── database/         # DB schemas and scripts
├── docs/             # Diagrams, research, and notes
└── README.md         # Project overview
