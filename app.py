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

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(page_title="Ventura AI", page_icon="🚀", layout="wide")

# Custom CSS for "SaaS-like" UI (Removes default Streamlit look)
st.markdown("""
<style>
    /* Main Background */
    .stApp { background: linear-gradient(to right, #f8f9fa, #e9ecef); }
    
    /* Chat Bubbles */
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
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 2. LOGIC: THE BRAIN ---
class StartupAdvisor:
    def __init__(self, api_key):
        self.api_key = api_key
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash') # Fast & Efficient model

    def generate_response(self, mode, query):
        if not self.api_key:
            return "⚠️ Please enter your API Key in the sidebar to start."

        # Specialized Prompts for each mode
        prompts = {
            "🧠 Strategy": f"Act as a Y-Combinator partner. Analyze this situation decisively: '{query}'. Give 3 bullet points on what to do next. Be brutal but helpful.",
            "💡 Idea Gen": f"Generate a contrarian startup idea based on: '{query}'. Format: **Concept**, **Moat** (Competition barrier), **First Step**.",
            "📊 Competition": f"List the top 3 competitors for: '{query}'. Then, identify one 'Blue Ocean' feature they all miss."
        }
        
        try:
            response = self.model.generate_content(prompts[mode])
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"

# --- 3. UI: THE FRONTEND ---
def main():
    # Sidebar
    with st.sidebar:
        st.header("🚀 Ventura AI")
        st.write("Your Pocket Co-Founder")
        
        # Smart Secret Management (Checks for Cloud Secrets first, then asks User)
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

    # Chat Interface
    advisor = StartupAdvisor(api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "bot", "content": "Hello Founder! I'm ready. What's on your mind?"}]

    # Display History
    for msg in st.session_state.messages:
        div_class = "user-msg" if msg['role'] == "user" else "bot-msg"
        st.markdown(f"<div style='width:100%; overflow:hidden;'><div class='{div_class}'>{msg['content']}</div></div>", unsafe_allow_html=True)

    # Input Area
    if prompt := st.chat_input("Ask about strategy, ideas, or risks..."):
        # 1. User Logic
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.markdown(f"<div style='width:100%; overflow:hidden;'><div class='user-msg'>{prompt}</div></div>", unsafe_allow_html=True)
        
        # 2. AI Logic
        with st.spinner("Analyzing market data..."):
            response = advisor.generate_response(mode, prompt)
            
            # Simulate "typing" for realism
            time.sleep(0.5) 
            
            st.session_state.messages.append({"role": "bot", "content": response})
            st.rerun() # Force refresh to show new message with correct styling

if __name__ == "__main__":
    main()
