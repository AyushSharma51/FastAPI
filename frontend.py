import pandas as pd
import requests
import streamlit as st

# ---------------- CONFIG ----------------
API_BASE_URL = "http://localhost:8000"
st.set_page_config(page_title="FOOTBALL DASHBOARD", layout="wide")


# ---------------- UI STYLE ----------------
bg_overlay = "rgba(2,6,23,0.85)"
text_color = "#f1f5f9"
card_bg = "rgba(17,24,39,0.85)"

st.markdown(f"""
<style>

/* BACKGROUND */
[data-testid="stAppViewContainer"] {{
    background: url("https://images.unsplash.com/photo-1489944440615-453fc2b6a9a9?q=80&w=1623&auto=format&fit=crop");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

/* OVERLAY */
[data-testid="stAppViewContainer"]::before {{
    content: "";
    position: fixed;
    inset: 0;
    background: {bg_overlay};
    z-index: 0;
}}

/* TEXT */
html, body, [class*="css"] {{
    color: {text_color};
}}

/* CARD */
.card {{
    background: {card_bg};
    padding: 20px;
    border-radius: 12px;
}}

/* CONTENT */
.block-container {{
    position: relative;
    z-index: 1;
}}

</style>
""", unsafe_allow_html=True)
# ---------------- API ----------------
@st.cache_data(ttl=60)
def fetch(endpoint, params=None):
    try:
        res = requests.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=5)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None


# ---------------- MATCH EXPLORER ----------------
def render_match_explorer():
    st.title("MATCH EXPLORER")

    leagues = fetch("/league")
    if not leagues:
        st.warning("No leagues found")
        return

    league_dict = {l["name"]: l["id"] for l in leagues}  # noqa: E741
    selected_league = st.selectbox("League", list(league_dict.keys()))

    seasons = fetch("/seasons")
    if not seasons:
        st.warning("No seasons found")
        return

    season_dict = {
        f"{s['start_date']} → {s['end_date']}": s["id"]
        for s in seasons
        if str(s.get("league_id")) == str(league_dict[selected_league])
    }

    if not season_dict:
        st.warning("No seasons for this league")
        return

    selected_season = st.selectbox("Season", list(season_dict.keys()))
    season_id = season_dict[selected_season]

    matches_data = fetch("/matches", {"season_id": season_id})
    matches = matches_data.get("matches", []) if matches_data else []

    if not matches:
        st.info("No matches found")
        return

    # METRICS
    c1, c2, c3 = st.columns(3)
    c1.metric("Total", len(matches))
    c2.metric("Completed", sum(m.get("status") == "completed" for m in matches))
    c3.metric("Upcoming", sum(m.get("status") != "completed" for m in matches))

    st.divider()

    # FILTER
    search = st.text_input("Search Match")

    filtered = []
    for m in matches:
        participants = m.get("participants", [])
        home = next((p["team"]["name"] for p in participants if p.get("is_home")), "")
        away = next((p["team"]["name"] for p in participants if not p.get("is_home")), "")

        if not search or search.lower() in (home + away).lower():
            filtered.append(m)

    if not filtered:
        st.warning("No matches found")
        return

    match_dict = {}
    for m in filtered:
        participants = m.get("participants", [])
        home = next((p["team"]["name"] for p in participants if p.get("is_home")), "Home")
        away = next((p["team"]["name"] for p in participants if not p.get("is_home")), "Away")

        label = f"{m.get('date')} | {home} vs {away}"
        match_dict[label] = m["id"]

    selected_match = st.selectbox("Match", list(match_dict.keys()))
    render_match_details(match_dict[selected_match])


def render_match_details(match_id):
    match = fetch(f"/matches/{match_id}")
    if not match:
        return

    match = match.get("matches", [match])[0]
    participants = match.get("participants", [])

    home = next((p for p in participants if p.get("is_home")), {})
    away = next((p for p in participants if not p.get("is_home")), {})

    home_name = home.get("team", {}).get("name", "Home")
    away_name = away.get("team", {}).get("name", "Away")

    stats = fetch("/matches/players/stats") or []
    stats = [s for s in stats if s.get("match_id") == match_id]

    home_id = home.get("team", {}).get("id")
    away_id = away.get("team", {}).get("id")

    home_score = sum(s.get("goals", 0) for s in stats if s.get("team_id") == home_id)
    away_score = sum(s.get("goals", 0) for s in stats if s.get("team_id") == away_id)

    status = match.get("status", "unknown")
    score = f"{home_score} - {away_score}" if status == "completed" else "vs"

    st.markdown(f"""
    <div class="card">
        <h2 style="text-align:center;">{home_name} {score} {away_name}</h2>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Status", status)
    c2.metric("Date", match.get("date"))
    c3.metric("Venue", match.get("venue"))

    if stats:
        df = pd.DataFrame(stats)
        st.dataframe(df, use_container_width=True)


# ---------------- PLAYERS ----------------
def render_players():
    st.title("Players")

    players = fetch("/players")
    if not players:
        st.warning("No players")
        return

    search = st.text_input("Search Player")

    players = [p for p in players if search.lower() in p["name"].lower()] if search else players

    player_dict = {p["name"]: p["id"] for p in players}
    selected = st.selectbox("Player", list(player_dict.keys()))

    stats = fetch(f"/players/{player_dict[selected]}/stats")

    if stats:
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Matches", stats.get("matches_played",0))
        c2.metric("Goals", stats.get("total_goals",0))
        c3.metric("Assists", stats.get("total_assists",0))
        c4.metric("Minutes", stats.get("total_minutes_played",0))


# ---------------- TEAMS ----------------
def render_teams():
    st.title("Teams")

    teams = fetch("/teams")
    if not teams:
        st.warning("No teams")
        return

    st.metric("Total Teams", len(teams))
    st.dataframe(pd.DataFrame(teams), use_container_width=True)


# ---------------- MAIN ----------------
def main():
    st.sidebar.title("Dashboard")

    menu = st.sidebar.radio("Navigation", ["Match Explorer", "Players", "Teams"])

    if menu == "Match Explorer":
        render_match_explorer()
    elif menu == "Players":
        render_players()
    else:
        render_teams()


if __name__ == "__main__":
    main()