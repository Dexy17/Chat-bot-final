import google.generativeai as genai

class GeminiAPIHandler:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def extract_symptoms(self, user_text):
        # Always translate user input to English for consistent symptom extraction
        # english_text = translator.translate_to_english(user_text)
        english_text = user_text
        prompt = f"""
        Extract medical symptoms from the following patient description:
        
        "{english_text}"
        
        Return ONLY a comma-separated list of the symptoms mentioned. 
        If no symptoms are detected, return "no".
        """
        
        response = self.model.generate_content(prompt)
        symptom_text = response.text.strip()
        
        # Split by commas and clean up whitespace
        symptoms = [s.strip() for s in symptom_text.split(',')]
        return symptoms
        
    def normalize_symptom(self, symptom):
        prompt = f"Normalize the following medical symptom to a standard term: {symptom}"
        response = self.model.generate_content(prompt)
        return response.text.strip()

    def generate_followup_questions(self, symptom):
        prompt = f"Generate follow-up questions for the symptom: {symptom}"
        response = self.model.generate_content(prompt)
        return response.text.split('\n')

    def generate_pdf_report(self, collected_data):
        prompt = f"Generate a detailed medical report in markdown format based on the following data: {collected_data}"
        response = self.model.generate_content(prompt)
        return response.text
     
    def is_exit_command_ga(self, user_text):
        # Translate to English for consistent command detection
        print("The correct gemini is being used!")
        english_text = user_text.lower()
        exit_commands = [
                "done", "exit", "quit", "finish", "end", "complete", 
                "that's all", "no more symptoms", "nothing else", "stop", "thank you thats all!"
            ]
        user_text = user_text.lower()
        if(user_text in exit_commands):
            return True
        try:
            prompt = (
                f"Determine if the following input from a user is meant to end the conversation. "
                f"Answer with 'yes' if it is an exit command or 'no' otherwise.\n\nUser Input: {user_text}"
            )
            response = self.model.generate_content(prompt)
            answer = response.text.strip().lower()
            # For example, if Gemini returns "yes", then we treat it as an exit command.
            return answer == "yes"
        except:
            print("Gemini Failed...")
            return False
    
if __name__ == "__main__":
    genai.configure(api_key = "AIzaSyBkRDmEdtVhVtHHbfvpetHKANTz1EW1qYQ")
    model_list = genai.list_models()
    for model in model_list:    
        print(model.name)