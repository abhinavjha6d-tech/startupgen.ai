# --- 2. LOGIC: THE BRAIN ---
class StartupAdvisor:
    def __init__(self, api_key: str | None):
        self.api_key = api_key
        self.model = None
        if self.api_key:
            genai.configure(api_key=self.api_key)
            # FIX: Changed 'gemini-latest' to a valid 2026 model ID
            self.model = genai.GenerativeModel("gemini-3-flash-preview") 

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
            # This will now catch specific versioning errors if they arise
            return f"❌ Gemini API Error:\n{str(e)}"

# --- 3. UI: THE FRONTEND ---
def main():
    # ... (Keep your existing sidebar and chat history display code) ...

    # Input section - Modified for smoother flow
    if prompt := st.chat_input("Ask about strategy, ideas, or risks..."):
        # 1. Add User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 2. Display the new user message immediately
        st.markdown(
            f"<div style='width:100%; overflow:hidden;'><div class='user-msg'>{prompt}</div></div>",
            unsafe_allow_html=True
        )

        # 3. Generate AI response with typing effect
        placeholder = st.empty()
        response_text = advisor.generate_response(mode, prompt)

        displayed_text = ""
        for char in response_text:
            displayed_text += char
            placeholder.markdown(f"<div class='bot-msg'>{displayed_text}▌</div>", unsafe_allow_html=True)
            time.sleep(0.005) # Slightly faster for better UX
        
        placeholder.markdown(f"<div class='bot-msg'>{displayed_text}</div>", unsafe_allow_html=True)

        # 4. Save to session state and rerun to sync state
        st.session_state.messages.append({"role": "bot", "content": displayed_text})
        st.rerun()
