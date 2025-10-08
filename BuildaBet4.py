# buildabet.py
import streamlit as st
import pandas as pd
import requests

# --- Session state ---
for key in ['page','sport','game']:
    if key not in st.session_state:
        st.session_state[key] = None
if st.session_state['page'] is None:
    st.session_state['page'] = 'home'

# --- API-Sports key ---
API_KEY = "30838192404ab22d79cbc4b13460279d"
HEADERS = {"x-apisports-key": API_KEY}

# --- Team logos ---
TEAM_LOGOS = {
    "KC":"https://a.espncdn.com/i/teamlogos/nfl/500/kc.png",
    "BUF":"https://a.espncdn.com/i/teamlogos/nfl/500/buf.png",
    "NE":"https://a.espncdn.com/i/teamlogos/nfl/500/ne.png",
    "MIA":"https://a.espncdn.com/i/teamlogos/nfl/500/mia.png",
    "LAL":"https://a.espncdn.com/i/teamlogos/nba/500/lal.png",
    "GSW":"https://a.espncdn.com/i/teamlogos/nba/500/gs.png",
    "BKN":"https://a.espncdn.com/i/teamlogos/nba/500/bkn.png",
    "MIL":"https://a.espncdn.com/i/teamlogos/nba/500/mil.png",
    "NYY":"https://a.espncdn.com/i/teamlogos/mlb/500/nyy.png",
    "BOS":"https://a.espncdn.com/i/teamlogos/mlb/500/bos.png",
    "LAD":"https://a.espncdn.com/i/teamlogos/mlb/500/lad.png",
    "SF":"https://a.espncdn.com/i/teamlogos/mlb/500/sf.png"
}

# --- Fetch live games ---
def fetch_games(sport):
    league_ids = {"NFL":3,"NBA":12,"MLB":1,"CFB":None}  # league IDs for API-Sports
    league = league_ids.get(sport)
    
    if sport == "CFB":
        # Simulate CFB games (or you can add live API if supported)
        return [
            {"home":"Ohio State","away":"Michigan","time":"12:00","id":"OSU_MICH"},
            {"home":"Alabama","away":"LSU","time":"15:30","id":"ALAB_LSU"}
        ]
    
    url = f"https://v1.api-sports.io/fixtures?league={league}&season=2025"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        data = r.json()
        games = []
        if "response" in data and isinstance(data["response"], list):
            for g in data["response"]:
                home = g["teams"]["home"]["name"]
                away = g["teams"]["away"]["name"]
                fixture_time = g["fixture"].get("date","TBD").split("T")[1][:5] if "fixture" in g else "TBD"
                game_id = str(g["fixture"]["id"]) if "fixture" in g else "unknown"
                games.append({"home":home,"away":away,"time":fixture_time,"id":game_id})
        return games
    except Exception as e:
        st.error(f"Error fetching games: {e}")
        return []

# --- Fetch live odds ---
def fetch_odds(game_id):
    url = f"https://v1.api-sports.io/odds?fixture={game_id}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        data = r.json()
        if "response" in data: 
            return data["response"]
        return {"info":"No odds available"}
    except Exception as e:
        return {"error":f"Error fetching odds: {e}"}

# --- Fetch player stats (simulated) ---
def fetch_player_stats(team):
    # Normally would fetch real player data via API-Sports or ESPN
    return [
        {"name":"QB1","pass_yards":280,"rush_yards":30,"rec_yards":0,"image":"https://a.espncdn.com/combiner/i?img=/i/headshots/nfl/players/full/4032974.png&w=100&h=100"},
        {"name":"RB1","pass_yards":0,"rush_yards":100,"rec_yards":20,"image":"https://a.espncdn.com/combiner/i?img=/i/headshots/nfl/players/full/3912305.png&w=100&h=100"},
        {"name":"WR1","pass_yards":0,"rush_yards":10,"rec_yards":70,"image":"https://a.espncdn.com/combiner/i?img=/i/headshots/nfl/players/full/3927934.png&w=100&h=100"}
    ]

# --- Calculate player props ---
def calculate_props(players):
    props = []
    for p in players:
        props.append({"player":p['name'],"prop":"Passing Yards","line":p['pass_yards'],
                      "odds":1.9,"reason":"Based on season stats and performance","image":p['image']})
        props.append({"player":p['name'],"prop":"Rushing Yards","line":p['rush_yards'],
                      "odds":1.85,"reason":"Expected workload","image":p['image']})
        props.append({"player":p['name'],"prop":"Receiving Yards","line":p['rec_yards'],
                      "odds":1.85,"reason":"Expected target share","image":p['image']})
    return pd.DataFrame(props)

# --- Streamlit UI ---
st.set_page_config(page_title="Build a Bet", layout="wide")
st.title("🏗 Build a Bet 🏗")

# --- Home Page ---
if st.session_state['page']=='home':
    st.markdown("### Which sport would you like to bet on?")
    col1,col2 = st.columns(2)
    col3,col4 = st.columns(2)
    with col1:
        if st.button("NFL 🏈"): st.session_state.update({'sport':'NFL','page':'games'}); st.experimental_rerun()
    with col2:
        if st.button("NBA 🏀"): st.session_state.update({'sport':'NBA','page':'games'}); st.experimental_rerun()
    with col3:
        if st.button("MLB ⚾️"): st.session_state.update({'sport':'MLB','page':'games'}); st.experimental_rerun()
    with col4:
        if st.button("CFB 🏟"): st.session_state.update({'sport':'CFB','page':'games'}); st.experimental_rerun()

# --- Games Page ---
elif st.session_state['page']=='games':
    sport = st.session_state['sport']
    st.header(f"{sport} Games")
    games = fetch_games(sport)
    if not games: st.info("No games found.")
    else:
        cols = st.columns(2)
        for idx, g in enumerate(games):
            col = cols[idx%2]
            home, away, time, game_id = g['home'], g['away'], g['time'], g['id']
            home_logo, away_logo = TEAM_LOGOS.get(home,""), TEAM_LOGOS.get(away,"")
            with col:
                st.markdown(f"""
                <div style='border:1px solid #ddd; padding:10px; border-radius:10px; text-align:center; margin-bottom:10px;'>
                <h3>{away} @ {home}</h3>
                <p>{time}</p>
                <div style='display:flex; justify-content:space-around; align-items:center;'>
                <img src='{away_logo}' width='50'>
                <img src='{home_logo}' width='50'>
                </div></div>""", unsafe_allow_html=True)
                if st.button(f"Build Bet for {away} @ {home}", key=game_id):
                    st.session_state.update({'game':game_id,'page':'bets'})
                    st.experimental_rerun()
    if st.button("⬅ Back to Home"): st.session_state['page']='home'; st.experimental_rerun()

# --- Bets Page ---
elif st.session_state['page']=='bets':
    sport = st.session_state['sport']
    game_id = st.session_state['game']
    st.header(f"💰 Build a Bet: Game ID {game_id}")

    # Live Odds
    st.subheader("Live Odds")
    odds = fetch_odds(game_id)
    st.write(odds)

    # Player Props
    st.subheader("Player Props")
    home_team = game_id.split("_")[0] if "_" in game_id else "Team1"
    away_team = game_id.split("_")[1] if "_" in game_id else "Team2"
    players = fetch_player_stats(home_team) + fetch_player_stats(away_team)
    df_props = calculate_props(players)
    
    for idx, row in df_props.iterrows():
        st.markdown(f"""
        <div style='border:1px solid #ccc; padding:10px; border-radius:10px; display:flex; align-items:center; margin-bottom:5px;'>
        <img src='{row["image"]}' width='50' style='margin-right:10px;'>
        <div>
        <b>{row["player"]}</b> - {row["prop"]} ({row["line"]} yds) <br>
        Odds: {row["odds"]} | {row["reason"]}
        </div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("⬅ Back to Games"): st.session_state['page']='games'; st.experimental_rerun()
