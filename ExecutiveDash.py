import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import streamlit as st
import math
from pathlib import Path

# Set Streamlit Page Layout
st.set_page_config(page_title="Plant Turnaround Dashboard", layout="wide")

st.title("🏭 Executive Report - Plant Turnaround")
st.caption("Real-time Operational & Safety Status Dashboard | Hendri Sitompul, Student ID: 114910")

# Load Dataset
@st.cache_data
def load_data():
    file_name = Path(__file__).parent/'data/TA_Checimal_Rev1.csv'
    df = pd.read_csv(file_name)
    df['Planned_Finish'] = pd.to_datetime(df['Planned_Finish'], errors='coerce')
    df['Actual_Start'] = pd.to_datetime(df['Actual_Start'], errors='coerce')
    df['Actual_Finish'] = pd.to_datetime(df['Actual_Finish'], errors='coerce')
    return df

df = load_data()

# Calculations
overall_progress = df['Completion_%'].mean()
current_date = df['Actual_Start'].max()
max_planned = df['Planned_Finish'].max()
days_remaining = max((max_planned - current_date).days, 0)
avg_spi = df['SPI'].mean()
total_planned_cost = df['Planned_Cost'].sum()
total_actual_cost = df['Actual_Cost'].sum()
budget_utilization = (total_actual_cost / total_planned_cost) * 100
recordables = (df['Recordable_Injury'] == 'Yes').sum()
near_misses = (df['Near_Miss'] == 'Yes').sum()
mechanical_completed = df[(df['Discipline'] == 'Mechanical') & (df['Status'] == 'Completed')].shape[0]
mechanical_total = df[df['Discipline'] == 'Mechanical'].shape[0]
mech_pct = (mechanical_completed / mechanical_total * 100) if mechanical_total > 0 else 0
readiness = df['Readiness_Score'].mean()
critical_risks = df[(df['Critical_Path'] == 'Yes') & (df['CEO_Red_Flag'] == 'Yes')].shape[0]
open_decisions = df[(df['CEO_Red_Flag'] == 'Yes') & (df['Status'] != 'Completed')].shape[0]

# --- KPI Section ---
st.subheader("Key Performance Indicators")
col1, col2, col3 = st.columns(3)
col1.metric("Overall Progress", f"{overall_progress:.1f}%", delta=f"{days_remaining} Days Left")
col2.metric("Schedule Variance (SPI)", f"{avg_spi:.2f}", delta="-0.14 vs Target", delta_color="inverse")
col3.metric("Budget Utilization", f"{budget_utilization:.1f}%", delta=f"${total_actual_cost - total_planned_cost:,.0f}", delta_color="inverse")

col4, col5, col6 = st.columns(3)
col4.metric("Safety Recordables", f"{recordables}", f"{near_misses} Near Misses", delta_color="inverse")
col5.metric("Mechanical Completion", f"{mech_pct:.1f}%", f"{mechanical_completed}/{mechanical_total} WOs")
col6.metric("Startup Readiness", f"{readiness:.1f} / 100")

col7, col8 = st.columns(2)
col7.metric("Critical Path Risks", f"{critical_risks:,}")
col8.metric("Open Executive Decisions", f"{open_decisions:,}")

st.divider()

# --- Visualization Section ---
st.subheader("Executive Visual Analytics")
tab1, tab2 = st.columns(2)

with tab1:
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    plan_counts = df.dropna(subset=['Planned_Finish']).groupby(df['Planned_Finish'].dt.date).size().cumsum()
    act_counts = df[(df['Status'] == 'Completed') & df['Actual_Finish'].notnull()].groupby(df['Actual_Finish'].dt.date).size().cumsum()
    
    ax1.plot(plan_counts.index, plan_counts.values, label='Baseline Plan', color='#112240', linestyle='--')
    ax1.plot(act_counts.index, act_counts.values, label='Actual Earned', color='#3182CE', linewidth=2)
    ax1.set_title("S-Curve Completion Trend")
    ax1.legend()
    st.pyplot(fig1)

with tab2:
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.barh(['Planned Budget', 'Actual Spend'], [total_planned_cost, total_actual_cost], color=['#112240', '#C53030'])
    ax2.set_title("Budget Position Overview")
    st.pyplot(fig2)