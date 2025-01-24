from flask import Flask, request, jsonify
import os
import tempfile
import yt_dlp
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configure Google Generative AI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

@app.route('/download_youtube_audio', methods=['POST'])
def download_youtube_audio():
    """Download audio from a YouTube URL."""
    data = request.json
    youtube_url = data.get('url')
    if not youtube_url:
        return jsonify({"error": "YouTube URL is required"}), 400

    try:
        # Download audio using yt-dlp
        temp_dir = tempfile.mkdtemp()
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(temp_dir, 'audio.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        # Return the path to the downloaded audio file
        audio_file = os.path.join(temp_dir, 'audio.mp3')
        if os.path.exists(audio_file):
            return jsonify({"audio_url": audio_file}), 200
        else:
            return jsonify({"error": "Failed to download audio"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/summarize_audio', methods=['POST'])
def summarize_audio():
    """Summarize audio using Google's Generative AI."""
    data = request.json
    audio_url = data.get('audio_url')
    if not audio_url:
        return jsonify({"error": "Audio URL is required"}), 400

    try:
        # Call Google's Generative AI API
        model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
        response = model.generate_content(
            [
                "Please summarize the following audio.",
                audio_url
            ]
        )
        return jsonify({"summary": response.text}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)