import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px

# --- CONFIGURATION ---
st.set_page_config(page_title="Habit Tracker", page_icon="✅", layout="wide")

# Define your habits here (matching the screenshot)
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

# Initialize DB on load
init_db()

# --- UI LAYOUT ---
st.title("📊 Personal Habit Tracker")

# 1. INPUT SECTION (Mobile Friendly)
st.header("Today's Targets")
col1, col2 = st.columns([2, 1])

date_selected = st.date_input("Select Date", datetime.now())
date_str = date_selected.strftime("%Y-%m-%d")

# Fetch existing data for this date to pre-fill checkboxes
df = get_data()
current_day_data = df[df['date'] == date_str]

# Create Checkboxes
with st.container():
    # CSS to make checkboxes bigger on mobile
    st.markdown("""
        <style>
        div[row-widget="stCheckbox"] label { font-size: 18px; padding-bottom: 10px; }
        </style>
        """, unsafe_allow_html=True)
    
    cols = st.columns(2) # split into 2 columns for compact view
    for i, habit in enumerate(HABITS):
        # Check if habit was previously completed
        is_done = False
        if not current_day_data.empty:
            status = current_day_data[current_day_data['habit'] == habit]['status'].values
            if len(status) > 0 and status[0] == 1:
                is_done = True
        
        # Toggle functionality
        col_idx = i % 2
        checked = cols[col_idx].checkbox(habit, value=is_done, key=f"{date_str}_{habit}")
        
        # Update DB immediately on change
        if checked != is_done:
            update_habit(date_str, habit, checked)
            st.rerun()

st.divider()

# 2. DASHBOARD SECTION (Matching Screenshot Visuals)
st.header("Analytics Dashboard")

if not df.empty:
    # Prepare Data
    df['date'] = pd.to_datetime(df['date'])
    df_sorted = df.sort_values('date')
    
    # Calculate Completion %
    daily_completion = df_sorted.groupby('date')['status'].sum().reset_index()
    total_habits = len(HABITS)
    daily_completion['percentage'] = (daily_completion['status'] / total_habits) * 100

    # A. Line Chart (Like the top left chart in your image)
    st.subheader("Consistency Trend")
    fig_line = px.area(daily_completion, x='date', y='percentage', 
                       title="Daily Completion Rate (%)",
                       labels={'percentage': 'Completion %'},
                       markers=True)
    fig_line.update_traces(line_color='#636EFA', fill='tozeroy')
    fig_line.update_yaxes(range=[0, 110])
    st.plotly_chart(fig_line, use_container_width=True)

    col_d1, col_d2 = st.columns(2)

    # B. Pie Chart (Overall Progress)
    with col_d1:
        st.subheader("Overall Success")
        total_attempts = len(df) # total records (0 or 1)
        total_success = df['status'].sum()
        # Note: This is simplified. Real math depends on how many days tracked.
        
        fig_pie = px.pie(names=['Completed', 'Missed'], 
                         values=[total_success, (total_attempts - total_success)],
                         hole=0.4,
                         color_discrete_sequence=['#00CC96', '#EF553B'])
        fig_pie.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)

    # C. Top Habits List (Matching bottom right image)
    with col_d2:
        st.subheader("Top Habits")
        habit_counts = df[df['status'] == 1]['habit'].value_counts().reset_index()
        habit_counts.columns = ['Habit', 'Streak']
        st.dataframe(habit_counts, hide_index=True, use_container_width=True)

    # D. The Weekly Grid (Heatmap style)
    st.subheader("Weekly Overview")
    # Pivot table to look like the spreadsheet grid
    last_7_days = datetime.now() - timedelta(days=7)
    recent_df = df[df['date'] >= last_7_days]
    
    if not recent_df.empty:
        grid_df = recent_df.pivot(index='habit', columns='date', values='status')
        grid_df = grid_df.fillna(0)
        # Replace 1/0 with visual indicators
        st.dataframe(grid_df.style.map(lambda v: 'background-color: #90EE90' if v == 1 else ''), use_container_width=True)

else:
    st.info("Start checking off habits to see your analytics!")