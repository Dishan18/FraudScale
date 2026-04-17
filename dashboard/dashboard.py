import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import os

st.set_page_config(page_title="FraudScale Live Command", layout="wide", initial_sidebar_state="collapsed")
API_URL = os.getenv("API_URL", "http://api:8000")

st_autorefresh(interval=30000, key="refresh")

if "prev_stats" not in st.session_state:
    st.session_state.prev_stats = {
        "total_records": 0,
        "fraud_count": 0,
        "fraud_rate": 0,
        "unique_users": 0
    }

prev = {
    "total_records": st.session_state.prev_stats.get("total_records", 0),
    "fraud_count": st.session_state.prev_stats.get("fraud_count", 0),
    "fraud_rate": st.session_state.prev_stats.get("fraud_rate", 0),
    "unique_users": st.session_state.prev_stats.get("unique_users", 0),
}

st.markdown("""
<style>

html, body, [data-testid="stAppViewContainer"] {
    height: 100vh;
    overflow: hidden;
    background: linear-gradient(135deg, #0e1117 0%, #151a24 60%, #1b2230 100%);
}

.main {
    height: 100vh;
    overflow: hidden;
}

.block-container {
    padding-top: 1rem !important;
    padding-bottom: 0rem !important;
}

/* KPI */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(40,44,52,0.7), rgba(28,31,38,0.9));
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 18px !important;
    text-align: center;
    transition: all 0.25s ease;
    backdrop-filter: blur(6px);
    animation: fadeInUp 0.6s ease;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-4px) scale(1.02);
    border: 1px solid rgba(255,255,255,0.12);
}

[data-testid="stMetricValue"] {
    font-size: 28px !important;
    font-weight: 600;
}

[data-testid="stMetricDelta"] {
    animation: pulse 0.6s ease;
}

.section-header {
    font-size: 0.95rem;
    font-weight: 500;
    color: #9aa4b2;
    margin-bottom: 6px;
    display: flex;
    justify-content: center;
}

/* Tooltip */
.tooltip { position: relative; display: inline-block; cursor: help; }
.tooltip .tooltiptext {
    visibility: hidden;
    width: 240px;
    background-color: #2c2f36;
    color: #fff;
    text-align: left;
    border-radius: 8px;
    padding: 10px;
    position: absolute;
    z-index: 100;
    top: 120%;
    left: 0;
    opacity: 0;
    transition: opacity 0.3s;
    font-size: 11px;
}
.tooltip:hover .tooltiptext { visibility: visible; opacity: 1; }

/* Charts */
[data-testid="stDataFrame"], .stPlotlyChart {
    animation: fadeIn 0.5s ease;
}

/* Animations */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
    0% { transform: scale(1.1); }
    100% { transform: scale(1); }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

/* Footer */
.footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    color: #555;
    text-align: center;
    font-size: 10px;
}

</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=25)
def fetch_data(endpoint):
    try:
        r = requests.get(f"{API_URL}/{endpoint}", timeout=3)
        return r.json()
    except Exception as e:
        st.warning(f"API error: {e}")
        return {}

stats = fetch_data("stats")
live_data = fetch_data("live")
df = pd.DataFrame(live_data) if live_data else pd.DataFrame()

st.markdown("<h2 style='margin:0; color:white;'>🛡️ FraudScale <span style='color:#666; font-size:14px;'>LIVE COMMAND</span></h2>", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)

def get_delta(curr, prev, is_percent=False):
    diff = curr - prev
    if is_percent:
        diff = diff * 100  

    if diff > 0:
        return f"+{diff:.2f}", "normal"
    elif diff < 0:
        return f"{diff:.2f}", "inverse"
    return "0.00", "off"

with k1:
    val = stats.get("total_records", 0)
    delta, color = get_delta(val, prev["total_records"])
    st.markdown('<div class="tooltip"><span class="section-header">Throughput</span><span class="tooltiptext">Total reviews processed</span></div>', unsafe_allow_html=True)
    st.metric("", val, delta=delta, delta_color=color)

with k2:
    val = stats.get("fraud_count", 0)
    delta, color = get_delta(val, prev["fraud_count"])
    st.markdown('<div class="tooltip"><span class="section-header">Fraud Cases</span><span class="tooltiptext">Detected fraud</span></div>', unsafe_allow_html=True)
    st.metric("", val, delta=delta, delta_color="inverse")

with k3:
    val = stats.get("fraud_rate", 0)
    delta, color = get_delta(val, prev["fraud_rate"], is_percent=True)
    st.markdown('<div class="tooltip"><span class="section-header">Fraud Rate</span><span class="tooltiptext">Fraud percentage</span></div>', unsafe_allow_html=True)
    st.metric("", f"{val*100:.2f}%", delta=f"{delta}%", delta_color=color)

with k4:
    val = stats.get("unique_users", 0)
    delta, color = get_delta(val, prev["unique_users"])
    st.markdown('<div class="tooltip"><span class="section-header">Active Bots</span><span class="tooltiptext">Unique flagged users</span></div>', unsafe_allow_html=True)
    st.metric("", val, delta=delta, delta_color=color)

if stats:
    st.session_state.prev_stats = stats

st.markdown("<hr style='margin:10px 0; border-color:#1c1f26;'>", unsafe_allow_html=True)

col_left, col_mid, col_right = st.columns([1.5, 1, 1])

with col_left:
    st.markdown('<div class="tooltip"><span class="section-header">Alert Stream</span><span class="tooltiptext">Live suspicious activity</span></div>', unsafe_allow_html=True)
    if not df.empty:
        disp = df[["user_id", "review_count", "similarity_score", "is_fraud"]].copy()
        st.dataframe(disp, height=300, use_container_width=True, hide_index=True)
    else:
        st.info("Ingesting stream...")

with col_mid:
    st.markdown('<div class="tooltip"><span class="section-header">Distribution</span><span class="tooltiptext">Fraud vs normal</span></div>', unsafe_allow_html=True)
    if not df.empty:
        fig_pie = px.pie(df, names="is_fraud", hole=0.6, color_discrete_map={1: '#ff4b4b', 0: '#00cc96'})
        fig_pie.update_layout(height=300, margin=dict(t=0,b=0,l=0,r=0), showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})

with col_right:
    st.markdown('<div class="tooltip"><span class="section-header">Similarity Trend</span><span class="tooltiptext">Bot similarity pattern</span></div>', unsafe_allow_html=True)
    if not df.empty:
        fig_bar = px.bar(df.head(10), x="user_id", y="similarity_score", color="similarity_score", color_continuous_scale='Viridis')
        fig_bar.update_layout(height=300, margin=dict(t=20,b=0,l=0,r=0), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title=None)
        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

st.markdown('<div class="footer">Dishan Sarkar © 2026 | System Active | Spark 3.5</div>', unsafe_allow_html=True)