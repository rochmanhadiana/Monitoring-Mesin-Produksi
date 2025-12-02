import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
import base64
import os
import random
from datetime import datetime, timedelta

# --- 1. SETTING HALAMAN ---
st.set_page_config(
    page_title="Machine Monitor (Speedometer)",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS "IOS 26 GLASS" + "SILVER SPARKLE" ---
bg_css = """
background-color: #F2F4F7;
background-image: 
    radial-gradient(at 15% 25%, hsla(210, 100%, 88%, 0.5) 0px, transparent 55%),
    radial-gradient(at 85% 75%, hsla(280, 80%, 90%, 0.6) 0px, transparent 55%),
    radial-gradient(at 50% 50%, hsla(0, 0%, 100%, 0.8) 0px, transparent 60%),
    radial-gradient(at 80% 10%, hsla(200, 60%, 85%, 0.4) 0px, transparent 50%),
    radial-gradient(at 10% 90%, hsla(340, 80%, 90%, 0.4) 0px, transparent 50%);
background-attachment: fixed;
background-size: cover;
"""

st.markdown(f"""
<style>
    /* IMPORT FONT MODERN */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');

    /* 1. ROOT VARIABLES */
    :root {{
        --glass-bg: rgba(255, 255, 255, 0.65);
        --glass-border: rgba(255, 255, 255, 0.8);
        --text-dark: #1A2333;
        --text-medium: #55657E;
        --shadow-glass: 0 12px 40px rgba(0, 0, 0, 0.05);
        --super-rounded: 30px;
    }}

    /* 2. GLOBAL RESET */
    .stApp {{ {bg_css} font-family: 'Inter', sans-serif; color: var(--text-dark); }}
    
    html, body, p, h1, h2, h3, h4, h5, h6, li, span, div, label, td, th {{
        font-family: 'Inter', sans-serif !important;
        color: var(--text-dark) !important;
        text-shadow: none !important;
    }}

    /* --- 3. JUDUL (SILVER BLUE SPARKLE) --- */
    @keyframes shine {{
        0% {{ background-position: 0% 50%; }}
        100% {{ background-position: 200% 50%; }}
    }}
    
    .bling-text {{
        font-family: 'Inter', sans-serif;
        font-weight: 900;
        font-size: 3.2rem;
        text-align: center;
        margin-bottom: 5px;
        background: linear-gradient(
            90deg, 
            #2c3e50 0%,    #bdc3c7 25%,   #2980b9 50%,   #bdc3c7 75%,   #2c3e50 100%
        );
        background-size: 200% auto;
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 4s linear infinite;
        filter: drop-shadow(0px 0px 8px rgba(41, 128, 185, 0.3));
        letter-spacing: -1px;
    }}

    /* 4. SIDEBAR (ULTRA GLASS) */
    section[data-testid="stSidebar"] {{
        background-color: rgba(255, 255, 255, 0.65) !important;
        backdrop-filter: blur(30px) saturate(150%);
        border-right: 1px solid rgba(255,255,255,0.4);
    }}
    button i, button span, .material-icons, [data-testid="stSidebarCollapseButton"] svg {{
        font-family: 'Material Icons' !important;
        color: #555 !important;
    }}

    /* 5. FIX DROPDOWN & INPUT */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {{
        background-color: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid #FFF !important;
        border-radius: 12px !important;
        color: #000 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }}
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[data-baseweb="menu"] {{
        background-color: #FFFFFF !important;
        border-radius: 14px !important;
        border: 1px solid #EEE !important;
    }}
    li[data-baseweb="menu-item"] {{ color: #000000 !important; background-color: #FFFFFF !important; }}
    li[data-baseweb="menu-item"] div {{ color: #000000 !important; }}
    li[data-baseweb="menu-item"]:hover {{ background-color: #E3F2FD !important; }}
    input {{ color: #000 !important; caret-color: #2980b9 !important; }}

    /* 6. CARD UI */
    div[data-testid="stMetric"], 
    div.stPlotlyChart {{
        background: var(--glass-bg) !important;
        backdrop-filter: blur(20px) saturate(130%);
        border-radius: var(--super-rounded) !important;
        border: 1px solid var(--glass-border) !important;
        box-shadow: var(--shadow-glass) !important;
        padding: 20px !important;
    }}

    /* Typography Metrik */
    div[data-testid="stMetricLabel"] p {{
        font-size: 0.9rem !important;
        color: var(--text-medium) !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    div[data-testid="stMetricValue"] div {{
        font-size: 2.4rem !important;
        font-weight: 800 !important;
        background: linear-gradient(45deg, #1A2333, #2980b9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    /* 7. STATUS BANNER */
    .status-card {{
        background: linear-gradient(135deg, #6DD5FA 0%, #2980B9 100%);
        padding: 20px;
        border-radius: var(--super-rounded);
        text-align: center;
        color: white !important;
        font-weight: 800;
        font-size: 1.6rem;
        box-shadow: 0 15px 35px rgba(41, 128, 185, 0.3);
        margin-bottom: 25px;
        border: 1px solid rgba(255,255,255,0.5);
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}

    /* 8. TABEL CUSTOM */
    .custom-table {{
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 15px;
        overflow: hidden;
        background: #FFFFFF;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        font-size: 0.9rem;
        border: 1px solid #E0E0E0;
    }}
    .custom-table thead tr {{ background-color: #2c3e50; color: #FFFFFF; }}
    .custom-table th {{
        padding: 15px; font-weight: 600; text-transform: uppercase; font-size: 0.8rem; color: #FFFFFF !important; border-bottom: 2px solid #34495e;
    }}
    .custom-table td {{
        padding: 12px 15px; border-bottom: 1px solid #F0F0F0; color: #2c3e50; font-weight: 500;
    }}
    .custom-table tbody tr:nth-child(even) {{ background-color: #F8F9FA; }}
    .custom-table tbody tr:hover {{ background-color: #E3F2FD; }}

    #MainMenu, footer, .stDeployButton {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR KONFIGURASI ---
with st.sidebar:
    st.markdown("### ⚙️ CONTROL PANEL")
    machine_class = st.selectbox("Pilih Kelas Mesin:", ("Class I (Small)", "Class II (Medium)", "Class III (Large Rigid)", "Class IV (Large Soft)"))
    
    if "Class I" in machine_class: defaults = [0.71, 1.80, 4.50]
    elif "Class II" in machine_class: defaults = [1.12, 2.80, 7.10]
    elif "Class III" in machine_class: defaults = [1.80, 4.50, 11.20]
    else: defaults = [2.80, 7.10, 18.00]

    st.divider()
    st.markdown("### 🔧 THRESHOLDS")
    use_custom = st.checkbox("Custom Limits", value=False)
    if use_custom:
        limit_a = st.number_input("Good Limit", value=defaults[0], format="%.2f")
        limit_b = st.number_input("Satisfactory Limit", value=defaults[1], format="%.2f")
        limit_c = st.number_input("Danger Limit", value=defaults[2], format="%.2f")
        current_limits = [limit_a, limit_b, limit_c]
    else:
        current_limits = defaults
        st.caption(f"ISO Standard: {machine_class}")

# --- DATA ENGINE ---
def get_data():
    URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRH2JWeoa-NMYC6MaqCY4YSYy0fqJZ2dFTUyEM96mk23jUts3lASM9ImSayBYp4FURRa14f0YoGLyFK/pub?gid=0&single=true&output=csv'
    csv_url = f"{URL}&t={time.time()}"
    try:
        df = pd.read_csv(csv_url, decimal=',')
        if df.shape[1] < 7: raise Exception("Kolom kurang")
        df = df.iloc[:, 0:7]
        df.columns = ['time', 'timestamp', 'temp', 'ax', 'ay', 'az', 'current']
        cols = ['temp', 'ax', 'ay', 'az', 'current']
        for c in cols:
            if df[c].dtype == object: df[c] = df[c].astype(str).str.replace(',', '.')
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.dropna()
        df['time'] = pd.to_datetime(df['time'], dayfirst=True, errors='coerce')
        if df.empty: raise Exception("Data kosong")
        return df, False 
    except Exception:
        dates = [datetime.now() - timedelta(seconds=i*5) for i in range(50)]
        val = 0.5
        vals = []
        for _ in range(50):
            val += random.uniform(-0.05, 0.05)
            vals.append(abs(val))
        dummy = pd.DataFrame({
            'time': dates,
            'temp': [random.uniform(48, 52) for _ in range(50)],
            'ax': [v * 0.8 for v in vals],
            'ay': [v * 0.6 for v in vals],
            'az': vals,
            'current': [random.uniform(12.5, 13.5) for _ in range(50)]
        })
        return dummy, True

# --- LOGIC ---
df, is_dummy = get_data()
df = df.sort_values(by='time', ascending=True)
last = df.iloc[-1]
vib_val = np.sqrt(last['ax']**2 + last['ay']**2 + last['az']**2)
temp_val = last['temp']

# Status Logic
if vib_val < current_limits[0]: 
    status, gradient = "GOOD", "linear-gradient(135deg, #34C759, #30D158)"
elif vib_val < current_limits[1]: 
    status, gradient = "SATISFACTORY", "linear-gradient(135deg, #FFCC00, #FFD60A)"
elif vib_val < current_limits[2]: 
    status, gradient = "WARNING", "linear-gradient(135deg, #FF9500, #FF9F0A)"
else: 
    status, gradient = "DANGER", "linear-gradient(135deg, #FF3B30, #FF453A)"

rul = 365 if status == "GOOD" else (180 if status == "SATISFACTORY" else (30 if status == "WARNING" else 0))

# --- DASHBOARD LAYOUT ---

# HEADER
st.markdown('<h1 class="bling-text">Machine Health Monitor</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #55657E; margin-bottom: 40px; font-weight: 500;'>Real-time Analytics • ISO 10816 Standard</p>", unsafe_allow_html=True)

# METRICS
c1, c2, c3 = st.columns(3)
c1.metric("Current Load", f"{last['current']:.2f} mA")
c2.metric("Temperature", f"{last['temp']:.2f} °C")
c3.metric("Vibration RMS", f"{vib_val:.3f} mm/s")

st.markdown("<br>", unsafe_allow_html=True)

# STATUS BANNER
st.markdown(f"""
<div class="status-card" style="background: {gradient};">
    SYSTEM STATUS: {status}
</div>
""", unsafe_allow_html=True)

# --- INDIKATOR SPEEDOMETER (GAUGE) ---
col_b1, col_b2, col_b3 = st.columns(3)

def create_gauge(title, value, max_val, unit, limits=None, colors=None, reverse_colors=False):
    
    # Tentukan warna bar utama berdasarkan nilai saat ini
    bar_color = "#1A2333" # Default dark
    if limits and colors:
        if not reverse_colors:
            if value < limits[0]: bar_color = colors[0]
            elif value < limits[1]: bar_color = colors[1]
            else: bar_color = colors[2]
        else: # Untuk RUL (Kebalikannya)
            if value > limits[1]: bar_color = colors[0] # Good (High RUL)
            elif value > limits[0]: bar_color = colors[1] # Warning
            else: bar_color = colors[2] # Danger (Low RUL)

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title, 'font': {'size': 16, 'color': '#55657E', 'family': 'Inter'}},
        number = {'suffix': unit, 'font': {'size': 26, 'color': '#1A2333', 'family': 'Inter', 'weight': 800}, 'valueformat': ".2f"},
        gauge = {
            'axis': {'range': [0, max_val], 'tickwidth': 2, 'tickcolor': "#55657E", 'tickfont': {'size': 10}},
            'bar': {'color': bar_color, 'thickness': 0.25}, # Jarum/Bar penunjuk
            'bgcolor': "rgba(0,0,0,0)", # Background transparan
            'borderwidth': 1,
            'bordercolor': "rgba(0,0,0,0.1)",
            'steps': [
                # Area warna di background gauge
                {'range': [0, max_val], 'color': "rgba(240, 242, 246, 0.5)"} 
            ],
             'threshold': {
                'line': {'color': "red", 'width': 2},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    # Layout agar pas di dalam kartu glass
    fig.update_layout(height=220, margin={'t': 40, 'b': 20, 'l': 30, 'r': 30}, paper_bgcolor='rgba(0,0,0,0)', font={'family': 'Inter'})
    return fig

# Warna Standar
cols_vib = ["#34C759", "#FFCC00", "#FF3B30"] # Green, Yellow, Red
cols_temp = ["#34C759", "#FF9500", "#FF3B30"] # Green, Orange, Red
cols_rul = ["#34C759", "#FF9500", "#FF3B30"] # Green, Orange, Red (Nanti dibalik logicnya)

with col_b1:
    # Gauge Vibration (Batas dari input user)
    st.plotly_chart(create_gauge("Vibration Severity", vib_val, current_limits[2]*1.5, " mm/s", [current_limits[0], current_limits[1]], cols_vib), use_container_width=True)

with col_b2:
    # Gauge Temperature (Batas asumsi: 65, 85)
    st.plotly_chart(create_gauge("Temperature", temp_val, 120, " °C", [65, 85], cols_temp), use_container_width=True)

with col_b3:
    # Gauge RUL (Batas asumsi: 50, 200 hari - Logic DIBALIK)
    st.plotly_chart(create_gauge("Predicted RUL", rul, 365, " Days", [50, 200], cols_rul, reverse_colors=True), use_container_width=True)


# --- CHARTS ---
st.markdown("### 📈 Performance Trends")
col_chart1, col_chart2, col_chart3 = st.columns(3)

common_layout = dict(
    template="plotly_white",
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(255,255,255,0.4)',
    margin=dict(t=50, l=30, r=20, b=30),
    font=dict(family="Inter", color="#1A2333"),
    xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)', showline=False, tickfont=dict(color='#55657E')),
    yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)', showline=False, tickfont=dict(color='#55657E'))
)

with col_chart1:
    fig_c = px.line(df, x='time', y='current', title="Current (Amperage)")
    fig_c.update_traces(line_color='#2980b9', line_width=3, line_shape='spline') 
    fig_c.update_layout(**common_layout)
    st.plotly_chart(fig_c, use_container_width=True)

with col_chart2:
    fig_t = px.line(df, x='time', y='temp', title="Temperature (°C)")
    fig_t.update_traces(line_color='#FF9500', line_width=3, line_shape='spline')
    fig_t.update_layout(**common_layout)
    st.plotly_chart(fig_t, use_container_width=True)

with col_chart3:
    fig_v = px.line(df, x='time', y=['ax','ay','az'], title="Vibration Axes")
    fig_v.update_traces(line_width=2)
    fig_v.update_layout(**common_layout)
    st.plotly_chart(fig_v, use_container_width=True)

# TABLE
st.markdown("### 📋 System Logs")
df_show = df.copy().sort_values(by='time', ascending=False).head(10)
df_show['time'] = df_show['time'].dt.strftime('%H:%M:%S')
for col in ['temp', 'ax', 'ay', 'az', 'current']:
    df_show[col] = df_show[col].apply(lambda x: f"{x:.2f}".replace('.', ','))

df_show.columns = ['Time', 'Timestamp', 'Temp (°C)', 'Ax', 'Ay', 'Az', 'Current (mA)']
html_table = df_show[['Time', 'Temp (°C)', 'Ax', 'Ay', 'Az', 'Current (mA)']].to_html(index=False, classes="custom-table")
st.markdown(html_table, unsafe_allow_html=True)

time.sleep(2)
st.rerun()