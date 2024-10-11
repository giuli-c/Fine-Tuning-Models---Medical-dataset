import openai
from openai import OpenAI

# Imposta la tua chiave API
client = OpenAI(
    api_key = "sk-proj-gZeHdn3l7z4EGkKxu1j3T3BlbkFJ5KqLyEZRhmjPv4AdO9S2"
)

# Prova a fare una richiesta all'API di GPT-4
try:
    response = client.chat.completions.create(
        model="gpt-4o",  
        messages=[{'role': 'user', 'content': 'Test di accesso all''API di GPT-4.'}],
        max_tokens=50
    )
    print("Accesso confermato. Risposta API:")
    print(response.choices[0].message.content)
except openai.error.OpenAIError as e:
    print(f"Errore: {e}")
