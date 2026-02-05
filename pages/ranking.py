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

st.subheader("🏆 IPL Team Rankings")

@st.cache_data
def load_data():
    match_df = pd.read_csv("matches.csv")
    deliveries_df = pd.read_csv("deliveries.csv")
    return match_df, deliveries_df

match_df, deliveries_df = load_data()
df = pd.merge(
    deliveries_df,
    match_df,
    left_on="match_id",
    right_on="id",
    how="inner"
)
team_name_map = {
    'Delhi Daredevils': 'Delhi Capitals',
    'Punjab Kings': 'Kings XI Punjab',
    'Rising Pune Supergiant': 'Rising Pune Supergiants',
    'Royal Challengers Bangalore': 'Royal Challengers Bengaluru'
}

for col in ["batting_team", "bowling_team", "team1", "team2", "toss_winner", "winner"]:
    df[col] = df[col].replace(team_name_map)

# Merge deliveries with matches to get season/date
player_team_df = deliveries_df.merge(match_df[["id", "season"]], left_on="match_id", right_on="id", how="left")

# Get latest team for each batter
latest_team = player_team_df.sort_values("season").groupby("batter").tail(1)[["batter", "batting_team"]].rename(columns={"batting_team": "current_team"})

# Get latest team for each bowler
bowler_latest_team = player_team_df.sort_values("season").groupby("bowler").tail(1)[["bowler", "bowling_team"]].rename(columns={"batting_team": "current_team"})

def n_bar():
    p1, p2, p3 = st.tabs(["🏆 Team Rankings", "🏏 Batsmen Rankings", "🎯 Bowler Rankings"])
    with p1:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("🥇 Team Ranking by Wins")
            team_rank_wins = match_df["winner"].value_counts().sort_values(ascending=False).reset_index().rename(columns={"winner": "Team", "count": "Matches"})
            team_rank_wins.index = team_rank_wins.index + 1
            team_rank_wins.index.name = "Rank"
            st.dataframe(team_rank_wins)

        with c2:
            st.subheader("🏏Team Ranking by Runs")
            team_rank_runs = df.groupby("batting_team")["total_runs"].sum().sort_values(ascending=False).reset_index().rename(columns={"batting_team": "Team", "total_runs": "Total Runs"})
            team_rank_runs.index = team_rank_runs.index + 1
            team_rank_runs.index.name = "Rank"
            st.dataframe(team_rank_runs)

        with c3:
            st.subheader("🏆 Team Ranking by Sixes")
            team_rank_sixes = df[df["batsman_runs"] == 6].groupby("batting_team").size().sort_values(ascending=False).reset_index().rename(columns={"batting_team": "Team", 0: "Total No. of Sixes"})
            team_rank_sixes.index = team_rank_sixes.index + 1
            team_rank_sixes.index.name = "Rank"
            st.dataframe(team_rank_sixes)

    with p2:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🏏 Batsmen Ranking by Runs")
            batsmen_runs = df.groupby("batter")["batsman_runs"].sum().sort_values(ascending=False).reset_index()
            batsmen_rank_runs = batsmen_runs.merge(latest_team, on="batter", how="left")
            batsmen_rank_runs = batsmen_rank_runs.rename(columns={"batter": "Name", "current_team": "Team", "batsman_runs": "Total Runs"})
            batsmen_rank_runs.index = batsmen_rank_runs.index + 1
            batsmen_rank_runs.index.name = "Rank"
            st.dataframe(batsmen_rank_runs)

        with c2:
            st.subheader("🏏️️ Batsman Ranking by Number of Sixes")
            batsmen_six = df[df["batsman_runs"] == 6].groupby("batter").size().sort_values(ascending=False).reset_index()
            batsmen_rank_six = batsmen_six.merge(latest_team, on="batter", how="left")
            batsmen_rank_six = batsmen_rank_six.rename(columns={"batter": "Name", "current_team": "Team", 0: "Total No. of Sixes"})
            batsmen_rank_six.index = batsmen_rank_six.index + 1
            batsmen_rank_six.index.name = "Rank"
            st.dataframe(batsmen_rank_six)

        st.markdown("---")

        lc1, lc2 = st.columns(2)
        with lc1:
            st.subheader("🏏 Batsmen Ranking by Number of Fours")
            batsmen_four = df[df["batsman_runs"] == 4].groupby("batter").size().sort_values(ascending=False).reset_index()
            batsmen_rank_four = batsmen_four.merge(latest_team, on="batter", how="left")
            batsmen_rank_four = batsmen_rank_four.rename(columns={"batter": "Name", "current_team": "Team", 0: "Total No. of Fours"})
            batsmen_rank_four.index = batsmen_rank_four.index + 1
            batsmen_rank_four.index.name = "Rank"
            st.dataframe(batsmen_rank_four)

        with lc2:
            st.subheader("🔴 Ranking by Catches")
            catcher = df["fielder"].value_counts().sort_values(ascending=False).reset_index()
            catcher_rank = catcher.merge(latest_team, left_on="fielder", right_on="batter", how="left")
            catcher_rank = catcher_rank.rename(columns={"current_team": "Team", "fielder": "Name", "count": "No. of Catches"})
            catcher_rank = catcher_rank.drop("batter", axis=1)
            catcher_rank.index = catcher_rank.index + 1
            catcher_rank.index.name = "Rank"
            st.dataframe(catcher_rank)

    with p3:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("⚪️ Bowler Ranking by Wickets")
            st.caption("")
            st.markdown("")
            bowler = df.groupby("bowler")["is_wicket"].sum().sort_values(ascending=False).reset_index()
            bowler_rank = bowler.merge(bowler_latest_team, on="bowler", how="left")
            bowler_rank = bowler_rank.rename(columns={"bowler": "Name", "is_wicket": "Wickets", "bowling_team": "Team"})
            bowler_rank.index = bowler_rank.index + 1
            bowler_rank.index.name = "Rank"
            st.dataframe(bowler_rank)

        with c2:
            st.subheader("🎯 Bowler Ranking by Least Runs Conceded")
            st.caption("Minimum 480 Balls Delivered")
            valid_bowler = df.groupby("bowler")["ball"].size().reset_index().query("ball >= 480")
            bowler_run = df.groupby("bowler")["total_runs"].sum().sort_values().reset_index()
            bowler_run = bowler_run.merge(valid_bowler[["bowler"]], on="bowler")
            bowler_run_rank = bowler_run.merge(bowler_latest_team, on="bowler", how="left")
            bowler_run_rank = bowler_run_rank.rename(columns={"bowler": "Name", "bowling_team": "Team"})
            bowler_run_rank.index = bowler_run_rank.index + 1
            bowler_run_rank.index.name = "Rank"
            st.dataframe(bowler_run_rank)

    st.divider()

n_bar()

