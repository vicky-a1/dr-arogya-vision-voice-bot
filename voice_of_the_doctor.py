# if you dont use pipenv uncomment the following:
from dotenv import load_dotenv
load_dotenv()

#Step1a: Setup Text to Speech–TTS–model with gTTS
import os
import logging
from gtts import gTTS
from pydub import AudioSegment

# Helper function to convert MP3 to WAV
def convert_mp3_to_wav(mp3_path, wav_path):
    try:
        # Try using pydub first
        try:
            sound = AudioSegment.from_mp3(mp3_path)
            sound.export(wav_path, format="wav")
            logging.info(f"Converted {mp3_path} to {wav_path} using pydub")
            return wav_path
        except Exception as pydub_error:
            logging.warning(f"Pydub conversion failed: {pydub_error}")

            # Fallback to ffmpeg if available
            try:
                import subprocess
                result = subprocess.run(
                    ["ffmpeg", "-i", mp3_path, wav_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                if result.returncode == 0:
                    logging.info(f"Converted {mp3_path} to {wav_path} using ffmpeg")
                    return wav_path
                else:
                    raise Exception(f"ffmpeg returned non-zero exit code: {result.returncode}")
            except Exception as ffmpeg_error:
                logging.warning(f"ffmpeg conversion failed: {ffmpeg_error}")
                # Just return the MP3 path as a last resort
                logging.info(f"Using original MP3 file: {mp3_path}")
                return mp3_path
    except Exception as e:
        logging.error(f"Error converting MP3 to WAV: {e}")
        return mp3_path  # Return the original MP3 path as a fallback

def text_to_speech_with_gtts_old(input_text, output_filepath):
    language="en"

    audioobj= gTTS(
        text=input_text,
        lang=language,
        slow=False
    )
    audioobj.save(output_filepath)


input_text="Hi this is Ai with Vikas!"
#text_to_speech_with_gtts_old(input_text=input_text, output_filepath="gtts_testing.mp3")

#Step1b: Setup Text to Speech–TTS–model with ElevenLabs
import elevenlabs
from elevenlabs.client import ElevenLabs

ELEVENLABS_API_KEY=os.environ.get("ELEVENLABS_API_KEY")

def text_to_speech_with_elevenlabs_old(input_text, output_filepath):
    client=ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio=client.generate(
        text= input_text,
        voice= "Aria",
        output_format= "mp3_22050_32",
        model= "eleven_turbo_v2"
    )
    elevenlabs.save(audio, output_filepath)

#text_to_speech_with_elevenlabs_old(input_text, output_filepath="elevenlabs_testing.mp3")

#Step2: Use Model for Text output to Voice

import subprocess
import platform

def text_to_speech_with_gtts(input_text, output_filepath):
    import logging
    language="en"

    try:
        # Create MP3 file first
        mp3_filepath = output_filepath
        if not mp3_filepath.endswith('.mp3'):
            mp3_filepath = output_filepath + '.mp3'

        # Generate MP3 with gTTS
        audioobj = gTTS(
            text=input_text,
            lang=language,
            slow=False
        )
        audioobj.save(mp3_filepath)
        logging.info(f"Generated MP3 file with gTTS at: {mp3_filepath}")

        # Convert to WAV for better compatibility
        wav_filepath = output_filepath
        if not wav_filepath.endswith('.wav'):
            wav_filepath = os.path.splitext(output_filepath)[0] + '.wav'

        # Convert MP3 to WAV
        wav_path = convert_mp3_to_wav(mp3_filepath, wav_filepath)
        if not wav_path:
            logging.warning(f"Could not convert to WAV, using MP3: {mp3_filepath}")
            wav_path = mp3_filepath

        # Try to play the audio (commented out for web interface)
        # We don't need to play the audio here as Gradio will handle playback
        # os_name = platform.system()
        # try:
        #     if os_name == "Darwin":  # macOS
        #         subprocess.run(['afplay', wav_path])
        #     elif os_name == "Windows":  # Windows
        #         subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{wav_path}").PlaySync();'])
        #     elif os_name == "Linux":  # Linux
        #         subprocess.run(['aplay', wav_path])  # Alternative: use 'mpg123' or 'ffplay'
        #     else:
        #         raise OSError("Unsupported operating system")
        # except Exception as e:
        #     logging.warning(f"An error occurred while trying to play the audio: {e}")

        return wav_path
    except Exception as e:
        logging.error(f"Error generating audio with gTTS: {e}")
        # Create a simple error message audio file
        try:
            error_message = "Sorry, there was an error generating the audio response."
            audioobj = gTTS(text=error_message, lang=language, slow=False)
            mp3_filepath = output_filepath
            if not mp3_filepath.endswith('.mp3'):
                mp3_filepath = output_filepath + '.mp3'
            audioobj.save(mp3_filepath)

            # Convert to WAV
            wav_filepath = os.path.splitext(output_filepath)[0] + '.wav'
            wav_path = convert_mp3_to_wav(mp3_filepath, wav_filepath)
            if not wav_path:
                return mp3_filepath
            return wav_path
        except Exception as e:
            logging.error(f"Failed to create even error message audio: {e}")
            return None


input_text="Hi this is Ai with Vikas, autoplay testing!"
#text_to_speech_with_gtts(input_text=input_text, output_filepath="gtts_testing_autoplay.mp3")


def text_to_speech_with_elevenlabs(input_text, output_filepath):
    import logging

    if not ELEVENLABS_API_KEY or ELEVENLABS_API_KEY == "your_elevenlabs_api_key_here":
        error_message = "ERROR: ELEVENLABS_API_KEY is not set or is using the default placeholder value."
        logging.error(error_message)
        # Fall back to gTTS if ElevenLabs API key is not available
        logging.warning("Falling back to gTTS for text-to-speech")
        return text_to_speech_with_gtts(input_text + "\n\nNote: Using Google Text-to-Speech because ElevenLabs API key is not set. Please add your actual ElevenLabs API key to the .env file. You can get an API key from https://elevenlabs.io", output_filepath)

    try:
        # Create MP3 file first
        mp3_filepath = output_filepath
        if not mp3_filepath.endswith('.mp3'):
            mp3_filepath = output_filepath + '.mp3'

        # Generate MP3 with ElevenLabs
        client=ElevenLabs(api_key=ELEVENLABS_API_KEY)
        logging.info(f"Sending text-to-speech request to ElevenLabs API with voice: Aria")
        audio=client.generate(
            text= input_text,
            voice= "Aria",
            output_format= "mp3_22050_32",
            model= "eleven_turbo_v2"
        )
        elevenlabs.save(audio, mp3_filepath)
        logging.info(f"Generated MP3 file with ElevenLabs at: {mp3_filepath}")

        # Convert to WAV for better compatibility
        wav_filepath = output_filepath
        if not wav_filepath.endswith('.wav'):
            wav_filepath = os.path.splitext(output_filepath)[0] + '.wav'

        # Convert MP3 to WAV
        wav_path = convert_mp3_to_wav(mp3_filepath, wav_filepath)
        if not wav_path:
            logging.warning(f"Could not convert to WAV, using MP3: {mp3_filepath}")
            wav_path = mp3_filepath

        # Try to play the audio (commented out for web interface)
        # We don't need to play the audio here as Gradio will handle playback
        # os_name = platform.system()
        # try:
        #     if os_name == "Darwin":  # macOS
        #         subprocess.run(['afplay', wav_path])
        #     elif os_name == "Windows":  # Windows
        #         subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{wav_path}").PlaySync();'])
        #     elif os_name == "Linux":  # Linux
        #         subprocess.run(['aplay', wav_path])  # Alternative: use 'mpg123' or 'ffplay'
        #     else:
        #         raise OSError("Unsupported operating system")
        # except Exception as e:
        #     logging.warning(f"An error occurred while trying to play the audio: {e}")

        return wav_path
    except Exception as e:
        error_message = f"Error in text_to_speech_with_elevenlabs: {e}"
        logging.error(error_message)
        logging.warning("Falling back to gTTS due to error")
        # Fall back to gTTS if ElevenLabs fails
        return text_to_speech_with_gtts(input_text + f"\n\nNote: Using Google Text-to-Speech because ElevenLabs API returned an error: {str(e)}", output_filepath)

#text_to_speech_with_elevenlabs(input_text, output_filepath="elevenlabs_testing_autoplay.mp3")  # Using Vikas in input_text