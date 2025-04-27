import streamlit as st

st.set_page_config(page_title="Welcome", page_icon="👋", layout="centered")

# --- Welcome Message ---
st.title("👋 Welcome to the Business Networking Follow-Up Generator!")

st.write("""
This app helps you:
- 📄 Upload your resume (PDF or DOCX)
- 🤖 Automatically extract important details
- 📁 Recieve feedback on past conversations
- 🖊️ Generate customized follow up emails
- ✨ Get personalized **career coaching feedback** powered by **Gemini AI**

---

**How to get started:**
1. Go to the **Business Networking Follow-Up Generator** page using the sidebar ➡️
2. Upload your resume
3. Review past conversations
4. Receive feedback instantly!

---
Built with ❤️ using Streamlit and Google Gemini API.

Let's supercharge your career conversations! 🚀
""")

st.info("Use the sidebar to navigate through the app!")
