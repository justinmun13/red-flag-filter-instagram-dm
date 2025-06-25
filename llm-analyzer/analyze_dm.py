import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_dm(dm, mode="best friend"):
    prompt = f'Read this DM like your {mode}. Highlight red flags and give playful probabilities for each possible interpretation. Output in a screenshot-friendly format.\nDM: "{dm}"'
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    dm = input("Paste DM: ")
    print(analyze_dm(dm))