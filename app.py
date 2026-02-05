# /// script
# requires-python = ">=3.9"
# dependencies = [
#      "streamlit",
#      "google-generativeai",
#      "plotly"
# ]
# ///

import streamlit as st
import google.generativeai as genai
import time

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(page_title="Ventura AI", page_icon="🚀", layout="wide")

# Custom CSS for a professional chat interface
st.markdown("""
<style>
    .stApp { background: linear-gradient(to right, #f8f9fa, #e9ecef); }
    
    .user-msg { 
        background-color: #2b313e; color: white; 
        padding: 15px; border-radius: 15px 15px 0 15px; 
        margin: 10px 0; display: inline-block; max-width: 80%; float: right;
        font-family: 'Inter', sans-serif;
    }
    .bot-msg { 
        background-color: #ffffff; color: #333; 
        padding: 15px; border-radius: 15px 15px 15px 0; 
        margin: 10px 0; display: inline-block; max-width: 80%; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e0e0e0;
        white-space: pre-wrap; font-family: 'Inter', sans-serif;
    }
    
    /* Hide default Streamlit elements for a cleaner look */
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGIC: THE BRAIN ---
class StartupAdvisor:
    def __init__(self, api_key: str | None):
        self.api_key = api_key
        self.model = None
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                # FIX: Using 'gemini-3-flash-preview' instead of 'gemini-latest'
                self.model = genai.GenerativeModel("gemini-3-flash-preview")
            except Exception as e:
                st.error(f"Configuration Error: {e}")

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
            return f"❌ Gemini API Error: {str(e)}"

# --- 3. UI: THE FRONTEND ---
def main():
    # Sidebar Setup
    with st.sidebar:
        st.header("🚀 Ventura AI")
        st.write("Your Pocket Co-Founder")

        # Load API Key from Secrets or User Input
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            st.success("✅ API Key Loaded")
        else:
            api_key = st.text_input("🔑 Enter Gemini API Key", type="password")
            st.caption("[Get Free Key](https://aistudio.google.com/app/apikey)")

        st.divider()
        mode = st.radio("Select Mode:", ["🧠 Strategy", "💡 Idea Gen", "📊 Competition"])

        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

    advisor = StartupAdvisor(api_key)

    # Initialize session state for messages
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "bot", "content": "Hello Founder! I'm ready. What's on your mind?"}
        ]

    # Display chat history
    for msg in st.session_state.messages:
        div_class = "user-msg" if msg["role"] == "user" else "bot-msg"
        alignment = "right" if msg["role"] == "user" else "left"
        st.markdown(
            f"<div style='width:100%; overflow:hidden;'>"
            f"<div class='{div_class}' style='float:{alignment};'>{msg['content']}</div></div>",
            unsafe_allow_html=True
        )

    # Chat Input
    if prompt := st.chat_input("Ask about strategy, ideas, or risks..."):
        # 1. Store and display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.markdown(
            f"<div style='width:100%; overflow:hidden;'>"
            f"<div class='user-msg' style='float:right;'>{prompt}</div></div>",
            unsafe_allow_html=True
        )

        # 2. Setup AI Response container
        placeholder = st.empty()
        
        # 3. Generate AI response
        with st.spinner("Thinking..."):
            response_text = advisor.generate_response(mode, prompt)

        # 4. Typing animation
        displayed_text = ""
        for char in response_text:
            displayed_text += char
            placeholder.markdown(
                f"<div style='width:100%; overflow:hidden;'>"
                f"<div class='bot-msg' style='float:left;'>{displayed_text}▌</div></div>", 
                unsafe_allow_html=True
            )
            time.sleep(0.005) # Fast typing speed
        
        # Final update to remove the cursor
        placeholder.markdown(
            f"<div style='width:100%; overflow:hidden;'>"
            f"<div class='bot-msg' style='float:left;'>{displayed_text}</div></div>", 
            unsafe_allow_html=True
        )

        # 5. Store in history and rerun to clean up the UI
        st.session_state.messages.append({"role": "bot", "content": displayed_text})
        st.rerun()

if __name__ == "__main__":
    main()
