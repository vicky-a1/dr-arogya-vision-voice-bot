# if you dont use pipenv uncomment the following:
from dotenv import load_dotenv
load_dotenv()

#Step1: Setup GROQ API key
import os

GROQ_API_KEY=os.environ.get("GROQ_API_KEY")

#Step2: Convert image to required format
import base64


#image_path="acne.jpg"

def encode_image(image_path):
    image_file=open(image_path, "rb")
    return base64.b64encode(image_file.read()).decode('utf-8')

#Step3: Setup Multimodal LLM
from groq import Groq

query="Is there something wrong with my face?"
model="meta-llama/llama-4-scout-17b-16e-instruct"  # This is a currently supported vision model

def analyze_image_with_query(query, model, encoded_image):
    import logging

    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        error_message = "ERROR: GROQ_API_KEY is not set or is using the default placeholder value."
        logging.error(error_message)
        return error_message + "\n\nPlease add your actual GROQ API key to the .env file. You can get an API key from https://console.groq.com/"

    try:
        client=Groq(api_key=GROQ_API_KEY)
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": query
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}",
                        },
                    },
                ],
            }]

        logging.info(f"Sending request to GROQ API with model: {model}")
        chat_completion=client.chat.completions.create(
            messages=messages,
            model=model
        )

        response = chat_completion.choices[0].message.content
        logging.info(f"Received response from GROQ API: {response[:100]}...")
        return response
    except Exception as e:
        error_message = f"Error in analyze_image_with_query: {e}"
        logging.error(error_message)
        return f"ERROR: Failed to analyze image with GROQ API. {str(e)}\n\nPlease check your API key and internet connection."