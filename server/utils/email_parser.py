import re
from bs4 import BeautifulSoup

class EmailParser:
    """
    A utility class designed to extract key information and infer the status
    of job applications from email content. This implementation is simplified;
    a production-grade solution would likely incorporate more advanced Natural Language Processing (NLP) techniques.
    """

    def __init__(self):
        # Define keywords and patterns to identify different application statuses
        self.application_keywords = [
            "application received", "thank you for your application",
            "we have received your application", "your application for the position of",
            "confirmation of your application"
        ]
        self.interview_keywords = [
            "interview invitation", "schedule an interview", "we would like to invite you for an interview",
            "next steps", "phone screen", "technical interview", "virtual interview"
        ]
        self.rejection_keywords = [
            "application update", "not moving forward", "unsuccessful", "regret to inform you",
            "position has been filled", "we have decided to pursue other candidates"
        ]
        self.offer_keywords = [
            "job offer", "offer of employment", "we are pleased to offer you", "employment agreement"
        ]

    def _clean_text(self, text):
        """
        Preprocesses text by removing excessive whitespace and converting it to lowercase.
        This helps standardize the input for keyword matching.
        """
        return re.sub(r'\s+', ' ', text).strip().lower()

    def parse_email(self, email_subject, email_body):
        """
        Analyzes the subject and body of an email to extract relevant job application details
        and determine a likely status.

        Args:
            email_subject (str): The subject line of the email.
            email_body (str): The HTML or plain text body of the email.

        Returns:
            dict: A dictionary containing extracted information such as company name, job title,
                  and a suggested application status. Returns None if no relevant job application
                  information is detected.
        """
        # Convert HTML to plain text if necessary using BeautifulSoup
        soup = BeautifulSoup(email_body, 'html.parser')
        plain_text_body = soup.get_text(separator=' ', strip=True)

        cleaned_subject = self._clean_text(email_subject)
        cleaned_body = self._clean_text(plain_text_body)

        extracted_info = {
            'company_name': None,
            'job_title': None,
            'suggested_status': 'Unknown',
            'email_snippet': plain_text_body[:200] # Store a brief snippet of the email body for context
        }

        # 1. Infer Status based on predefined keywords in subject or body
        if any(keyword in cleaned_subject or keyword in cleaned_body for keyword in self.offer_keywords):
            extracted_info['suggested_status'] = 'Offer'
        elif any(keyword in cleaned_subject or keyword in cleaned_body for keyword in self.interview_keywords):
            extracted_info['suggested_status'] = 'Interview'
        elif any(keyword in cleaned_subject or keyword in cleaned_body for keyword in self.rejection_keywords):
            extracted_info['suggested_status'] = 'Rejected'
        elif any(keyword in cleaned_subject or keyword in cleaned_body for keyword in self.application_keywords):
            extracted_info['suggested_status'] = 'Applied' # Corrected to Applied for application keywords

        # 2. Attempt to Extract Company Name (this is a highly heuristic approach and would benefit from NLP/ML)
        # A more robust solution would typically involve Named Entity Recognition (NER).
        company_patterns = [
            r"from\s+([a-z0-9\s.&'-]+)\s+regarding",
            r"at\s+([a-z0-9\s.&'-]+)\s+for the position",
            r"your application to\s+([a-z0-9\s.&'-]+)",
            r"from\s+([a-z0-9\s.&'-]+)\s+team"
        ]
        for pattern in company_patterns:
            match = re.search(pattern, cleaned_body)
            if match:
                extracted_info['company_name'] = match.group(1).title() # Capitalize first letter of each word for consistency
                break
        
        # Fallback: In a more advanced implementation, one might try to deduce the company
        # from the email sender's domain (e.g., info@google.com -> Google), which requires
        # access to email headers not directly handled by this parser's current scope.

        # 3. Attempt to Extract Job Title (also a highly heuristic method)
        job_title_patterns = [
            r"for the position of\s+([a-z0-9\s.&'-]+)",
            r"your application for\s+([a-z0-9\s.&'-]+)",
            r"regarding your application for the\s+([a-z0-9\s.&'-]+)\s+role"
        ]
        for pattern in job_title_patterns:
            match = re.search(pattern, cleaned_body)
            if match:
                extracted_info['job_title'] = match.group(1).title()
                break
        
        # Try to extract from subject if not found in body
        if not extracted_info['job_title']:
            subject_job_title_patterns = [
                r"application for\s+([a-z0-9\s.&'-]+)",
                r"interview for\s+([a-z0-9\s.&'-]+)"
            ]
            for pattern in subject_job_title_patterns:
                match = re.search(pattern, cleaned_subject)
                if match:
                    extracted_info['job_title'] = match.group(1).title()
                    break

        # If no specific status or key details (company/job title) are found, the email might not be relevant
        if extracted_info['suggested_status'] == 'Unknown' and not extracted_info['company_name'] and not extracted_info['job_title']:
            return None # Indicate that this is likely not a job application-related email

        return extracted_info

# Example Usage (for testing the parser's functionality)
if __name__ == '__main__':
    parser = EmailParser()

    # Test Case 1: Application Confirmation Email
    subject1 = "Your Application to Acme Corp - Software Engineer"
    body1 = "Dear John, Thank you for your application to the Software Engineer position at Acme Corp. We have received your application and will review it shortly."
    print("--- Processing Email 1: Application Confirmation ---")
    print(parser.parse_email(subject1, body1))

    # Test Case 2: Interview Invitation Email
    subject2 = "Interview Invitation - Senior Data Scientist at Globex Inc."
    body2 = "Hi Jane, We would like to invite you for an interview for the Senior Data Scientist position at Globex Inc. Please click here to schedule a time."
    print("\n--- Processing Email 2: Interview Invitation ---")
    print(parser.parse_email(subject2, body2))

    # Test Case 3: Rejection Email
    subject3 = "Update on your application to Initech"
    body3 = "Dear Applicant, Thank you for your interest in the position at Initech. We regret to inform you that we have decided to pursue other candidates at this time."
    print("\n--- Processing Email 3: Application Rejection ---")
    print(parser.parse_email(subject3, body3))

    # Test Case 4: Job Offer Email
    subject4 = "Job Offer from Cyberdyne Systems - AI Researcher"
    body4 = "Dear Alex, We are pleased to offer you the position of AI Researcher at Cyberdyne Systems. Please review the attached offer letter."
    print("\n--- Processing Email 4: Job Offer ---")
    print(parser.parse_email(subject4, body4))

    # Test Case 5: Irrelevant Email (should return None)
    subject5 = "Your order confirmation"
    body5 = "Thank you for your recent purchase. Your order #12345 has been confirmed."
    print("\n--- Processing Email 5: Irrelevant Content ---")
    print(parser.parse_email(subject5, body5))
