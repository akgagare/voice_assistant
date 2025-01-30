import google.generativeai as genai

genai.configure(api_key="APi_KEY")
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Give information about MPSC")
print(response.text)