# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "streamlit",
#     "google-generativeai",
#     "plotly"
# ]
# ///

import streamlit as st
import google.generativeai as genai
import time
import sys

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(page_title="Ventura AI", page_icon="🚀", layout="wide")

st.markdown("""
<style>
.stApp { background: linear-gradient(to right, #f8f9fa, #e9ecef); }

.user-msg { 
    background-color: #2b313e; color: white; 
    padding: 15px; border-radius: 15px 15px 0 15px; 
    margin: 10px 0; display: inline-block; max-width: 80%; float: right;
}
.bot-msg { 
    background-color: #ffffff; color: #333; 
    padding: 15px; border-radius: 15px 15px 15px 0; 
    margin: 10px 0; display: inline-block; max-width: 80%; 
    box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e0e0e0;
    white-space: pre-wrap;
}

#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGIC: THE BRAIN ---
class StartupAdvisor:
    def __init__(self, api_key: str | None):
        self.api_key = api_key
        self.model = None
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-pro")  # Old SDK compatible model

    def generate_response(self, mode, query):
        if not self.api_key or not self.model:
            return "⚠️ Please enter your API Key in the sidebar to start."

        prompts = {
            "🧠 Strategy": (
                f"Act as a Y-Combinator partner. Analyze this situation decisively:\n"
                f"'{query}'\n\n"
                f"Give 3 bullet points on what to do next. Be brutal but helpful."
            ),
            "💡 Idea Gen": (
                f"Generate a contrarian startup idea based on:\n"
                f"'{query}'\n\n"
                f"Format:\n**Concept**\n**Moat** (Competition barrier)\n**First Step**"
            ),
            "📊 Competition": (
                f"List the top 3 competitors for:\n"
                f"'{query}'\n\n"
                f"Then identify one 'Blue Ocean' feature they all miss."
            )
        }

        try:
            response = self.model.generate_content(prompts[mode])
            return response.text
        except Exception as e:
            return f"❌ Gemini API Error:\n{e}"

# --- 3. UI: THE FRONTEND ---
def main():
    # Sidebar
    with st.sidebar:
        st.header("🚀 Ventura AI")
        st.write("Your Pocket Co-Founder")

        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            st.success("✅ API Key Loaded from Cloud")
        else:
            api_key = st.text_input("🔑 Enter Gemini API Key", type="password")
            st.caption("[Get Free Key](https://aistudio.google.com/app/apikey)")

        st.divider()
        mode = st.radio("Select Mode:", ["🧠 Strategy", "💡 Idea Gen", "📊 Competition"])

        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

    advisor = StartupAdvisor(api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "bot", "content": "Hello Founder! I'm ready. What's on your mind?"}
        ]

    # Display chat history
    for msg in st.session_state.messages:
        div_class = "user-msg" if msg["role"] == "user" else "bot-msg"
        st.markdown(
            f"<div style='width:100%; overflow:hidden;'>"
            f"<div class='{div_class}'>{msg['content']}</div></div>",
            unsafe_allow_html=True
        )

    # Input
    if prompt := st.chat_input("Ask about strategy, ideas, or risks..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Typing animation
        placeholder = st.empty()
        placeholder.markdown(f"<div class='bot-msg'>AI is typing...</div>", unsafe_allow_html=True)
        time.sleep(0.5)

        # Generate AI response
        response = advisor.generate_response(mode, prompt)

        # Simulate typing effect
        displayed_text = ""
        for char in response:
            displayed_text += char
            placeholder.markdown(f"<div class='bot-msg'>{displayed_text}|</div>", unsafe_allow_html=True)
            time.sleep(0.01)
        placeholder.markdown(f"<div class='bot-msg'>{displayed_text}</div>", unsafe_allow_html=True)

        st.session_state.messages.append({"role": "bot", "content": displayed_text})
        st.rerun()

if __name__ == "__main__":
    main()
