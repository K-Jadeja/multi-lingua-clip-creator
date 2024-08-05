import subprocess
from os.path import splitext
import whisper
import re

def convert_webm_to_wav(input_file):
    """
    Converts a WebM file to WAV format using ffmpeg.

    Args:
        input_file (str): Path to the input WebM file.

    Returns:
        str: Path to the output WAV file.
    """
    try:
        output_file = splitext(input_file)[0] + '.wav'

        # Command for ffmpeg conversion
        command = [
            'ffmpeg',
            '-i', input_file,  # Input WebM file
            '-y',  # Overwrite output file if exists
            '-vn',  # Disable video stream
            '-acodec', 'pcm_s16le',  # Use PCM (WAV) codec without loss
            output_file  # Output WAV file
        ]

        # Execute ffmpeg command
        subprocess.run(command, check=True)
        return output_file

    except subprocess.CalledProcessError as e:
        print(f"Error executing ffmpeg command: {e}")


def split_into_phrases(text, max_words=3):
    words = text.split()
    phrases = [' '.join(words[i:i+max_words]) for i in range(0, len(words), max_words)]
    return phrases

def transcribe(file_path):
    """
    Transcribes audio from a WAV file using the Whisper model.

    Args:
        file_path (str): Path to the input WAV file.

    Returns:
        tuple: A tuple containing the detected language (str) and a list of transcribed segments.
    """
    try:
        # Load the Whisper model
        model = whisper.load_model("base")

        # Transcribe the audio file
        print(f"Transcribing {file_path}...")
        result = model.transcribe(file_path)

        # Extract language
        print(f"Detected language: {result['language']}")
        language = result['language']

        # Extract and split segments
        print("Transcribed segments:")
        segments = []
        for segment in result['segments']:
            print("=======================================")
            print(segment)
            phrases = split_into_phrases(segment['text'])
            start = segment['start']
            duration = (segment['end'] - segment['start']) / len(phrases)
            for i, phrase in enumerate(phrases):
                segments.append({
                    'start': start + i * duration,
                    'end': start + (i + 1) * duration,
                    'text': phrase
                })

        return language, segments

    except Exception as e:
        print(f"Error during transcription: {e}")
        return None, []


# Example usage
if __name__ == "__main__":
    input_file = "path/to/your/input.webm"
    wav_file = convert_webm_to_wav(input_file)
    if wav_file:
        language, segments = transcribe(wav_file)
        print(f"Detected language: {language}")
        print("Transcribed segments:")
        for segment in segments:
            print(segment)
