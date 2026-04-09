import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import base64

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="🏏 Cricbuzz Premium Dashboard", layout="wide")

# -------------------------------
# LOAD LOCAL IMAGE (BASE64)
# -------------------------------
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

img_base64 = get_base64_image(r"D:\Internship\labmentix\cricbuzz\Coding\Cricbuzz_project\image.png")

# -------------------------------
# PREMIUM BACKGROUND + UI
# -------------------------------
st.markdown(f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("data:image/png;base64,{img_base64}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

/* DARK OVERLAY */
[data-testid="stAppViewContainer"]::before {{
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(10, 20, 30, 0.75);
    z-index: 0;
}}

/* CONTENT ABOVE OVERLAY */
.block-container {{
    position: relative;
    z-index: 1;
}}

/* KPI CARDS */
.metric-card {{
    background: rgba(255,255,255,0.1);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    backdrop-filter: blur(10px);
    box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
}}

/* TEXT COLORS */
h1, h2, h3, h4, h5, h6 {{
    color: #ffffff !important;
}}

p, div, label {{
    color: #e0e0e0 !important;
}}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# SIDEBAR
# -------------------------------
st.sidebar.title("🏏 Cricbuzz Premium")
page = st.sidebar.radio("Navigation", ["Home", "Live Matches", "Analytics"])

# -------------------------------
# AUTO REFRESH
# -------------------------------
st_autorefresh(interval=30000, limit=None, key="refresh")

# -------------------------------
# DATABASE
# -------------------------------
conn = sqlite3.connect("cricket.db")

query = """
SELECT 
    m.match_id,
    t1.team_name AS team1,
    t2.team_name AS team2,
    v.venue_name,
    m.status
FROM matches m
JOIN teams t1 ON m.team1_id = t1.team_id
JOIN teams t2 ON m.team2_id = t2.team_id
JOIN venues v ON m.venue_id = v.venue_id
"""

df = pd.read_sql(query, conn)

# -------------------------------
# COMMON DATA
# -------------------------------
team_counts = pd.concat([df['team1'], df['team2']]).value_counts()
venue_counts = df['venue_name'].value_counts()
status_counts = df['status'].value_counts()

# -------------------------------
# HOME PAGE
# -------------------------------
if page == "Home":
    st.title("🏏 Cricbuzz Premium Dashboard")

    total_matches = df['match_id'].nunique()
    total_teams = len(set(df['team1']).union(set(df['team2'])))
    total_venues = df['venue_name'].nunique()

    top_team = team_counts.idxmax()
    top_venue = venue_counts.idxmax()

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.markdown(f"<div class='metric-card'><h3>Matches</h3><h1>{total_matches}</h1></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='metric-card'><h3>Teams</h3><h1>{total_teams}</h1></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='metric-card'><h3>Venues</h3><h1>{total_venues}</h1></div>", unsafe_allow_html=True)
    col4.markdown(f"<div class='metric-card'><h3>Top Team</h3><h1>{top_team}</h1></div>", unsafe_allow_html=True)
    col5.markdown(f"<div class='metric-card'><h3>Top Venue</h3><h1>{top_venue}</h1></div>", unsafe_allow_html=True)

    st.write("⏱ Last Updated:", pd.Timestamp.now())

# -------------------------------
# LIVE MATCHES PAGE
# -------------------------------
elif page == "Live Matches":
    st.title("🏏 Live Matches")

    teams = sorted(set(df['team1']).union(set(df['team2'])))
    selected_team = st.selectbox("🔍 Select Team", teams)

    filtered_df = df[
        (df['team1'] == selected_team) | (df['team2'] == selected_team)
    ]

    st.subheader("📋 Filtered Matches")
    st.dataframe(filtered_df, use_container_width=True)

    # TABLE 1
    st.subheader("📊 Match Status Summary")
    status_table = status_counts.reset_index()
    status_table.columns = ["Status", "Count"]
    st.dataframe(status_table)

    # TABLE 2
    st.subheader("🏏 Team Performance")
    team_table = team_counts.reset_index()
    team_table.columns = ["Team", "Matches"]
    st.dataframe(team_table)

    # TABLE 3
    st.subheader("🏟 Venue Performance")
    venue_table = venue_counts.reset_index()
    venue_table.columns = ["Venue", "Matches"]
    st.dataframe(venue_table)

    # DOWNLOAD
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Data", csv, "matches.csv", "text/csv")

# -------------------------------
# ANALYTICS PAGE
# -------------------------------
elif page == "Analytics":
    st.title("📊 Advanced Analytics")

    col1, col2 = st.columns(2)

    # DONUT CHARTS
    fig1 = px.pie(values=status_counts.values, names=status_counts.index, hole=0.5)
    col1.plotly_chart(fig1, use_container_width=True)

    fig2 = px.pie(values=venue_counts.values, names=venue_counts.index, hole=0.5)
    col2.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # BAR CHARTS
    fig3 = px.bar(team_counts, title="Matches per Team")
    st.plotly_chart(fig3, use_container_width=True)

    fig4 = px.bar(venue_counts, title="Matches per Venue")
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")

    # TABLES
    st.subheader("📋 Team Table")
    st.dataframe(team_counts.reset_index().rename(columns={'index':'Team',0:'Matches'}))

    st.subheader("📋 Venue Table")
    st.dataframe(venue_counts.reset_index().rename(columns={'index':'Venue',0:'Matches'}))

    st.subheader("📋 Status Table")
    st.dataframe(status_counts.reset_index().rename(columns={'index':'Status',0:'Count'}))
