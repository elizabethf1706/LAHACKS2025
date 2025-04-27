import json
import scipy.io.wavfile as wf
import numpy as np
from groq import Groq
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import base64

load_dotenv()

app = Flask(__name__)

@app.post("/api/audio-response")
def post_audio_response():
    data = request.data.decode()

    base64_data = data
    binary_data = base64.b64decode(base64_data)

    app.logger.info(len(data))

    # idk if i need this, but before, sometimes there'd be an error b/c data wasn't always a multiple of 4
    if len(binary_data) % 4 != 0:
        binary_data = binary_data[:-(len(binary_data) % 4)]

    # app.logger.info(len(data))

    np_data = np.frombuffer(binary_data, dtype='float32')

    try:
        os.remove("test.wav")
    except OSError:
        pass

    wf.write("test.wav", 16000, np_data)

    print("wav file done")

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    with open("test.wav", "rb") as sound_file:
        # Create a transcription of the audio file
        transcription = client.audio.transcriptions.create(
            file=sound_file, # Required audio file
            model="whisper-large-v3-turbo", # Required model to use for transcription
            language="en",
        )
        text = transcription.text

        app.logger.info(text)

        print("transcription done")

        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are given some dialogue from the user and the person they're speaking to; the user messages are *not* talking to you, they're transcripts of the user's conversation with someone else. Reply with information that may help the user in this conversation. If you cannot provide direct help, don't say anything. Be clear and as concise as possible (1 sentence)."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            model="llama-3.3-70b-versatile"
        )

    return jsonify({
        "success": True,
        "response": response.choices[0].message.content
    })

