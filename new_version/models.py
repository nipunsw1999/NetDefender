import os
from google import genai
from langchain_groq import ChatGroq
from prompts import *

# Function to call Google Gemini API
# def call_to_llm_v3(prompt):
#     gemini = genai.GenerativeModel("gemini-1.5-flash", api_key=os.getenv('GEMINI_API_KEY'))
#     response = gemini.generate_content(prompt)
#     return response.text

def call_to_llm2(system_prompt,user_message,temperature):
    chat = ChatGroq(temperature=temperature, model_name="llama-3.3-70b-versatile")
    system_message = system_prompt
    user_input = user_message
    formatted_prompt = f"{system_message}\n\nUser: {user_input}\nAssistant:"


    response = chat.invoke(formatted_prompt)
    return response.content if hasattr(response, "content") else response


print(call_to_llm2(system_prompt,user_message,0))


