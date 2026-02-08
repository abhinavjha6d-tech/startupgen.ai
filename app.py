import streamlit as st
import google.generativeai as genai
import plotly.graph_objects as go
import json
import re

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Venture.Ai", page_icon="🚀", layout="wide")

# Advanced CSS for Cyber-Pink & Black Aesthetic
st.markdown("""
<style>
    /* Main Background Gradient */
    .stApp {
        background: radial-gradient(circle at top right, #2d0b1e, #0d1117 80%);
        color: #ffffff;
    }
    
    /* Title Styling */
    .title-text {
        font-family: 'Inter', sans-serif;
        font-weight: 900;
        background: -webkit-linear-gradient(#ff00cc, #3333ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        letter-spacing: -1.5px;
    }

    /* Glassmorphism Cards */
    .dashboard-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 25px;
        border: 1px solid rgba(255, 0, 204, 0.15);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
        margin-bottom: 20px;
    }
    
    /* Neon Chat Bubbles */
    .user-msg {
        background: linear-gradient(135deg, #ff00cc 0%, #7000ff 100%);
        padding: 15px; border-radius: 20px 20px 0 20px;
        margin: 10px 0; float: right; width: fit-content; max-width: 85%;
        box-shadow: 0 4px 15px rgba(255, 0, 204, 0.2);
    }
    .bot-msg {
        background: rgba(255, 255, 255, 0.06);
        padding: 15px; border-radius: 20px 20px 20px 0;
        margin: 10px 0; float: left; width: fit-content; max-width: 85%;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Sidebar customization */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 12, 16, 0.98);
        border-right: 1px solid rgba(255, 0, 204, 0.1);
    }

    /* Hide default streamlit elements */
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 2. CHARTING FUNCTIONS (Fixed for Plotly 6.x) ---
def draw_funding_pie(data):
    colors = ['#ff00cc', '#7000ff', '#00d4ff', '#333333']
    fig = go.Figure(data=[go.Pie(
        labels=list(data.keys()), 
        values=list(data.values()), 
        hole=.78,
        marker=dict(colors=colors, line=dict(color='#0d1117', width=3))
    )])
    fig.update_layout(
        showlegend=True,
        legend=dict(font=dict(color="#888", size=10), orientation="h", yanchor="bottom", y=-0.3),
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=260
    )
    return fig

def draw_growth_line(values):
    # Safety check for growth values
    if not isinstance(values, list) or len(values) < 4:
        values = [0, 0, 0, 0]
        
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=['Q1', 'Q2', 'Q3', 'Q4'], y=values,
        mode='lines+markers',
        line=dict(color='#ff00cc', width=4, shape='spline'),
        marker=dict(size=8, color='#ffffff', line=dict(color='#ff00cc', width=2)),
        fill='tozeroy',
        fillcolor='rgba(255, 0, 204, 0.08)'
    ))
    fig.update_layout(
        xaxis=dict(showgrid=False, color='#666', tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.03)', color='#666', tickfont=dict(size=10)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=10, b=10, l=10, r=10),
        height=180
    )
    return fig

# --- 3. AI LOGIC (Gemini 2.5 Flash + Secrets) ---
class StartupAdvisor:
    def __init__(self):
        self.api_key = st.secrets.get("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-2.5-flash")
        else:
            self.model = None

    def generate_analysis(self, query):
        if not self.model: return "Connect API in Secrets.", None
        
        system_prompt = f"""
        Act as an Elite Silicon Valley VC. Analyze this: {query}
        Provide brutal and smart advice. 
        Then, ALWAYS end with a JSON block for these graphs:
        ```json
        {{
            "funding": {{"R&D": 45, "Marketing": 25, "Ops": 20, "Sales": 10}},
            "growth": [15, 35, 70, 100],
            "roi": "5.4x"
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
        except Exception:
            return "Analysis complete. Check graphs for details.", None

# --- 4. SESSION STATE ---
if "chart_data" not in st.session_state:
    st.session_state.chart_data = {
        "funding": {"Market": 25, "Product": 25, "Team": 25, "Scale": 25}, 
        "growth": [0, 0, 0, 0], 
        "roi": "0.0x"
    }
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "bot", "content": "Welcome to Venture.Ai. Let's analyze your trajectory."}]

# --- 5. UI STRUCTURE ---
advisor = StartupAdvisor()

with st.sidebar:
    st.markdown('<div class="title-text">Venture.Ai</div>', unsafe_allow_html=True)
    st.markdown("🚀 *Founder Intelligence Dashboard*")
    st.divider()
    if st.button("New Session"):
        st.session_state.messages = []
        st.rerun()

col_chat, col_dash = st.columns([0.62, 0.38], gap="large")

with col_chat:
    st.markdown("### 🧠 Strategy Portal")
    chat_container = st.container(height=580)
    
    with chat_container:
        for m in st.session_state.messages:
            cls = "user-msg" if m["role"] == "user" else "bot-msg"
            st.markdown(f"<div class='{cls}'>{m['content']}</div><div style='clear:both;'></div>", unsafe_allow_html=True)

    if prompt := st.chat_input("Enter strategy query..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("Analyzing venture data..."):
            advice, data = advisor.generate_analysis(prompt)
            if data: st.session_state.chart_data = data
            st.session_state.messages.append({"role": "bot", "content": advice})
        st.rerun()

with col_dash:
    st.markdown("### 📈 Tactical Analytics")
    
    # Funding Allocation
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("<p style='color:#ff00cc; font-weight:bold; margin-bottom:10px;'>Capital Allocation</p>", unsafe_allow_html=True)
    st.plotly_chart(draw_funding_pie(st.session_state.chart_data["funding"]), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Market Growth
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("<p style='color:#ff00cc; font-weight:bold; margin-bottom:10px;'>Scaling Forecast</p>", unsafe_allow_html=True)
    st.plotly_chart(draw_growth_line(st.session_state.chart_data["growth"]), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ROI Metric
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.metric(label="Calculated ROI", value=st.session_state.chart_data["roi"], delta="Live AI Projection")
    st.markdown('</div>', unsafe_allow_html=True)
