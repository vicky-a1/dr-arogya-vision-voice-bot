from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import logging
import base64
from werkzeug.utils import secure_filename
import uuid
import json

# Import our existing modules
from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_gtts

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Check if API keys are available
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_VISION_API_KEY = os.environ.get("GOOGLE_VISION_API_KEY")

# Create Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure allowed extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'wav', 'mp3'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# System prompt for the doctor
system_prompt = """You are Dr. Arogya, a professional dermatologist with expertise in skin conditions and medical diagnosis.
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

@app.route('/')
def index():
    return render_template('index.html')

# API status route removed as requested

@app.route('/api/upload', methods=['POST'])
def upload_file():
    # Check if the post request has the file part
    if 'audio' not in request.files or 'image' not in request.files:
        return jsonify({
            "status": "error",
            "message": "Missing audio or image file"
        }), 400

    audio_file = request.files['audio']
    image_file = request.files['image']

    # If user does not select file, browser also
    # submit an empty part without filename
    if audio_file.filename == '' or image_file.filename == '':
        return jsonify({
            "status": "error",
            "message": "No selected file"
        }), 400

    if audio_file and allowed_file(audio_file.filename) and image_file and allowed_file(image_file.filename):
        # Generate unique filenames
        audio_filename = str(uuid.uuid4()) + '.' + audio_file.filename.rsplit('.', 1)[1].lower()
        image_filename = str(uuid.uuid4()) + '.' + image_file.filename.rsplit('.', 1)[1].lower()

        # Save files
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)

        audio_file.save(audio_path)
        image_file.save(image_path)

        try:
            # Process the files
            logging.info(f"Processing audio file: {audio_path}")
            logging.info(f"Processing image file: {image_path}")

            # Transcribe audio
            speech_to_text_output = transcribe_with_groq(
                GROQ_API_KEY=GROQ_API_KEY,
                audio_filepath=audio_path,
                stt_model="whisper-large-v3"
            )
            logging.info(f"Transcription result: {speech_to_text_output}")

            # Analyze image
            doctor_response = analyze_image_with_query(
                query=system_prompt + speech_to_text_output,
                encoded_image=encode_image(image_path),
                model="meta-llama/llama-4-scout-17b-16e-instruct"
            )
            logging.info(f"Doctor's response: {doctor_response}")

            # Generate audio response
            output_filepath = os.path.join(app.config['UPLOAD_FOLDER'], str(uuid.uuid4()) + ".wav")
            voice_of_doctor = text_to_speech_with_gtts(input_text=doctor_response, output_filepath=output_filepath)
            logging.info(f"Generated voice response at: {voice_of_doctor}")

            # Get relative paths for frontend
            audio_output_path = os.path.relpath(voice_of_doctor, start=os.path.dirname(__file__))

            return jsonify({
                "status": "success",
                "transcription": speech_to_text_output,
                "diagnosis": doctor_response,
                "audio_response": audio_output_path
            })

        except Exception as e:
            logging.error(f"Error in processing: {e}")
            return jsonify({
                "status": "error",
                "message": f"Error processing files: {str(e)}"
            }), 500

    return jsonify({
        "status": "error",
        "message": "Invalid file type"
    }), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, port=7860)
