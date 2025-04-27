import streamlit as st
import groq
import re
import requests
import json
import os
from datetime import datetime

st.title("Business Networking Follow-Up Generator")

# — your Groq API key (move to env var in prod!) —
GROQ_API_KEY = "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"

DATA_PATH = "conversations.json"
URL = "https://la-hacks-2025-backend.onrender.com/api/get-conversations"

# — helpers for I/O & dedupe —

def load_entries(path=DATA_PATH):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_entries(entries, path=DATA_PATH):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

def fetch_remote():
    try:
        resp = requests.get(URL)
        resp.raise_for_status()
        return resp.json().get("transcriptions", [])
    except Exception as e:
        st.error(f"Failed to fetch: {e}")
        return []

def make_clickable(text):
    pattern = r"(https?://www\.linkedin\.com/[^\s]+)"
    return re.sub(pattern, r'[\1](\1)', text)

def analyze_summary(conversation_text):
    client = groq.Groq(api_key=GROQ_API_KEY)
    prompt = (
        "You are an expert networking assistant. "
        "Given a conversation between two people who are networking professionally, "
        "suggest specific friendly business follow-ups they could send. "
        "Be casual but professional — suggest things like scheduling a coffee chat, "
        "continuing a topic they discussed, offering to help, or connecting on LinkedIn. "
        "Mention when and how they met if possible.\n\n"
        + conversation_text
    )
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user",   "content": conversation_text},
        ]
    )
    return response.choices[0].message.content

def clear_entries(path=DATA_PATH):
    """Overwrite the JSON file with an empty list."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

# — UI: fetch & save —

if st.button("Fetch & Save New Conversation", type = "secondary"):
    new_conv = fetch_remote()
    if new_conv:
        entries = load_entries()
        seen = {json.dumps(e["transcriptions"], sort_keys=True) for e in entries}
        serial = json.dumps(new_conv, sort_keys=True)
        if serial not in seen:
            entries.append({
                "timestamp": datetime.now().isoformat() + "Z",
                "transcriptions": new_conv
            })
            save_entries(entries)
            st.success("New conversation saved ✅")
        else:
            st.info("No new data to save.")
    else:
        st.warning("No conversation returned.")

# — UI: display & inspect —

entries = load_entries()
if not entries:
    st.info("No conversations yet. Click “Fetch & Save” above.")
    st.stop()

st.header("All Saved Conversations")
for i, e in enumerate(entries, 1):
    st.markdown(f"**#{i} — {e['timestamp']}**")
    for turn in e["transcriptions"]:
        st.write(f"- {make_clickable(turn)}")

if st.button("Clear All Conversations", type = "primary", icon = '🗑️'):
    clear_entries()
    st.success("All conversations cleared.")
    st.info("Please refresh the page.")

st.markdown("---")
st.header("Generate Follow-Up for a Conversation")
idx = st.selectbox("Pick one:", list(range(1, len(entries)+1))) - 1
conv_text = "\n".join(entries[idx]["transcriptions"])

if st.button("Generate Follow-Up"):
    with st.spinner("Analyzing…"):
        follow_up = analyze_summary(conv_text)
    st.subheader("Suggested Follow-Ups")
    st.write(follow_up)