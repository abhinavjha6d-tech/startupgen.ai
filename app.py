import streamlit as st
import google.generativeai as genai
import plotly.graph_objects as go
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Startup Sphere AI", page_icon="🌐", layout="wide")

# Custom CSS for the "Glassmorphism" Dark UI
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0d1117;
        color: #ffffff;
    }
    
    /* Title Styling */
    .title-text {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        background: -webkit-linear-gradient(#00d4ff, #9b59b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        text-align: center;
        margin-bottom: 30px;
    }

    /* Container Styling (Cards) */
    [data-testid="stVerticalBlock"] > div:has(div.card-container) {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }

    /* Message Bubbles */
    .user-msg {
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        color: white; padding: 15px; border-radius: 15px 15px 0 15px;
        margin: 10px 0; float: right; width: fit-content; max-width: 85%;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .bot-msg {
        background: rgba(255, 255, 255, 0.05);
        color: #e0e0e0; padding: 15px; border-radius: 15px 15px 15px 0;
        margin: 10px 0; float: left; width: fit-content; max-width: 85%;
        border: 1px solid rgba(0, 212, 255, 0.3);
    }

    /* Sidebar Tweaks */
    [data-testid="stSidebar"] {
        background-color: #0a0c10;
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Hide default streamlit elements */
    #MainMenu, footer, header { visibility: hidden; }
</style>
<div class="title-text">Startup Sphere AI</div>
""", unsafe_allow_html=True)

# --- 2. DATA VISUALIZATION FUNCTIONS ---
def get_donut_chart():
    # Matches the "Funding Allocation" colors in your image
    labels = ['AI', 'FinTech', 'HealthTech', 'Other']
    values = [40, 25, 20, 15]
    colors = ['#00f2ff', '#7000ff', '#00ff88', '#444']
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.7)])
    fig.update_traces(hoverinfo='label+percent', textinfo='none', 
                      marker=dict(colors=colors, line=dict(color='#0d1117', width=2)))
    fig.update_layout(
        showlegend=True,
        legend=dict(font=dict(color="white"), orientation="h", yanchor="bottom", y=-0.2),
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=250
    )
    return fig

def get_growth_chart():
    # Matches the "Market Growth" neon line in your image
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=['Jan', 'Feb', 'Mar', 'Apr'], y=[100, 150, 250, 400],
        mode='lines+markers',
        line=dict(color='#00d4ff', width=4),
        fill='tozeroy',
        fillcolor='rgba(0, 212, 255, 0.1)'
    ))
    fig.update_layout(
        xaxis=dict(showgrid=False, color='gray'),
        yaxis=dict(showgrid=False, color='gray'),
        margin=dict(t=20, b=20, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=200
    )
    return fig

# --- 3. LOGIC ---
class StartupAdvisor:
    def __init__(self, api_key):
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash") # Use stable model
        else:
            self.model = None

    def ask(self, query):
        if not self.model: return "Please enter API key."
        response = self.model.generate_content(f"Context: Startup Advisor. User asks: {query}")
        return response.text

# --- 4. MAIN LAYOUT ---
# Sidebar for Settings
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2091/2091665.png", width=100)
    api_key = st.text_input("Gemini API Key", type="password")
    st.divider()
    st.info("Metrics update based on AI analysis of your venture.")

advisor = StartupAdvisor(api_key)

# Main Dashboard Grid
col_chat, col_stats = st.columns([0.6, 0.4], gap="large")

with col_chat:
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.subheader("💬 AI Co-Founder")
    
    # Message Container
    chat_subcol = st.container(height=500)
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "bot", "content": "Welcome to Startup Sphere. How can I assist with your venture today?"}]

    with chat_subcol:
        for msg in st.session_state.messages:
            cls = "user-msg" if msg["role"] == "user" else "bot-msg"
            st.markdown(f"<div class='{cls}'>{msg['content']}</div><div style='clear:both;'></div>", unsafe_allow_html=True)

    if prompt := st.chat_input("Ask about strategy, ROI, or funding..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("Analyzing..."):
            ans = advisor.ask(prompt)
            st.session_state.messages.append({"role": "bot", "content": ans})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col_stats:
    # Top Stats Card
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.subheader("Funding Allocation")
    st.plotly_chart(get_donut_chart(), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.write("") # Spacer
    
    # Bottom Stats Card
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.subheader("Market Growth")
    st.plotly_chart(get_growth_chart(), use_container_width=True)
    
    # ROI Metric
    st.divider()
    c1, c2 = st.columns(2)
    c1.metric("Projected ROI", "4.8x", "+0.5")
    c2.metric("Burn Rate", "$12k/mo", "-2%")
    st.markdown('</div>', unsafe_allow_html=True)
