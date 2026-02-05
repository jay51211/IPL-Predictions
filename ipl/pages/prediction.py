import pandas as pd
import streamlit as st
import pickle

st.set_page_config(
    page_title="IPL Performance Predictor",
    layout="wide",
    page_icon="🏏"
)

@st.cache_data
def load_data():
    with open("model.pkl", "rb") as f:
        batsman_model = pickle.load(f)
    with open("match_pred.pkl", "rb") as f:
        match_model = pickle.load(f)
    with open("bowler_model.pkl", "rb") as f:
        bowler_model = pickle.load(f)
    batsman_df = pd.read_csv("batsman_match_stats.csv")
    bowler_df = pd.read_csv("bowler_latest_stats.csv")

    return batsman_model, match_model, bowler_model, batsman_df, bowler_df

batsman_model, match_model, bowler_model, batsman_df, bowler_df = load_data()

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
st.divider()

def predict_match_winner(model, team1, team2, venue, toss_winner, toss_decision):
    X = pd.DataFrame([{
        "team1": team1,
        "team2": team2,
        "venue": venue,
        "toss_winner": toss_winner,
        "toss_decision": toss_decision
    }])
    return model.predict(X)[0]

def predict_batsman(model, avg5, avg10, bowling_team, venue):
    X = pd.DataFrame([{
        "avg_last_5": avg5,
        "avg_last_10": avg10,
        "bowling_team": bowling_team,
        "venue": venue
    }])
    return model.predict(X)[0]

def predict_bowler(model, avg5, avg10, batting_team, venue):
    X = pd.DataFrame([{
        "avg_last_5": avg5,
        "avg_last_10": avg10,
        "batting_team": batting_team,
        "venue": venue
    }])
    return model.predict(X)[0]

teams = ['Kolkata Knight Riders', 'Royal Challengers Bengaluru','Chennai Super Kings', 'Kings XI Punjab', 'Rajasthan Royals','Delhi Capitals', 'Mumbai Indians', 'Deccan Chargers','Kochi Tuskers Kerala', 'Pune Warriors', 'Sunrisers Hyderabad','Rising Pune Supergiants', 'Gujarat Lions', 'Lucknow Super Giants','Gujarat Titans']

venues = ['M Chinnaswamy Stadium','Punjab Cricket Association Stadium, Mohali', 'Feroz Shah Kotla','Wankhede Stadium', 'Eden Gardens', 'Sawai Mansingh Stadium','Rajiv Gandhi International Stadium, Uppal','MA Chidambaram Stadium, Chepauk', 'Dr DY Patil Sports Academy','Newlands', "St George's Park", 'Kingsmead', 'SuperSport Park','Buffalo Park', 'New Wanderers Stadium', 'De Beers Diamond Oval','OUTsurance Oval', 'Brabourne Stadium','Sardar Patel Stadium, Motera', 'Barabati Stadium','Brabourne Stadium, Mumbai','Vidarbha Cricket Association Stadium, Jamtha','Himachal Pradesh Cricket Association Stadium', 'Nehru Stadium','Holkar Cricket Stadium','Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium','Subrata Roy Sahara Stadium','Maharashtra Cricket Association Stadium','Shaheed Veer Narayan Singh International Stadium','JSCA International Stadium Complex', 'Sheikh Zayed Stadium','Sharjah Cricket Stadium', 'Dubai International Cricket Stadium','Punjab Cricket Association IS Bindra Stadium, Mohali','Saurashtra Cricket Association Stadium', 'Green Park','M.Chinnaswamy Stadium','Punjab Cricket Association IS Bindra Stadium','Rajiv Gandhi International Stadium', 'MA Chidambaram Stadium','Arun Jaitley Stadium', 'MA Chidambaram Stadium, Chepauk, Chennai','Wankhede Stadium, Mumbai', 'Narendra Modi Stadium, Ahmedabad','Arun Jaitley Stadium, Delhi', 'Zayed Cricket Stadium, Abu Dhabi','Dr DY Patil Sports Academy, Mumbai','Maharashtra Cricket Association Stadium, Pune','Eden Gardens, Kolkata','Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh','Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow','Rajiv Gandhi International Stadium, Uppal, Hyderabad','M Chinnaswamy Stadium, Bengaluru', 'Barsapara Cricket Stadium, Guwahati', 'Sawai Mansingh Stadium, Jaipur', 'Himachal Pradesh Cricket Association Stadium, Dharamsala','Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur','Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam']

c1, c2, c3 = st.columns(3)
with c1:
    st.subheader("🏆 Predict Match Winner")

    team1 = st.selectbox("Select Team 1", sorted(teams))
    team2 = st.selectbox("Select Team 2", sorted([t for t in teams if t != team1]))
    venue = st.selectbox("Select Venue", sorted(venues))
    toss_winner = st.selectbox("Select Toss Winner", [team1, team2])
    toss_decision = st.radio("Select Toss Decision", ["Bat", "Field"]).lower()

    submit = st.button("Predict Winner")
    if submit:
        winner = predict_match_winner(match_model, team1, team2, venue, toss_winner, toss_decision)

        st.success(f"🏆 Predicted Winner: {winner}")

with c2:
    st.subheader("🏏 Predict Batsman Runs")

    batter = st.selectbox("Select Batsman", batsman_df["batter"].unique())
    row = batsman_df[batsman_df["batter"] == batter].iloc[0]
    avg5 = row["avg_last_5"]
    avg10 = row["avg_last_10"]

    st.markdown("**Recent Performance (Auto-calculated):**")
    st.write(f"• Avg runs (last 5 matches): **{avg5:.2f}**")
    st.write(f"• Avg runs (last 10 matches): **{avg10:.2f}**")

    bowling_team = st.selectbox("Select Bowling Team", sorted(teams))
    venue = st.selectbox("Select Venue", sorted(venues), key="bat_venue")
    submit = st.button("Predict Batsman Runs")

    if submit:
        runs = predict_batsman(batsman_model, avg5, avg10, bowling_team, venue)
        st.success(f"🏏 Predicted Batsman Runs: **{runs:.1f}**")

with c3:
    st.subheader("🎯 Predict Bowler Wickets")

    bowler = st.selectbox("Select Bowler", bowler_df["bowler"].unique())
    row = bowler_df[bowler_df["bowler"] == bowler].iloc[0]
    avg5 = row["avg_last_5"]
    avg10 = row["avg_last_10"]

    st.markdown("**Recent Performance (Auto-calculated):**")
    st.write(f"• Avg wickets (last 5 matches): **{avg5:.2f}**")
    st.write(f"• Avg wickets (last 10 matches): **{avg10:.2f}**")

    batting_team = st.selectbox("Select Batting Team", sorted(teams))
    venue = st.selectbox("Select Venue", sorted(venues), key="bowl_venue")
    submit = st.button("Predict Bowler Wickets")

    if submit:
        wickets = predict_bowler(bowler_model, avg5, avg10, batting_team, venue)
        pred_wickets = int(round(wickets))
        st.success(f"🎯 Predicted Wickets: **{pred_wickets}**")