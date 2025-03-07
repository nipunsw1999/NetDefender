import os

from groq import Groq

os.environ['GROQ_API_KEY'] = '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'
        
client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
            )

with open("output.txt", "r", encoding="utf-8") as file:
    text = file.read()
    
    
prompt= f"""Read the text and return the details of the open ports. It should output as JSON. {'ip', 'port','port type'}. Please return only json. Do not return anything else.This is the text: {text}"""

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ],
    model="llama-3.3-70b-versatile",
)

print(chat_completion.choices[0].message.content)

json_output = chat_completion.choices[0].message.content

# Save JSON output to filter.txt
with open("filter.txt", "w", encoding="utf-8") as file:
    file.write(json_output)