# if you dont use pipenv uncomment the following:
from dotenv import load_dotenv
load_dotenv()

#Step1: Setup API keys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

GROQ_API_KEY=os.environ.get("GROQ_API_KEY")
GOOGLE_VISION_API_KEY=os.environ.get("GOOGLE_VISION_API_KEY")

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
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        error_message = "ERROR: GROQ_API_KEY is not set or is using the default placeholder value."
        logging.error(error_message)
        return error_message + "\n\nPlease add your actual GROQ API key to the .env file. You can get an API key from https://console.groq.com/"

    # List of models to try in order of preference
    models_to_try = [
        model,  # Try the requested model first
        "meta-llama/llama-4-scout-17b-16e-instruct",  # Then try Llama 4 Scout
        "llama-3.2-90b-vision-preview",  # Then try Llama 3.2 90B
        "claude-3-5-sonnet-20240620",  # Try Claude 3.5 Sonnet
        "gemini-1.5-pro-latest",  # Try Gemini 1.5 Pro
        "llama-3.1-8b-instant"  # Fallback to a non-vision model if needed
    ]

    last_error = None

    # Try each model in sequence until one works
    for current_model in models_to_try:
        try:
            client = Groq(api_key=GROQ_API_KEY)

            # Prepare the message content based on whether the model supports vision
            if "vision" in current_model or "scout" in current_model or "claude" in current_model or "gemini" in current_model:
                # Vision-capable model
                messages = [
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
                    }
                ]
            else:
                # Non-vision model (fallback)
                messages = [
                    {
                        "role": "user",
                        "content": f"{query}\n\nNote: I would analyze your image, but I'm currently using a non-vision model as a fallback. Please try again later when vision models are available."
                    }
                ]

            logging.info(f"Attempting to use model: {current_model}")
            chat_completion = client.chat.completions.create(
                messages=messages,
                model=current_model,
                temperature=0.7,  # Add some creativity
                max_tokens=800    # Ensure we get a detailed response
            )

            response = chat_completion.choices[0].message.content
            logging.info(f"Successfully used model {current_model}")
            logging.info(f"Received response from GROQ API: {response[:100]}...")
            return response

        except Exception as e:
            last_error = e
            error_message = f"Error with model {current_model}: {e}"
            logging.warning(error_message)
            # Continue to the next model

    # If we get here, all models failed
    error_message = f"All models failed. Last error: {last_error}"
    logging.error(error_message)
    return f"I apologize, but I'm currently unable to analyze your image. Our vision analysis service is temporarily unavailable. Please try again later or consult with a healthcare professional directly.\n\nTechnical details: {str(last_error)}"