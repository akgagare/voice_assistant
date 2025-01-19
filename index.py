import pyttsx3 as p
import speech_recognition as sr # speech to text
from selenium_web import infow
engine = p.init()
rate = engine.getProperty("rate")
engine.setProperty('rate',130)
voices = engine.getProperty('voices')
engine.setProperty('voice',voices[0].id) #voices[0].id -> male voice and voices[1].id -> female voice
print(voices)

def speak(text):
    engine.say(text)
    engine.runAndWait()




r = sr.Recognizer() # helps to retrive audio from microphone
speak("hello sir, I'm your voice assistant how are you")

# Capture audio from microphone
with sr.Microphone() as source:
    print("Adjusting for ambient noise... Please wait")
    r.adjust_for_ambient_noise(source)  # Helps in noisy environments
    print("Say something...")
    audio = r.listen(source, timeout=10)

# Try recognizing the speech
try:
    text = r.recognize_google(audio)
    print("You said:", text)

except sr.UnknownValueError:
    print("Google Speech Recognition could not understand the audio")

except sr.RequestError as e:
    print(f"Could not request results from Google Speech Recognition; {e}")

# Save audio for debugging
with open("test_audio.wav", "wb") as f:
    f.write(audio.get_wav_data())
    print("Saved test audio as 'test_audio.wav' for debugging.")

if "what" or "about" or "you" in text:
    speak("I'm having a good day")
speak("how can I help you")

with sr.Microphone() as source:
    print("Adjusting for ambient noise... Please wait")
    r.adjust_for_ambient_noise(source)  # Helps in noisy environments
    print("Say something...")
    audio = r.listen(source, timeout=10)

# Try recognizing the speech
try:
    text2 = r.recognize_google(audio)
    print("You said:", text2)

except sr.UnknownValueError:
    print("Google Speech Recognition could not understand the audio")

except sr.RequestError as e:
    print(f"Could not request results from Google Speech Recognition; {e}")

if "information" in text2:
    speak("You want information related to which topic:")
    with sr.Microphone() as source:
        print("Adjusting for ambient noise... Please wait")
        r.adjust_for_ambient_noise(source)  # Helps in noisy environments
        print("Say something...")
        audio = r.listen(source, timeout=10)

    try:
        infor_query = r.recognize_google(audio)
        print("You said:", infor_query)

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio.")
        infor_query = ""  # Set to empty string so program doesn't crash

    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition; {e}")
        infor_query = ""


    # # Run the script
    # assist = infow()
    # assist.getinfo(infor_query)

