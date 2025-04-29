import os
from langchain_groq import ChatGroq
from prompts import *
from langchain_google_genai import ChatGoogleGenerativeAI
from h2ogpte import H2OGPTE

h2ogpte_api_token = os.getenv('H2OGPTE_API_TOKEN')

# Function to call Google Gemini API
# def call_to_llm_v3(prompt):
#     gemini = genai.GenerativeModel("gemini-1.5-flash", api_key=os.getenv('GEMINI_API_KEY'))
#     response = gemini.generate_content(prompt)
#     return response.text


def h2ogpteCall(SystemPrompt,user):
    client = H2OGPTE(
    address='https://h2ogpte.genai.h2o.ai',
    api_key=h2ogpte_api_token,
    )

    chat_session_id = client.create_chat_session()

    answer = "answer"
    
    with client.connect(chat_session_id) as session:
        reply = session.query(SystemPrompt+ f"{user}")
        answer = reply.content
    return answer



def call_to_llm2(system_prompt,user_message,temperature):
    chat = ChatGroq(temperature=temperature, model_name="llama-3.3-70b-versatile")
    system_message = system_prompt
    user_input = user_message
    formatted_prompt = f"{system_message}\n\nUser: {user_input}\nAssistant:"


    response = chat.invoke(formatted_prompt)
    return response.content if hasattr(response, "content") else response


# def call_to_gemini(system_prompt,user_message,temperature):
#     llm = ChatGoogleGenerativeAI(
#         model="gemini-1.5-pro",
#         temperature=temperature,
#         google_api_key=os.getenv("GEMINI_API_KEY"),
#         # other params...
#     )
    
#     messages = [("system",system_prompt,),("human", user_message),]
#     ai_msg = llm.invoke(messages)
#     return ai_msg.content
        
