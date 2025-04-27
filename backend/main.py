import json
import scipy.io.wavfile as wf
import numpy as np
from groq import Groq
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import base64
import requests
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)

transcriptions = []
stored_profiles = []

# Set your Groq API key here or use an environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Groq API endpoint for completions
url = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

@app.post("/api/transcribe")
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

    client = Groq(api_key=GROQ_API_KEY)

    with open("test.wav", "rb") as sound_file:
        # Create a transcription of the audio file
        transcription = client.audio.transcriptions.create(
            file=sound_file, # Required audio file
            model="whisper-large-v3-turbo", # Required model to use for transcription
            language="en",
        )
        text = transcription.text

    return jsonify({
        "success": True,
        "transcription": text
    })

DUMMY_RESUME = """
John Doe
Email: johndoe@email.com | Phone: (555) 123-4567

Education:
- B.S. in Computer Science, University of Example, Expected Graduation: 2025
- Relevant Coursework: Data Structures, Algorithms, Web Development, Machine Learning

Experience:
- Software Engineering Intern, TechStart Inc. (Summer 2023)
    - Developed a web application using React and Node.js to streamline internal workflows.
    - Collaborated with a team of 5 interns to deliver project milestones on time.

Projects:
- Personal Portfolio Website: Designed and built a personal website using HTML, CSS, and JavaScript.
- Chatbot for Student Services: Created a chatbot using Python and Flask to answer common student questions.

Skills:
- Programming: Python, Java, JavaScript, C++
- Tools: Git, VS Code, Figma

Activities:
- President, University Coding Club
- Volunteer, Local Food Bank
"""

DUMMY_LINKEDIN = """
Name: Sarah Smith
Title: Technical Recruiter at Innovatech Solutions

Background:
- 7+ years of experience recruiting for software engineering and data science roles.
- Passionate about helping students and recent graduates find their first tech job.
- Frequently posts about resume tips, interview preparation, and career growth in tech.

Interests:
- Mentoring students and early-career professionals.
- Diversity and inclusion in technology.
- Attending university career fairs and hackathons.
"""

# Add a global variable to store conversation history
global_conversation_history = []

def get_speaker_labeling_prompt(conversation_history):
    """
    Returns a prompt for labeling speakers in a conversation history.
    """
    return (
        "You are an expert conversation analyst. "
        "Your job is to label each sentence or phrase in the following conversation history as either 'User:' or 'Recruiter:'.\n"
        "\n"
        "CRITICAL INSTRUCTIONS:\n"
        "- The 'User' is always the person looking for a job or opportunity.\n"
        "- The 'Recruiter' is the person who has the LinkedIn profile provided and may have jobs or opportunities to offer.\n"
        "- Do NOT assume the conversation alternates. One speaker may say several sentences or phrases in a row.\n"
        "- For each sentence or phrase, analyze the context, word choice, tone, and who is being addressed.\n"
        "- If a block of text contains multiple sentences from the same speaker, label each sentence or phrase individually.\n"
        "- Use clues such as:\n"
        "    * Who is asking for information, advice, or opportunities? (Usually the User)\n"
        "    * Who is offering information about jobs, company, or giving advice? (Usually the Recruiter)\n"
        "    * Who is answering questions about their background, skills, or experience? (Usually the User)\n"
        "    * Who is asking about the User's experience, skills, or interests? (Usually the Recruiter)\n"
        "- If unsure, use the context of previous and following lines to make the best decision. Do NOT guess randomly.\n"
        "- Your labeling must be extremely accurate. This is critical.\n"
        "- Label every sentence or phrase clearly as either 'User:' or 'Recruiter:'.\n"
        "\n"
        "Return ONLY the labeled conversation, with each sentence or phrase starting with 'User:' or 'Recruiter:'.\n"
        "\n"
        f"Conversation History:\n{conversation_history}\n"
    )

@app.route('/api/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message", "")
    user_resume = request.json.get("resume", DUMMY_RESUME)
    linkedin_details = request.json.get("linkedin", DUMMY_LINKEDIN)
    conversation_history = request.json.get("history", "")

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    # Step 1: Label speakers in the conversation history (always use the latest user input)
    # Append the new user input to the conversation history if needed
    if conversation_history.strip():
        updated_history = conversation_history.strip() + "\n" + user_input.strip()
    else:
        updated_history = user_input.strip()

    speaker_labeling_prompt = "Label each line as 'User:' or 'Recruiter:'.\n\n" + updated_history
    print("\n--- Speaker Labeling Prompt ---\n", speaker_labeling_prompt)

    speaker_labeling_messages = [
        {"role": "system", "content": speaker_labeling_prompt}
    ]
    speaker_labeling_data = {
        "model": "llama-3.3-70b-versatile",
        "messages": speaker_labeling_messages,
        "max_tokens": 512,
        "temperature": 0.0
    }
    speaker_labeling_response = requests.post(url, headers=headers, json=speaker_labeling_data)
    try:
        speaker_labeling_response.raise_for_status()
        labeled_transcript = speaker_labeling_response.json()["choices"][0]["message"]["content"]
        print("\n--- Labeled Transcript Output ---\n", labeled_transcript)
    except requests.exceptions.HTTPError as e:
        return jsonify({
            "error": "Speaker labeling HTTP error",
            "details": str(e),
            "response_content": speaker_labeling_response.text
        }), 500

    # Step 2: Use labeled transcript in the main system prompt
    system_prompt = (
        "You are an interview coach. "
        "Given the user's resume, recruiter's LinkedIn, and labeled chat, "
        "give concise, actionable tips (max 5 words each) for the user to say next. "
        "Focus on connection, relevance, and standing out. "
        "Each tip: ≤5 words. "
        "Respond ONLY with a JSON array of 3 strings, e.g.: [\"Ask about company culture\", \"Highlight leadership experience\"]"
        "\n\n"
        f"User Resume:\n{user_resume}\n\n"
        f"Recruiter's LinkedIn:\n{linkedin_details}\n\n"
        f"Labeled Chat:\n{labeled_transcript}\n"
    )
    print("\n--- Main System Prompt ---\n", system_prompt)

    messages = [
        {"role": "system", "content": system_prompt}
    ]

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "max_tokens": 256,
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)
    try:
        response.raise_for_status()
        result = response.json()
        assistant_message = result["choices"][0]["message"]["content"]
        print("\n--- Assistant Message Output ---\n", assistant_message)

        # Update the global conversation history
        global global_conversation_history
        global_conversation_history.append(f"User: {user_input}")
        global_conversation_history.append(f"Assistant: {assistant_message}")

        return jsonify({"assistant": assistant_message})
    except requests.exceptions.HTTPError as e:
        return jsonify({
            "error": "HTTP error",
            "details": str(e),
            "response_content": response.text
        }), 500

@app.route('/api/gemini_chat', methods=['POST'])
def stop_stream():
    # Summarize the global conversation history using Gemini
    genai.configure(api_key=os.getenv("GENAI_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")

    # Prepare the summary prompt
    summary_prompt = (
    "You are an expert career coach. "
    "Analyze the following conversation between you (the User) and a recruiter (the Assistant). "
    "Give direct, constructive feedback to the User about their engagement with the recruiter. "
    "Your feedback should include:\n"
    "- What you did well in the conversation\n"
    "- Areas where you could improve\n"
    "- 2-3 actionable tips for your next recruiter conversation\n"
    "Address the User as 'you'. Be specific and concise. Use bullet points for clarity.\n\n"
    "Conversation:\n"
    + "\n".join(global_conversation_history)
    )
    summary_response = model.generate_content(summary_prompt)
    summary_text = summary_response.text

    return jsonify({"summary": summary_text})

@app.post("/api/save-conversation")
def save_conversation():
    transcription = request.json["transcription"]

    transcriptions.append(transcription)

    return jsonify({
        "success": True
    })

@app.get("/api/get-conversations")
def get_conversations():
    return jsonify({
        "success": True,
        "transcriptions": transcriptions
    })

@app.post("/api/upload-profiles")
def upload_profiles():
    global stored_profiles
    profiles = request.json["profiles"]

    stored_profiles = profiles

    return jsonify({
        "success": True
    })

@app.post("/api/get-profiles")
def get_profiles():
    return jsonify({
        "success": True,
        "profiles": stored_profiles
    })
