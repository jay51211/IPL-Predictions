import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="IPL Performance Predictor",
    layout="wide",
    page_icon="🏏"
)

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        display: none;
    }
    [data-testid="stAppViewContainer"] {
        margin-left: 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def load_df():
    batsman_df = pd.read_csv("batsman_match_stats.csv")
    bowler_df = pd.read_csv("bowler_latest_stats.csv")
    match_df = pd.read_csv("matches.csv")
    deliveries_df = pd.read_csv("deliveries.csv")
    return batsman_df, bowler_df, match_df, deliveries_df

batsman_df, bowler_df, match_df, deliveries_df = load_df()

c1, c2 = st.columns([4, 3])
with c1:
    st.title("🏏 IPL Performance Predictor")
    st.caption("End-to-end Machine Learning application for IPL analytics")
with c2:
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏠 Home"):
            st.switch_page("app.py")
    with c2:
        if st.button("🏆 Rankings"):
            st.switch_page("pages/ranking.py")
    with c3:
        if st.button("🔮 Predictions"):
            st.switch_page("pages/prediction.py")

st.subheader("🏏 IPL Analytics & Performance Prediction Platform")

st.write("""
This application provides **data-driven insights and predictions** for the Indian Premier League (IPL) 
using historical match and ball-by-ball data.
""")

st.markdown("""
### 🔍 What You Can Explore
- 🏆 **Team Rankings** based on match performance  
- 🏏 **Top Batsmen & Bowlers** across IPL seasons  
- 🔮 **Match Winner Prediction** using ML models  
- 🎯 **Batsman Runs & Bowler Wickets Prediction**  
""")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total Matches", match_df.shape[0])
with c2:
    st.metric("Total Teams", match_df["team1"].nunique())

all_player = pd.Series(pd.concat([deliveries_df["batter"], deliveries_df["bowler"]]).dropna().unique())
with c3:
    st.metric("Total Players", len(all_player))
with c4:
    st.metric("Seasons Covered", match_df["season"].nunique())

st.subheader("📊 IPL at a Glance")
i1, i2, i3 =  st.columns(3)
with i1:
    st.image("images/top_10_teams_by_wins.jpg", caption="Top 10 Teams by Wins")
with i2:
    st.image("images/top_10_batsman.jpg", caption="Top 10 Batsman")
with i3:
    st.image("images/top_10_bowlers.jpg", caption="Top 10 Bowler")

st.subheader("🤖 How Predictions Work")

st.write("""
Predictions are generated using machine learning models trained on:
- Historical IPL match results  
- Player performance trends  
- Match context such as venue and opposition  

The models learn patterns from past data to estimate future outcomes.
""")

st.caption(
    "⚠️ Predictions are based on historical data (2008 - 2024) and statistical patterns. "
    "They do not guarantee actual match results."

)





