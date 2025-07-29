# Applyst - Auto Job Application Tracker

Automatically tracks job applications from Gmail using AI analysis.

## Setup

1. **Get API Keys**
   - [Gmail OAuth](https://console.developers.google.com) - Create credentials for Desktop app
   - [Gemini AI](https://aistudio.google.com/app/apikey) - Get API key

2. **Configure**
   ```bash
   cp .env-example .env
   # Edit .env with your API keys
   ```

3. **Run**
   ```bash
   python setup_and_run.py
   ```

The script handles everything - virtual environment, dependencies, and launches both frontend and backend.

Access at: http://localhost:8501