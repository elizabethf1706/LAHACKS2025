import streamlit as st
import groq
import re
import requests  # <--- import requests

# Set the title
st.title("Business Networking Follow-Up Generator")

# Your Groq API Key
GROQ_API_KEY = "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"

# Fetch conversation from your backend
def fetch_conversation():
    try:
        response = requests.get("https://la-hacks-2025-backend.onrender.com/api/get-conversations")
        response.raise_for_status()  # Raises error for bad responses
        data = response.json()
        # Assume the conversation text is stored under a key like "conversation" — adjust if necessary
        return data.get("transcriptions", "No conversation found.")
    except Exception as e:
        st.error(f"Failed to fetch conversation: {e}")
        return "Error fetching conversation."

# Function to make LinkedIn links clickable (if there are any)
def make_links_clickable(text):
    pattern = r"(https?://www\.linkedin\.com/[^\s]+)"
    return re.sub(pattern, r'[\g<0>](\g<0>)', text)

# Function to analyze conversation and generate follow-up
def analyze_summary(conversation_text):
    client = groq.Groq(api_key=GROQ_API_KEY)

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": (
                "You are an expert networking assistant. "
                "Given a conversation between two people who are networking professionally, "
                "suggest specific friendly business follow-ups they could send. "
                "Be casual but professional — suggest things like scheduling a coffee chat, "
                "continuing a topic they discussed, offering to help, or connecting on LinkedIn. "
                "Mention the context of when and how they met if possible."
            )},
            {"role": "user", "content": f"Here is the conversation:\n\n{conversation_text}"}
        ]
    )
    return response.choices[0].message.content

# --- Now run everything automatically ---

# Get the conversation
conversation_text = fetch_conversation()

if isinstance(conversation_text, list):
    conversation_text = "\n".join(conversation_text)
# Make LinkedIn links clickable
clickable_conversation = make_links_clickable(conversation_text)

# Show the conversation
st.subheader("Conversation:")
st.markdown(clickable_conversation, unsafe_allow_html=True)

# Automatically generate follow-up
with st.spinner("Generating a follow-up suggestion..."):
    follow_up = analyze_summary(conversation_text)
    st.subheader("Suggested Follow-Up Message:")
    st.markdown(follow_up)
