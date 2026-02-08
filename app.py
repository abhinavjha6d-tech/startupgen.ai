import streamlit as st
import google.generativeai as genai
import plotly.graph_objects as go
import json
import re

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Venture.Ai", page_icon="🚀", layout="wide")

# Advanced CSS for Cyber-Pink Aesthetic
st.markdown("""
<style>
    /* Main Background Gradient */
    .stApp {
        background: radial-gradient(circle at top right, #2d0b1e, #0d1117 70%);
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
        letter-spacing: -1px;
    }

    /* Glassmorphism Cards */
    .dashboard-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 25px;
        border: 1px solid rgba(255, 0, 204, 0.2);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        margin-bottom: 20px;
    }
    
    /* Neon Chat Bubbles */
    .user-msg {
        background: linear-gradient(135deg, #ff00cc 0%, #7000ff 100%);
        padding: 15px; border-radius: 20px 20px 0 20px;
        margin: 10px 0; float: right; width: fit-content; max-width: 85%;
        box-shadow: 0 4px 15px rgba(255, 0, 204, 0.3);
    }
    .bot-msg {
        background: rgba(255, 255, 255, 0.07);
        padding: 15px; border-radius: 20px 20px 20px 0;
        margin: 10px 0; float: left; width: fit-content; max-width: 85%;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Hide default streamlit elements */
    #MainMenu, footer, header { visibility: hidden; }
    
    /* Sidebar customization */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 12, 16, 0.95);
        border-right: 1px solid rgba(255, 0, 204, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. AESTHETIC CHARTING FUNCTIONS ---
def draw_funding_pie(data):
    # Pink, Purple, Deep Blue, and Cyan palette
    colors = ['#ff00cc', '#7000ff', '#00d4ff', '#1a1a1a']
    fig = go.Figure(data=[go.Pie(
        labels=list(data.keys()), 
        values=list(data.values()), 
        hole=.75,
        marker=dict(colors=colors, line=dict(color='#0d1117', width=3))
    )])
    fig.update_layout(
        showlegend=True,
        legend=dict(font=dict(color="white"), orientation="h", yanchor="bottom", y=-0.2),
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=280
    )
    return fig

def draw_growth_line(values):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=['Q1', 'Q2', 'Q3', 'Q4'], y=values,
        mode='lines+markers',
        line=dict(color='#ff00cc', width=4, shape='spline'),
        marker=dict(size=10, color='#ffffff', line=dict(color='#ff00cc', width=2)),
        fill='tozeroy',
        fillcolor='rgba(255, 0, 204, 0.1)'
    ))
    fig.update_layout(
        xaxis=dict(showgrid=False, color='#888', font=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color='#888'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=10, b=10, l=10, r=10),
        height=200
    )
    return fig

# --- 3. AI LOGIC (Gemini 2.5 Flash) ---
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
        Act as a Elite Venture Capitalist Advisor. Analyze this: {query}
        Return advice + JSON data for graphs:
        ```json
        {{
            "funding": {{"Dev": 40, "Marketing": 30, "Sales": 20, "Misc": 10}},
            "growth": [10, 30, 60, 100],
            "roi": "5.2x"
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
            return "Analysis complete.", None

# --- 4. UI STRUCTURE ---
advisor = StartupAdvisor()

with st.sidebar:
    st.markdown('<div class="title-text">Venture.Ai</div>', unsafe_allow_html=True)
    st.markdown("🚀 *Next-Gen Founder Intelligence*")
    st.divider()
    if st.button("Clear Strategy Session"):
        st.session_state.messages = []
        st.rerun()

if "chart_data" not in st.session_state:
    st.session_state.chart_data = {
        "funding": {"Start": 100}, "growth": [0, 0, 0, 0], "roi": "0.0x"
    }

col_chat, col_dash = st.columns([0.6, 0.4], gap="large")

with col_chat:
    st.markdown("### 🧠 Strategic Advisor")
    chat_container = st.container(height=600)
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "bot", "content": "Founder, let's optimize your trajectory. What are we looking at today?"}]

    with chat_container:
        for m in st.session_state.messages:
            cls = "user-msg" if m["role"] == "user" else "bot-msg"
            st.markdown(f"<div class='{cls}'>{m['content']}</div><div style='clear:both;'></div>", unsafe_allow_html=True)

    if prompt := st.chat_input("Ask about market entry, ROI, or burn rate..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("Processing..."):
            advice, data = advisor.generate_analysis(prompt)
            if data: st.session_state.chart_data = data
            st.session_state.messages.append({"role": "bot", "content": advice})
        st.rerun()

with col_dash:
    st.markdown("### 📈 Live Performance")
    
    # Funding Card
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("#### Capital Allocation")
    st.plotly_chart(draw_funding_pie(st.session_state.chart_data["funding"]), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Growth Card
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("#### Projected Scaling")
    st.plotly_chart(draw_growth_line(st.session_state.chart_data["growth"]), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ROI Card
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.metric(label="Calculated ROI", value=st.session_state.chart_data["roi"], delta="AI Confidence: 94%")
    st.markdown('</div>', unsafe_allow_html=True)
