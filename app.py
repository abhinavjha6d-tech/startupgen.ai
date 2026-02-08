import streamlit as st
import google.generativeai as genai
import plotly.graph_objects as go
import json
import re

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Venture.Ai", page_icon="🚀", layout="wide")

# Custom CSS for the Venture.Ai branding
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #0a0c10; border-right: 1px solid #30363d; }
    
    .title-text {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        background: -webkit-linear-gradient(#00d4ff, #9b59b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        margin-bottom: 20px;
    }

    .dashboard-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    
    .user-msg {
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        padding: 12px; border-radius: 15px 15px 0 15px;
        margin: 10px 0; float: right; width: fit-content; max-width: 80%;
    }
    .bot-msg {
        background: rgba(255, 255, 255, 0.08);
        padding: 12px; border-radius: 15px 15px 15px 0;
        margin: 10px 0; float: left; width: fit-content; max-width: 80%;
        border: 1px solid rgba(0, 212, 255, 0.2);
    }
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 2. DYNAMIC CHARTING ---
def draw_funding_pie(data):
    fig = go.Figure(data=[go.Pie(
        labels=list(data.keys()), 
        values=list(data.values()), 
        hole=.7,
        marker=dict(colors=['#00f2ff', '#7000ff', '#00ff88', '#ff0077'])
    )])
    fig.update_layout(
        showlegend=False, margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=220
    )
    return fig

def draw_growth_line(values):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=['Q1', 'Q2', 'Q3', 'Q4'], y=values,
        mode='lines+markers', line=dict(color='#00d4ff', width=4),
        fill='tozeroy', fillcolor='rgba(0, 212, 255, 0.1)'
    ))
    fig.update_layout(
        xaxis=dict(showgrid=False, color='white'), yaxis=dict(showgrid=False, color='white'),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=10, b=10, l=10, r=10), height=180
    )
    return fig

# --- 3. AI LOGIC ---
class StartupAdvisor:
    def __init__(self, api_key):
        self.model = None
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-2.5-flash")

    def generate_analysis(self, query):
        if not self.model: return "⚠️ Please enter your API Key in the sidebar.", None
        
        system_prompt = f"""
        Act as a Venture Capitalist Advisor. Analyze this: {query}
        Return your response in two parts:
        1. Natural language advice.
        2. A JSON block at the very end wrapped in triple backticks like this:
        ```json
        {{
            "funding": {{"R&D": 40, "Marketing": 30, "Ops": 20, "Legal": 10}},
            "growth": [10, 25, 55, 90],
            "roi": "4.5x"
        }}
        ```
        """
        try:
            response = self.model.generate_content(system_prompt)
            text = response.text
            json_match = re.search(r'```json\n(.*?)\n```', text, re.DOTALL)
            data = json.loads(json_match.group(1)) if json_match else None
            clean_text = re.sub(r'```json.*?```', '', text, flags=re.DOTALL)
            return clean_text.strip(), data
        except Exception as e:
            return f"Error: {e}", None

# --- 4. MAIN INTERFACE ---
with st.sidebar:
    st.markdown('<div class="title-text">Venture.Ai</div>', unsafe_allow_html=True)
    key = st.text_input("Gemini API Key", type="password", help="Get yours at aistudio.google.com")
    st.divider()
    st.caption("v1.0 - Your AI Co-Founder")
    
    if "chart_data" not in st.session_state:
        st.session_state.chart_data = {
            "funding": {"AI": 25, "Sales": 25, "Ops": 25, "Product": 25}, 
            "growth": [10, 20, 30, 40], 
            "roi": "0x"
        }

advisor = StartupAdvisor(key)

# 2-Column Dashboard Layout
col_left, col_right = st.columns([0.6, 0.4], gap="large")

with col_left:
    st.markdown("### 💬 Strategic Analysis")
    chat_box = st.container(height=550)
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "bot", "content": "Welcome to Venture.Ai. Tell me about your startup idea or current bottleneck."}]

    with chat_box:
        for m in st.session_state.messages:
            div = "user-msg" if m["role"] == "user" else "bot-msg"
            st.markdown(f"<div class='{div}'>{m['content']}</div><div style='clear:both;'></div>", unsafe_allow_html=True)

    if prompt := st.chat_input("Enter your query..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("Calculating..."):
            advice, data = advisor.generate_analysis(prompt)
            if data: st.session_state.chart_data = data
            st.session_state.messages.append({"role": "bot", "content": advice})
        st.rerun()

with col_right:
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.write("### 📊 Funding Allocation")
    st.plotly_chart(draw_funding_pie(st.session_state.chart_data["funding"]), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.write("### 📈 Market Growth")
    st.plotly_chart(draw_growth_line(st.session_state.chart_data["growth"]), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.metric("Estimated ROI", st.session_state.chart_data["roi"], delta="Market Potential")
    st.markdown('</div>', unsafe_allow_html=True)
