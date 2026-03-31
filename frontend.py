import streamlit as st
import requests
import pandas as pd

BASE_URL = "http://localhost:8000"

# ---------------------- SESSION ----------------------

if "token" not in st.session_state:
    st.session_state.token = None

def get_headers():
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

# ---------------------- LOGIN ----------------------

def login():
    st.title("⚽ Football Control Center")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = requests.post(
            f"{BASE_URL}/auth/token",
            data={"username": username, "password": password}
        )

        if res.status_code == 200:
            st.session_state.token = res.json()["access_token"]
            st.success("Logged in successfully")
            st.rerun()
        else:
            st.error("Invalid credentials")

# ---------------------- DASHBOARD ----------------------

def dashboard():
    st.title("📊 Match Dashboard")

    res = requests.get(f"{BASE_URL}/matches")
    data = res.json()

    matches = data.get("matches", [])

    if matches:
        df = pd.json_normalize(matches)
        st.dataframe(df, use_container_width=True)

    st.metric("Total Matches", data.get("total", 0))

# ---------------------- CREATE MATCH ----------------------

def create_match():
    st.title("⚽ Create Match")

    season_id = st.number_input("Season ID", min_value=1)
    venue = st.text_input("Venue")
    date = st.date_input("Date")
    status = st.selectbox("Status", ["upcoming", "completed"])

    st.subheader("Participants")

    col1, col2 = st.columns(2)

    with col1:
        team1 = st.number_input("Team 1 ID", min_value=1)
    with col2:
        team2 = st.number_input("Team 2 ID", min_value=1)

    if st.button("Create Match"):
        payload = [
            {
                "season_id": season_id,
                "venue": venue,
                "date": str(date),
                "status": status,
                "participants": [
                    {"team_id": team1, "is_home": True},
                    {"team_id": team2, "is_home": False}
                ]
            }
        ]

        res = requests.post(
            f"{BASE_URL}/matches",
            json=payload,
            headers=get_headers()
        )

        if res.status_code == 201:
            st.success("Match created!")
        else:
            st.error(res.text)

# ---------------------- STANDINGS ----------------------

def standings():
    st.title("🏆 League Standings")

    season_id = st.number_input("Season ID", min_value=1)

    res = requests.get(
        f"{BASE_URL}/standings",
        params={"season_id": season_id}
    )

    data = res.json()

    if data:
        standings = data[0]["standings"]
        df = pd.DataFrame(standings)

        st.dataframe(df, use_container_width=True)

        st.bar_chart(df.set_index("team_name")["points"])

# ---------------------- TEAM ANALYTICS ----------------------

def team_stats():
    st.title("📈 Team Analytics")

    team_id = st.number_input("Team ID", min_value=1)

    res = requests.get(
        f"{BASE_URL}/teams/{team_id}/stats",
        headers=get_headers()
    )

    if res.status_code == 200:
        data = res.json()

        st.metric("Goals Scored", data["goals_scored"])
        st.metric("Matches Played", data["matches_played"])
        st.metric("Points", data["points"])

# ---------------------- MAIN ----------------------

if not st.session_state.token:
    login()
else:
    st.sidebar.title("⚙️ Navigation")

    page = st.sidebar.radio(
        "Go to",
        ["Dashboard", "Create Match", "Standings", "Team Analytics"]
    )

    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.rerun()

    if page == "Dashboard":
        dashboard()
    elif page == "Create Match":
        create_match()
    elif page == "Standings":
        standings()
    elif page == "Team Analytics":
        team_stats()