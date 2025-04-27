import os
import streamlit as st
import requests
import fitz  # PyMuPDF
import mammoth  # For DOCX reading
import google.generativeai as genai  # Gemini API
from io import BytesIO

# --- Streamlit Page Config ---
st.set_page_config(page_title="Business Networking Follow-Up Generator", page_icon="📄", layout="centered", initial_sidebar_state="expanded")
st.title("Business Networking Follow-Up Generator")

# --- Global conversation history (for demo, you can populate dynamically later) ---
global_conversation_history = []

# --- Extract Text Functions ---
def extract_text_from_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()

def extract_text_from_docx(file):
    result = mammoth.extract_raw_text(file)
    return result.value.strip()

# --- Send Resume to Backend ---
def send_resume_to_backend(resume_text):
    try:
        response = requests.post(
            "https://la-hacks-2025-backend.onrender.com/api/set_resume",
            json={"resume": resume_text}
        )
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Failed to send resume: {e}")
        return False

# --- Summarize Conversation using Gemini ---
def summarize_conversation(conversation_history):
    try:
        genai.configure(api_key="AIzaSyDq7mmeFIw8QJbgvunDLCL_x2U6E_kDGlM")
        model = genai.GenerativeModel("gemini-2.0-flash")

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
            + "\n".join(conversation_history)
        )

        summary_response = model.generate_content(summary_prompt)
        summary_text = summary_response.text
        return summary_text
    except Exception as e:
        st.error(f"Failed to generate summary: {e}")
        return None

# --- Upload Section ---
uploaded_file = st.file_uploader("Upload your file", type=["pdf", "docx"])

if uploaded_file:
    file_type = uploaded_file.type

    with st.spinner('Processing file...'):
        if file_type == "application/pdf" or uploaded_file.name.endswith(".pdf"):
            extracted_text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.name.endswith(".docx"):
            extracted_text = extract_text_from_docx(uploaded_file)
        else:
            extracted_text = None

    if extracted_text:
        st.success("✅ Text extracted successfully!")
        st.text_area("Extracted Text:", extracted_text, height=300)

        # Automatically send to backend
        with st.spinner('Sending resume to backend...'):
            success = send_resume_to_backend(extracted_text)
            if success:
                st.success("✅ Resume sent to backend successfully!")
            else:
                st.error("⚠️ Failed to send resume to backend.")

        # Example: Add extracted text as a 'message' to conversation history
        global_conversation_history.append(f"User: {extracted_text}")

        # --- After upload, generate Gemini feedback ---
        with st.spinner('Generating career coaching feedback...'):
            summary = summarize_conversation(global_conversation_history)

        if summary:
            st.subheader("Career Coaching Feedback ✨")
            st.markdown(summary)
    else:
        st.error("⚠️ Unsupported file type or failed to extract text.")
