import google.generativeai as genai
import pyttsx3 as p
import speech_recognition as sr

class VoiceAssistant:
    def __init__(self, api_key):
        # Initialize Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Initialize text-to-speech engine
        self.engine = p.init()
        self.engine.setProperty('rate', 130)
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
    
    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()
    
    def listen(self):
        with sr.Microphone() as source:
            print("Adjusting for ambient noise... Please wait")
            self.recognizer.adjust_for_ambient_noise(source)
            print("Listening...")
            try:
                audio = self.recognizer.listen(source, timeout=10)
                text = self.recognizer.recognize_google(audio)
                print("You said:", text)
                return text
            except sr.UnknownValueError:
                print("Could not understand the audio")
                return None
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                return None
    
    def get_gemini_response(self, prompt):
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error getting response from Gemini: {e}")
            return "I'm sorry, I couldn't get a response at this time."
    
    def run(self):
        self.speak("Hello! I'm your voice assistant. How can I help you?")
        
        while True:
            user_input = self.listen()
            
            if user_input is None:
                self.speak("I didn't catch that. Could you please repeat?")
                continue
                
            if "exit" in user_input.lower() or "bye" in user_input.lower():
                self.speak("Goodbye!")
                break
            
            # Get response from Gemini
            gemini_response = self.get_gemini_response(user_input)
            
            # Speak the response
            self.speak(gemini_response)

def main():
    # Replace with your actual API key
    API_KEY = "AIzaSyD_zEUtIa2ucHwvcTG4hwQxa0bTztzGQks"
    
    assistant = VoiceAssistant(API_KEY)
    assistant.run()

if __name__ == "__main__":
    main()