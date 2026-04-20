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

img_base64 = get_base64_image(r"image.png")

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
page = st.sidebar.radio("Navigation", ["Home", "Live Matches", "Analytics", "Manage Players"])

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

    st.markdown("""
    ### 📊 Project Overview  
    This dashboard provides real-time cricket analytics using API data and SQL-based insights.  
    It includes live match tracking, performance analysis, and player management features.
    
    ### 🚀 Key Features  
    - Live Match Data (Auto-refresh)  
    - Interactive Charts & KPIs  
    - SQL-Based Analytics  
    - CRUD Operations for Player Data  
    """)

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
    fig3 = px.bar(team_counts, title="🏏 Team Participation Analysis (Matches Played)")
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

# -------------------------------
# PREMIUM CRUD PAGE
# -------------------------------
elif page == "Manage Players":
    st.title("🛠️ Player Management System")

    conn = sqlite3.connect("cricket.db", check_same_thread=False)
    cursor = conn.cursor()

    # Create Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        team TEXT,
        runs INTEGER,
        wickets INTEGER
    )
    """)
    conn.commit()
# ---------------- DEFAULT DATA INSERT ----------------
    cursor.execute("SELECT COUNT(*) FROM players")
    count = cursor.fetchone()[0]
    
    if count == 0:
        sample_players = [
            ("Virat Kohli", "India", 12000, 5),
            ("Rohit Sharma", "India", 10000, 8),
            ("Joe Root", "England", 9500, 12),
            ("Steve Smith", "Australia", 9000, 15)
        ]
    
        cursor.executemany(
            "INSERT INTO players (name, team, runs, wickets) VALUES (?, ?, ?, ?)",
            sample_players
        )
        conn.commit()
    
    # ---------------- CREATE ----------------
    st.subheader("➕ Add New Player")

    col1, col2 = st.columns(2)
    name = col1.text_input("Player Name")
    team = col2.text_input("Team")

    col3, col4 = st.columns(2)
    runs = col3.number_input("Runs", min_value=0)
    wickets = col4.number_input("Wickets", min_value=0)

    if st.button("Add Player"):
        if name and team:
            cursor.execute(
                "INSERT INTO players (name, team, runs, wickets) VALUES (?, ?, ?, ?)",
                (name, team, runs, wickets)
            )
            conn.commit()
            st.success("✅ Player added successfully!")
        else:
            st.error("⚠️ Please fill all fields")

    # ---------------- READ ----------------
    st.subheader("📋 Player Records")
    df_players = pd.read_sql("SELECT * FROM players", conn)
    st.dataframe(df_players, use_container_width=True)

    # ---------------- DOWNLOAD PLAYER DATA ----------------
    if not df_players.empty:
        csv_players = df_players.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Player Data", csv_players, "players.csv", "text/csv")

   # ---------------- SEARCH & FILTER ----------------
    st.subheader("🔍 Search & Filter Players")

    search = st.text_input("Search Player by Name")

    teams_list = df_players["team"].dropna().unique() if not df_players.empty else []
    selected_team_filter = st.selectbox("Filter by Team", ["All"] + list(teams_list))

    filtered_players = df_players.copy()

    if search:
        filtered_players = filtered_players[filtered_players["name"].str.contains(search, case=False)]

    if selected_team_filter != "All":
        filtered_players = filtered_players[filtered_players["team"] == selected_team_filter]

    st.dataframe(filtered_players, use_container_width=True)

    # ---------------- MINI ANALYTICS ----------------

    # ---------------- KPI CARDS ----------------
    st.subheader("📌 Key Player Stats")

    if not df_players.empty:

        total_players = len(df_players)
        total_runs = df_players["runs"].sum()
        total_wickets = df_players["wickets"].sum()
        avg_runs = int(df_players["runs"].mean())

        c1, c2, c3, c4 = st.columns(4)

        c1.markdown(f"<div class='metric-card'><h4>Total Players</h4><h2>{total_players}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card'><h4>Total Runs</h4><h2>{total_runs}</h2></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-card'><h4>Total Wickets</h4><h2>{total_wickets}</h2></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='metric-card'><h4>Avg Runs</h4><h2>{avg_runs}</h2></div>", unsafe_allow_html=True)

    else:
        st.info("No data for KPIs")
        
        st.subheader("📊 Player Performance Insights")

        if not df_players.empty:

            col1, col2 = st.columns(2)

            fig_runs = px.bar(df_players, x="name", y="runs", title="Runs by Players")
            col1.plotly_chart(fig_runs, use_container_width=True)

            fig_wickets = px.bar(df_players, x="name", y="wickets", title="Wickets by Players")
            col2.plotly_chart(fig_wickets, use_container_width=True)

            top_player = df_players.sort_values(by="runs", ascending=False).iloc[0]

            st.markdown(f"""
            <div class='metric-card'>
                <h3>🏆 Top Performer</h3>
                <h2>{top_player['name']}</h2>
                <p>Runs: {top_player['runs']} | Wickets: {top_player['wickets']}</p>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.info("No data available for analytics.")

    # ---------------- BEST BATSMAN ----------------
    if not df_players.empty:
        best_batsman = df_players.loc[df_players['runs'].idxmax()]
        st.success(f"🏏 Best Batsman: {best_batsman['name']} with {best_batsman['runs']} runs")
            
    # ---------------- PLAYER RANKING ----------------
    st.subheader("🥇 Player Rankings")

    if not df_players.empty:

        df_rank = df_players.copy()

        # Simple scoring formula
        df_rank["score"] = df_rank["runs"] * 0.7 + df_rank["wickets"] * 10

        df_rank = df_rank.sort_values(by="score", ascending=False)

        st.dataframe(df_rank[["name", "team", "runs", "wickets", "score"]], use_container_width=True)

        # Top 3 Highlight
        st.markdown("### 🌟 Top 3 Players")

        top3 = df_rank.head(3)

        for i, row in top3.iterrows():
            st.markdown(f"""
            <div class='metric-card'>
                <h3>#{top3.index.get_loc(i)+1} - {row['name']}</h3>
                <p>Team: {row['team']}</p>
                <p>Runs: {row['runs']} | Wickets: {row['wickets']}</p>
                <p>Score: {int(row['score'])}</p>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.info("No data for ranking")

    # ---------------- UPDATE ----------------
    st.subheader("✏️ Update Player")

    if not df_players.empty:
        player_options = df_players["name"] + " (ID: " + df_players["id"].astype(str) + ")"
        selected_player = st.selectbox("Select Player", player_options)

        selected_id = int(selected_player.split("ID: ")[1].replace(")", ""))

        player_data = df_players[df_players["id"] == selected_id].iloc[0]

        col5, col6 = st.columns(2)
        new_runs = col5.number_input("Update Runs", value=int(player_data["runs"]))
        new_wickets = col6.number_input("Update Wickets", value=int(player_data["wickets"]))

        if st.button("Update Player"):
            cursor.execute(
                "UPDATE players SET runs=?, wickets=? WHERE id=?",
                (new_runs, new_wickets, selected_id)
            )
            conn.commit()
            st.success("✅ Player updated successfully!")

    else:
        st.info("No players available to update.")

    # ---------------- DELETE ----------------
    st.subheader("🗑️ Delete Player")

    if not df_players.empty:
        delete_player = st.selectbox("Select Player to Delete", player_options, key="delete")

        delete_id = int(delete_player.split("ID: ")[1].replace(")", ""))

        if st.button("Delete Player"):
            cursor.execute("DELETE FROM players WHERE id=?", (delete_id,))
            conn.commit()
            st.warning("⚠️ Player deleted successfully!")
    else:
        st.info("No players available to delete.")
