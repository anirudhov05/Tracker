import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Habitify Pro",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- PROFESSIONAL DARK MODE STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Dark animated gradient background */
    .stApp {
        background: linear-gradient(-45deg, #0f172a, #1e1b4b, #1e293b, #0f172a);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        color: #e2e8f0;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Floating particles */
    .stApp::before {
        content: '';
        position: fixed;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        background-image: 
            radial-gradient(circle at 20% 80%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(168, 85, 247, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(147, 51, 234, 0.1) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }
    
    /* Header styling */
    h1 {
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        background: linear-gradient(135deg, #a78bfa 0%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem !important;
        letter-spacing: -0.02em;
    }
    
    h2 {
        font-weight: 600 !important;
        font-size: 1.5rem !important;
        color: #f1f5f9 !important;
        margin-top: 2rem !important;
        letter-spacing: -0.01em;
    }
    
    h3 {
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        color: #cbd5e1 !important;
        letter-spacing: -0.01em;
    }
    
    /* Text colors */
    p, label, span, div {
        color: #e2e8f0 !important;
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #f1f5f9 !important;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        color: #94a3b8 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    div[data-testid="stMetricDelta"] {
        color: #a78bfa !important;
    }
    
    /* Custom checkbox styling */
    .stCheckbox {
        background: rgba(30, 41, 59, 0.6) !important;
        backdrop-filter: blur(10px);
        padding: 1rem 1.25rem !important;
        border-radius: 12px !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        margin-bottom: 0.75rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3) !important;
    }
    
    .stCheckbox:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(139, 92, 246, 0.3) !important;
        border-color: rgba(167, 139, 250, 0.4) !important;
        background: rgba(30, 41, 59, 0.8) !important;
    }
    
    .stCheckbox label {
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        color: #e2e8f0 !important;
        cursor: pointer !important;
    }
    
    .stCheckbox label span {
        color: #e2e8f0 !important;
    }
    
    /* Date input styling */
    .stDateInput {
        background: rgba(30, 41, 59, 0.6) !important;
        backdrop-filter: blur(10px);
        padding: 0.75rem !important;
        border-radius: 12px !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
    }
    
    .stDateInput input {
        background: transparent !important;
        color: #e2e8f0 !important;
        border: none !important;
    }
    
    /* Plotly chart styling */
    .js-plotly-plot {
        border-radius: 16px !important;
        background: rgba(30, 41, 59, 0.4) !important;
        backdrop-filter: blur(10px) !important;
        padding: 1rem !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background: rgba(30, 41, 59, 0.4) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        padding: 0.5rem !important;
    }
    
    .stDataFrame table {
        color: #e2e8f0 !important;
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Divider styling */
    hr {
        margin: 2rem 0 !important;
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(148, 163, 184, 0.3), transparent) !important;
    }
    
    /* Info box */
    .stAlert {
        background: rgba(30, 41, 59, 0.6) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        color: #e2e8f0 !important;
    }
    
    /* Fade in animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .element-container {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Input fields */
    input {
        background: rgba(30, 41, 59, 0.6) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 8px !important;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(139, 92, 246, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# Define habits
HABITS = [
    "Wake up at 6AM ⏰",
    "No Snoozing 🚫",
    "Drink 3L Water 💧",
    "Gym Workout 🏋️",
    "Stretching 🧘",
    "Read 10 Pages 📚",
    "Study 1 Hour 🎓",
    "Skincare Routine ✨",
    "Limit Social Media 📵",
    "No Alcohol 🚫🍺",
    "Track Expenses 💵"
]

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            date TEXT,
            habit TEXT,
            status INTEGER,
            PRIMARY KEY (date, habit)
        )
    ''')
    conn.commit()
    conn.close()

def update_habit(date_str, habit, status):
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO progress VALUES (?, ?, ?)', (date_str, habit, 1 if status else 0))
    conn.commit()
    conn.close()

def get_data():
    conn = sqlite3.connect('habits.db')
    df = pd.read_sql_query("SELECT * FROM progress", conn)
    conn.close()
    return df

init_db()

# --- UI LAYOUT ---
st.markdown("<h1>✨ Habitify Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #94a3b8; font-size: 1rem; margin-top: -0.5rem;'>Build better habits, one day at a time</p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Date selection
col_date, col_spacer = st.columns([1, 3])
with col_date:
    date_selected = st.date_input("📅 Select Date", datetime.now(), label_visibility="collapsed")
    date_str = date_selected.strftime("%Y-%m-%d")

st.markdown("<h2>Today's Habits</h2>", unsafe_allow_html=True)

# Fetch data
df = get_data()
current_day_data = df[df['date'] == date_str]

# Habit checkboxes
cols = st.columns(2)
for i, habit in enumerate(HABITS):
    is_done = False
    if not current_day_data.empty:
        status = current_day_data[current_day_data['habit'] == habit]['status'].values
        if len(status) > 0 and status[0] == 1:
            is_done = True
    
    col_idx = i % 2
    checked = cols[col_idx].checkbox(habit, value=is_done, key=f"{date_str}_{habit}")
    
    if checked != is_done:
        update_habit(date_str, habit, checked)
        st.rerun()

st.divider()

# --- ANALYTICS ---
st.markdown("<h2>📊 Your Progress</h2>", unsafe_allow_html=True)

if not df.empty:
    df['date'] = pd.to_datetime(df['date'])
    df_sorted = df.sort_values('date')
    
    # Metrics row
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    total_habits = len(HABITS)
    today_completed = df[(df['date'] == date_str) & (df['status'] == 1)].shape[0]
    today_percentage = int((today_completed / total_habits) * 100)
    
    total_days = df['date'].nunique()
    total_completions = df['status'].sum()
    overall_percentage = int((total_completions / (total_days * total_habits)) * 100) if total_days > 0 else 0
    
    current_streak = 0
    dates = sorted(df['date'].unique(), reverse=True)
    for date in dates:
        day_data = df[df['date'] == date]
        if day_data['status'].sum() == total_habits:
            current_streak += 1
        else:
            break
    
    with metric_col1:
        st.metric("Today's Progress", f"{today_percentage}%", f"{today_completed}/{total_habits}")
    with metric_col2:
        st.metric("Overall Success", f"{overall_percentage}%")
    with metric_col3:
        st.metric("Current Streak", f"{current_streak} days")
    with metric_col4:
        st.metric("Days Tracked", total_days)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts
    daily_completion = df_sorted.groupby('date')['status'].sum().reset_index()
    daily_completion['percentage'] = (daily_completion['status'] / total_habits) * 100
    
    # Trend chart
    st.markdown("<h3>Consistency Trend</h3>", unsafe_allow_html=True)
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=daily_completion['date'],
        y=daily_completion['percentage'],
        mode='lines+markers',
        fill='tozeroy',
        line=dict(color='#a78bfa', width=3),
        marker=dict(size=8, color='#c084fc'),
        fillcolor='rgba(167, 139, 250, 0.2)',
        hovertemplate='<b>%{x|%b %d}</b><br>Completion: %{y:.0f}%<extra></extra>'
    ))
    fig_line.update_layout(
        plot_bgcolor='rgba(15, 23, 42, 0.4)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, title='', color='#94a3b8'),
        yaxis=dict(showgrid=True, gridcolor='rgba(148, 163, 184, 0.1)', title='', range=[0, 105], color='#94a3b8'),
        margin=dict(l=20, r=20, t=20, b=20),
        height=300,
        font=dict(color='#e2e8f0')
    )
    st.plotly_chart(fig_line, use_container_width=True)
    
    col_chart1, col_chart2 = st.columns(2)
    
    # Habit performance
    with col_chart1:
        st.markdown("<h3>Habit Performance</h3>", unsafe_allow_html=True)
        habit_counts = df[df['status'] == 1]['habit'].value_counts().reset_index()
        habit_counts.columns = ['Habit', 'Count']
        
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            y=habit_counts['Habit'],
            x=habit_counts['Count'],
            orientation='h',
            marker=dict(
                color=habit_counts['Count'],
                colorscale=[[0, '#4c1d95'], [1, '#a78bfa']],
                showscale=False
            ),
            hovertemplate='<b>%{y}</b><br>Completed: %{x} times<extra></extra>'
        ))
        fig_bar.update_layout(
            plot_bgcolor='rgba(15, 23, 42, 0.4)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, title='', color='#94a3b8'),
            yaxis=dict(showgrid=False, title='', color='#e2e8f0'),
            margin=dict(l=20, r=20, t=20, b=20),
            height=400,
            font=dict(color='#e2e8f0')
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Success distribution
    with col_chart2:
        st.markdown("<h3>Success Distribution</h3>", unsafe_allow_html=True)
        total_attempts = len(df)
        total_success = df['status'].sum()
        
        fig_donut = go.Figure()
        fig_donut.add_trace(go.Pie(
            labels=['Completed', 'Missed'],
            values=[total_success, total_attempts - total_success],
            hole=0.6,
            marker=dict(colors=['#a78bfa', '#334155']),
            textinfo='percent',
            textfont=dict(color='#e2e8f0'),
            hovertemplate='<b>%{label}</b><br>%{value} habits<br>%{percent}<extra></extra>'
        ))
        fig_donut.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.1,
                xanchor="center",
                x=0.5,
                font=dict(color='#e2e8f0')
            ),
            margin=dict(l=20, r=20, t=20, b=20),
            height=400,
            font=dict(color='#e2e8f0')
        )
        st.plotly_chart(fig_donut, use_container_width=True)
    
    # Weekly overview
    st.markdown("<h3>Weekly Overview</h3>", unsafe_allow_html=True)
    last_7_days = datetime.now() - timedelta(days=7)
    recent_df = df[df['date'] >= last_7_days]
    
    if not recent_df.empty:
        grid_df = recent_df.pivot(index='habit', columns='date', values='status')
        grid_df = grid_df.fillna(0)
        
        def style_grid(val):
            if val == 1:
                return 'background-color: #4c1d95; color: #e9d5ff; font-weight: 600;'
            else:
                return 'background-color: #1e293b; color: #64748b;'
        
        styled_df = grid_df.style.applymap(style_grid)
        st.dataframe(styled_df, use_container_width=True)

else:
    st.info("✨ Start tracking your habits to see beautiful analytics!")

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.875rem;'>Made with ❤️ by Habitify Pro</p>", unsafe_allow_html=True)
