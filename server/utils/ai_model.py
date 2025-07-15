from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib
import os

class AIModel:
    """
    This class provides a basic AI model to predict the status of job application emails.
    It uses TF-IDF for text analysis and Logistic Regression for classification.
    """
  
    def __init__(self, model_path='ai_model.joblib'):
        self.model_path = model_path
        self.pipeline = None
        self._load_or_train_model()

    def _load_or_train_model(self):
        """
        Checks if a trained AI model already exists. If yes, it loads it.
        If not, it trains a basic model and saves it for later use.
        """
        if os.path.exists(self.model_path):
            print(f"Loading AI model from {self.model_path}")
            self.pipeline = joblib.load(self.model_path)
        else:
            print("AI model not found. Training a dummy model...")
            self._train_dummy_model()
            self.save_model()

    def _train_dummy_model(self):
        """
        Trains a very simple model just for demonstration.
        In a real project, you would use a large, real dataset for training.
        """
        # Example data for training the model
        texts = [
            "Thank you for your application to the Software Engineer position.", # Applied
            "We have received your application for the Data Scientist role.", # Applied
            "We would like to invite you for an interview for the Marketing Manager position.", # Interview
            "Please schedule your phone screen for the Product Designer role.", # Interview
            "We regret to inform you that your application was unsuccessful.", # Rejected
            "The position has been filled, thank you for your interest.", # Rejected
            "We are pleased to offer you the position of Project Coordinator.", # Offer
            "Your offer letter for the Analyst role is attached." # Offer
        ]
        labels = [
            "Applied", "Applied", "Interview", "Interview",
            "Rejected", "Rejected", "Offer", "Offer"
        ]

        # Set up a simple process: first, convert text to numbers (TF-IDF), then classify
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(stop_words='english', max_features=1000)),
            ('classifier', LogisticRegression(max_iter=1000))
        ])

        self.pipeline.fit(texts, labels)
        print("Dummy AI model trained.")

    def save_model(self):
        """Saves the trained AI model to a file so it can be loaded later."""
        if self.pipeline:
            joblib.dump(self.pipeline, self.model_path)
            print(f"AI model saved to {self.model_path}")

    def predict_status(self, email_content):
        """
        Guesses the status of a job application based on the email's text.

        Args:
            email_content (str): The subject and body of the email combined.

        Returns:
            str: The predicted status (e.g., 'Applied', 'Interview', 'Rejected', 'Offer').
                 Returns 'Unknown' if the model isn't ready.
        """
        if not self.pipeline:
            print("Model not loaded or trained. Cannot predict.")
            return "Unknown"

        # Prepare the email text (make it lowercase for consistency)
        processed_content = email_content.lower()

        # Use the trained model to guess the status
        predicted_status = self.pipeline.predict([processed_content])[0]
        return predicted_status

# Example Usage (how to use and test this AI model)
if __name__ == '__main__':
    # Remove any old model file to ensure we train a fresh one for this demo
    if os.path.exists('ai_model.joblib'):
        os.remove('ai_model.joblib')
        print("Removed existing model for fresh training demo.")

    ai_model = AIModel()

    print("\n--- Testing Predictions ---")
    print(f"Email: 'Your application has been received.' -> Status: {ai_model.predict_status('Your application has been received.')}")
    print(f"Email: 'We'd like to invite you for an interview.' -> Status: {ai_model.predict_status('We\'d like to invite you for an interview.')}")
    print(f"Email: 'Unfortunately, we are not moving forward with your application.' -> Status: {ai_model.predict_status('Unfortunately, we are not moving forward with your application.')}")
    print(f"Email: 'Congratulations! We are pleased to offer you the position.' -> Status: {ai_model.predict_status('Congratulations! We are pleased to offer you the position.')}")
    print(f"Email: 'Just checking in on the weather.' -> Status: {ai_model
