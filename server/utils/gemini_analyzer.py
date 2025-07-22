import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiEmailAnalyzer:
    
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key.strip() == '' or api_key.strip() == "''":
            raise ValueError("❌ GEMINI_API_KEY environment variable is required and cannot be empty. Please set it in the .env file.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def analyze_email_for_interview_stage(self, subject, body, sender_email=""):
        prompt = f"""
        Analyze this email and extract job application information:
        
        Subject: {subject}
        Body: {body}
        Sender: {sender_email}
        
        Extract the following information:
        1. Company name
        2. Job title/position
        3. Interview stage (choose from: application_received, phone_screen, technical_interview, 
           behavioral_interview, final_interview, offer, rejected, other)
        4. Confidence level (0-100) based on how certain you are
        
        Return the response in this exact JSON format:
        {{
            "company_name": "extracted company name or null",
            "job_title": "extracted job title or null", 
            "interview_stage": "stage or null",
            "confidence": confidence_score
        }}
        
        Only return the JSON, no other text.
        """
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            import json
            import re
            
            json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group(1).strip()
            
            result = json.loads(result_text)
            
            def clean_value(value):
                return None if value in [None, 'null', ''] else (value.strip() if isinstance(value, str) else value)
            
            return {
                'company_name': clean_value(result.get('company_name')),
                'job_title': clean_value(result.get('job_title')),
                'interview_stage': clean_value(result.get('interview_stage')),
                'confidence': int(result.get('confidence', 0))
            }
            
        except Exception as e:
            print(f"❌ Gemini analysis error: {e}")
            return {
                'company_name': None,
                'job_title': None,
                'interview_stage': None,
                'confidence': 0
            }
