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
from voice_of_the_doctor import text_to_speech_with_gtts

system_prompt="""You are Dr. Vikas, a professional dermatologist with expertise in skin conditions and medical diagnosis.
            Analyze the uploaded image carefully and provide a detailed medical assessment.
            If you identify any skin condition or medical issue, provide a clear diagnosis and suggest appropriate remedies or treatments.
            Your response should be structured as follows:
            1. Begin with a greeting and acknowledge what you see in the image
            2. Provide your professional assessment of any medical conditions visible
            3. Suggest possible treatments or next steps
            4. End with reassurance and professional closing

            Speak directly to the patient as if in a doctor's office. Be thorough but compassionate.
            Do not use markdown formatting or mention that you are an AI. Respond as a real doctor would.
            If the image is unclear or you cannot make a definitive diagnosis, be honest about limitations and suggest seeking in-person medical advice."""


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
        voice_of_doctor = text_to_speech_with_gtts(input_text=doctor_response, output_filepath=output_filepath)
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

# Check if API key is valid (not just a placeholder)
valid_groq_key = groq_api_key and groq_api_key != "your_groq_api_key_here"

# Create API key status message
api_status = ""
if not valid_groq_key:
    api_status = "⚠️ GROQ API KEY REQUIRED: Please add your GROQ API key to the .env file."
    logging.error("GROQ API key is missing or invalid")
else:
    api_status = "✅ API key detected. Using GROQ API for analysis."
    logging.info("GROQ API key is valid")

# Create a custom theme with Arogya colors
arogya_theme = gr.themes.Soft(
    primary_hue="teal",
    secondary_hue="blue",
    neutral_hue="gray"
).set(
    button_primary_background_fill="#00A3A3",
    button_primary_background_fill_hover="#008080",
    button_primary_text_color="white",
    button_secondary_background_fill="#E0F7FA",
    button_secondary_background_fill_hover="#B2EBF2",
    button_secondary_text_color="#006064",
    background_fill_primary="#F5FFFF",
    block_title_text_color="#006064",
    block_label_text_color="#00796B",
    input_background_fill="#FFFFFF",
    slider_color="#00A3A3",
    slider_color_dark="#008080",
)

# Create the enhanced interface with Arogya color theme
with gr.Blocks(theme=arogya_theme, css=".gradio-container {max-width: 900px; margin: auto}") as iface:

    # Header with title
    with gr.Row():
        gr.Markdown(
            """<h1 style='text-align: center; margin-bottom: 1rem; color: #00796B;'>Arogya Doctor Vision</h1>
            <h3 style='text-align: center; margin-top: 0; color: #00A3A3;'>AI-Powered Medical Diagnosis Assistant</h3>"""
        )

    # Status message
    gr.Markdown(f"<div style='text-align: center; padding: 0.5rem; margin-bottom: 1rem; border-radius: 0.5rem; background-color: {'#E0F7FA' if 'API keys detected' in api_status else '#FFEBEE'}; color: {'#006064' if 'API keys detected' in api_status else '#B71C1C'};'>{api_status}</div>")

    # Instructions
    with gr.Accordion("How to use this application", open=True):
        gr.Markdown(
            """### Follow these simple steps to get a medical diagnosis:
            1. **Record your voice** - Click the microphone button and ask about your medical condition
            2. **Upload an image** - Upload a clear image of the affected area or medical scan
            3. **Get diagnosis** - Click the 'Get Diagnosis' button and wait for Dr. Vikas's analysis
            4. **Review results** - Read the diagnosis and listen to the audio response

            For best results, ensure your image is clear and well-lit, and speak clearly when recording your question."""
        )

    # Main interface with tabs
    with gr.Tabs():
        with gr.TabItem("Diagnosis"):
            with gr.Row():
                # Input section
                with gr.Column():
                    gr.Markdown("### Step 1: Record your question")
                    audio_input = gr.Audio(
                        sources=["microphone"],
                        type="filepath",
                        label="Record Your Voice",
                        elem_id="audio-input"
                    )

                    gr.Markdown("### Step 2: Upload a medical image")
                    image_input = gr.Image(
                        type="filepath",
                        label="Upload Medical Image",
                        elem_id="image-input",
                        height=300
                    )

                    with gr.Row():
                        clear_btn = gr.Button("Clear", variant="secondary")
                        submit_btn = gr.Button("Get Diagnosis", variant="primary", elem_id="submit-btn")

            # Output section
            with gr.Column():
                with gr.Group():
                    gr.Markdown("### Your Transcribed Question")
                    text_output = gr.Textbox(label="", elem_id="text-output")

                with gr.Group():
                    gr.Markdown("### Dr. Arogya's Diagnosis")
                    doctor_output = gr.Textbox(label="", elem_id="doctor-output", lines=10)

                with gr.Group():
                    gr.Markdown("### Audio Response")
                    audio_output = gr.Audio(label="", type="filepath", elem_id="audio-output")

        with gr.TabItem("About"):
            gr.Markdown(
                """## About Arogya Doctor Vision

                Arogya Doctor Vision is an AI-powered medical diagnosis assistant that helps you get preliminary insights about your medical conditions.

                ### Features:
                - **Voice interaction** - Ask questions naturally using your voice
                - **Image analysis** - Upload medical images for AI analysis
                - **Professional diagnosis** - Get detailed medical insights from Dr. Vikas
                - **Audio response** - Listen to the diagnosis in a natural voice

                ### Important Note:
                This application is for informational purposes only and should not replace professional medical advice. Always consult with a healthcare professional for proper diagnosis and treatment.

                ### Technologies Used:
                - GROQ API for speech-to-text and image analysis
                - Google Text-to-Speech for audio responses
                - Google Vision AI as a fallback for image analysis

                ### Contact:
                For support or inquiries, please contact support@arogya.com
                """
            )

    # Set up event handlers
    submit_btn.click(
        fn=process_inputs,
        inputs=[audio_input, image_input],
        outputs=[text_output, doctor_output, audio_output],
        api_name="diagnose"
    )

    # Clear button functionality
    clear_btn.click(
        lambda: [None, None, None, None, None],
        inputs=None,
        outputs=[audio_input, image_input, text_output, doctor_output, audio_output],
        api_name="clear"
    )

iface.launch(debug=True)

#http://127.0.0.1:7860