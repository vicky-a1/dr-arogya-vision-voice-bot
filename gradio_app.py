# if you dont use pipenv uncomment the following:
from dotenv import load_dotenv
load_dotenv()

#VoiceBot UI with Gradio
import os
import gradio as gr
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import record_audio, transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_gtts, text_to_speech_with_elevenlabs

system_prompt="""You have to act as a professional doctor, i know you are not but this is for learning purpose.
            What's in this image?. Do you find anything wrong with it medically?
            If you make a differential, suggest some remedies for them. Donot add any numbers or special characters in
            your response. Your response should be in one long paragraph. Also always answer as if you are answering to a real person.
            Donot say 'In the image I see' but say 'With what I see, I think you have ....'
            Dont respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot,
            Keep your answer concise (max 2 sentences). No preamble, start your answer right away please"""


def process_inputs(audio_filepath, image_filepath):
    try:
        logging.info(f"Processing audio file: {audio_filepath}")
        logging.info(f"Processing image file: {image_filepath}")

        # Check if audio file exists
        if not audio_filepath:
            logging.error("No audio file provided")
            return "No audio recorded", "Please record audio first", None

        # Transcribe audio
        speech_to_text_output = transcribe_with_groq(
            GROQ_API_KEY=os.environ.get("GROQ_API_KEY"),
            audio_filepath=audio_filepath,
            stt_model="whisper-large-v3"
        )
        logging.info(f"Transcription result: {speech_to_text_output}")

        # Handle the image input
        if image_filepath:
            logging.info("Analyzing image with query")
            doctor_response = analyze_image_with_query(
                query=system_prompt+speech_to_text_output,
                encoded_image=encode_image(image_filepath),
                model="meta-llama/llama-4-scout-17b-16e-instruct"
            )
        else:
            logging.warning("No image provided for analysis")
            doctor_response = "No image provided for me to analyze"

        logging.info(f"Doctor's response: {doctor_response}")

        # Generate audio response
        output_filepath = "final.wav"
        voice_of_doctor = text_to_speech_with_elevenlabs(input_text=doctor_response, output_filepath=output_filepath)
        logging.info(f"Generated voice response at: {voice_of_doctor}")

        if voice_of_doctor is None:
            logging.error("Failed to generate audio response")
            return speech_to_text_output, doctor_response, None

        # Make sure the file exists
        if not os.path.exists(voice_of_doctor):
            logging.error(f"Audio file does not exist at path: {voice_of_doctor}")
            return speech_to_text_output, doctor_response, None

        logging.info(f"Returning audio file: {voice_of_doctor}")
        return speech_to_text_output, doctor_response, voice_of_doctor

    except Exception as e:
        logging.error(f"Error in process_inputs: {e}")
        return f"Error: {str(e)}", f"An error occurred: {str(e)}", None


# Check if API keys are available
groq_api_key = os.environ.get("GROQ_API_KEY")
elevenlabs_api_key = os.environ.get("ELEVENLABS_API_KEY")

# Check if API keys are valid (not just placeholders)
valid_groq_key = groq_api_key and groq_api_key != "your_groq_api_key_here"
valid_elevenlabs_key = elevenlabs_api_key and elevenlabs_api_key != "your_elevenlabs_api_key_here"

# Create API key status message
api_status = ""
if not valid_groq_key and not valid_elevenlabs_key:
    api_status = "⚠️ API KEYS REQUIRED: Please add your GROQ and ElevenLabs API keys to the .env file."
    logging.error("Both GROQ and ElevenLabs API keys are missing or invalid")
elif not valid_groq_key:
    api_status = "⚠️ GROQ API KEY REQUIRED: Please add your GROQ API key to the .env file."
    logging.error("GROQ API key is missing or invalid")
elif not valid_elevenlabs_key:
    api_status = "⚠️ ELEVENLABS API KEY REQUIRED: Please add your ElevenLabs API key to the .env file."
    logging.error("ElevenLabs API key is missing or invalid")
else:
    api_status = "✅ API keys detected. Using GROQ and ElevenLabs APIs."
    logging.info("Both API keys are valid")

# Create the interface
iface = gr.Interface(
    fn=process_inputs,
    inputs=[
        gr.Audio(sources=["microphone"], type="filepath"),
        gr.Image(type="filepath")
    ],
    outputs=[
        gr.Textbox(label="Speech to Text"),
        gr.Textbox(label="Doctor's Response"),
        gr.Audio(label="Doctor's Voice Response", type="filepath")
    ],
    title="AI Doctor with Vision and Voice",
    description="Upload an image and record your voice to get a medical analysis.\n" + api_status + "\n\nGet API keys at: https://console.groq.com/ and https://elevenlabs.io"
)

iface.launch(debug=True)

#http://127.0.0.1:7860