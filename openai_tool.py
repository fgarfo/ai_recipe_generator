from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_KEY"))


def recipe_generator(prompt):
    response = client.chat.completions.create(model="gpt-3.5-turbo",
                                              messages=[{
                                                  "role": "user", "content": "Make a recipe with the following ingredients: " + prompt}],
                                              max_tokens=500)
    return response.choices[0].message.content
