# app.py

import streamlit as st
import pandas as pd
import numpy as np
import scipy.stats as stats
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime
import os
import json
import string
import random
import time

# ============================
# ====== CONFIGURATION =======
# ============================

# Define paths for storing leaderboards and game states
LEADERBOARD_PATH = 'leaderboards.json'
GAME_STATE_PATH = 'game_states.json'

# Predefined Game Codes with descriptions and creation dates
PREDEFINED_GAME_CODES = {
    'FINANCE2024': {
        'description': 'Spring Semester Challenge',
        'created_at': '2024-04-01'
    },
    'ARBITRAGEX': {
        'description': 'Arbitrage Expert Mode',
        'created_at': '2024-05-15'
    },
    'GROUPA': {
        'description': 'Group A Competition',
        'created_at': '2024-06-10'
    }
}

# ============================
# ====== HELPER FUNCTIONS =====
# ============================

def load_json(path):
    """Load JSON data from a file."""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        st.error(f"Error decoding JSON from {path}. Please check the file format.")
        return {}

def save_json(path, data):
    """Save JSON data to a file."""
    try:
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        st.error(f"Error saving JSON to {path}: {e}")

def initialize_game_state():
    """Initialize game states for all predefined Game Codes."""
    game_states = load_json(GAME_STATE_PATH)
    updated = False

    for game_code, details in PREDEFINED_GAME_CODES.items():
        if game_code not in game_states:
            # Initialize new game state for this game code
            game_states[game_code] = {
                'players': {},
                'current_round': 1,
                'num_rounds': 15,  # Increased number of rounds for added difficulty
                'assets': ['Asset A', 'Asset B', 'Asset C', 'Asset D', 'Asset E'],
                'asset_initial_prices': [100, 105, 110, 95, 102],
                'asset_price_history': {asset: [price] for asset, price in zip(['Asset A', 'Asset B', 'Asset C', 'Asset D', 'Asset E'], [100, 105, 110, 95, 102])},
                'capital_history': {},  # Populated per player
                'market_conditions': generate_market_conditions(15),
                'leaderboard': {}
            }
            updated = True

    if updated:
        save_json(GAME_STATE_PATH, game_states)

    return game_states

def initialize_leaderboards():
    """Initialize leaderboards if not present."""
    leaderboards = load_json(LEADERBOARD_PATH)
    updated = False

    for game_code in PREDEFINED_GAME_CODES.keys():
        if game_code not in leaderboards:
            leaderboards[game_code] = []
            updated = True

    if updated:
        save_json(LEADERBOARD_PATH, leaderboards)

    return leaderboards

def initialize_player(game_states, player_name, game_code):
    """Add a player to a specific game session."""
    game = game_states[game_code]
    if player_name not in game['players']:
        game['players'][player_name] = {
            'capital': 200000,
            'score': 0,
            'penalties': 0,
            'decisions': [],
            'capital_history': [200000]
        }
        save_json(GAME_STATE_PATH, game_states)
        st.sidebar.success(f"✅ Joined game '{game_code}' as '{player_name}'.")
    else:
        st.sidebar.info(f"ℹ️ You are already in game '{game_code}'.")

def generate_market_conditions(num_rounds):
    """Generate market conditions for the game rounds."""
    conditions = []
    for _ in range(num_rounds):
        condition = np.random.choice(
            ['Stable Market', 'Volatile Market', 'Bull Market', 'Bear Market'], 
            p=[0.3, 0.4, 0.2, 0.1]
        )
        conditions.append(condition)
    return conditions

def simulate_market(asset_prices, market_condition):
    """Simulate market movements based on the current market condition."""
    new_prices = []
    for price in asset_prices:
        if market_condition == 'Bull Market':
            change_percent = np.random.uniform(0.05, 0.15)
        elif market_condition == 'Bear Market':
            change_percent = np.random.uniform(-0.15, -0.05)
        elif market_condition == 'Volatile Market':
            change_percent = np.random.uniform(-0.2, 0.2)
        else:  # Stable Market
            change_percent = np.random.uniform(-0.03, 0.03)
        new_price = price * (1 + change_percent)
        new_prices.append(round(new_price, 2))
    return new_prices

def calculate_statistics(asset_prices, asset_index_1, asset_index_2):
    """Calculate advanced statistical indicators for asset pairs."""
    # Simulate 30-day historical prices with realistic correlations
    np.random.seed()  # Ensure randomness per call
    base_price_1 = asset_prices[asset_index_1]
    base_price_2 = asset_prices[asset_index_2]
    
    # Generate correlated price series
    correlation = np.random.uniform(0.5, 0.95)  # High correlation for arbitrage opportunities
    mean = [base_price_1, base_price_2]
    std_dev = [5, 5]
    cov = [[std_dev[0]**2, correlation * std_dev[0] * std_dev[1]],
           [correlation * std_dev[0] * std_dev[1], std_dev[1]**2]]
    price_series = np.random.multivariate_normal(mean, cov, 30)
    price_series_1 = price_series[:,0]
    price_series_2 = price_series[:,1]
    
    # Moving Averages
    ma_short_1 = np.mean(price_series_1[-5:])
    ma_long_1 = np.mean(price_series_1[-20:])
    ma_short_2 = np.mean(price_series_2[-5:])
    ma_long_2 = np.mean(price_series_2[-20:])
    
    # Correlation
    corr_coef, _ = stats.pearsonr(price_series_1, price_series_2)
    
    # Z-Score
    spread = price_series_1 - price_series_2
    mean_spread = np.mean(spread)
    std_spread = np.std(spread)
    z_score = (spread[-1] - mean_spread) / std_spread if std_spread != 0 else 0
    
    # Bollinger Bands
    bollinger_upper = ma_long_1 + (2 * std_spread)
    bollinger_lower = ma_long_1 - (2 * std_spread)
    
    # RSI
    delta = np.diff(price_series_1)
    up = np.where(delta > 0, delta, 0)
    down = np.where(delta < 0, -delta, 0)
    avg_gain = np.mean(up[-14:]) if len(up) >=14 else np.mean(up)
    avg_loss = np.mean(down[-14:]) if len(down) >=14 else np.mean(down)
    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    rsi = 100 - (100 / (1 + rs))
    
    # MACD
    ema_short = pd.Series(price_series_1).ewm(span=12, adjust=False).mean().iloc[-1]
    ema_long = pd.Series(price_series_1).ewm(span=26, adjust=False).mean().iloc[-1]
    macd = ema_short - ema_long
    signal = pd.Series(price_series_1).ewm(span=9, adjust=False).mean().iloc[-1]
    macd_hist = macd - signal
    
    stats_dict = {
        'ma_short_1': round(ma_short_1, 2),
        'ma_long_1': round(ma_long_1, 2),
        'ma_short_2': round(ma_short_2, 2),
        'ma_long_2': round(ma_long_2, 2),
        'correlation': round(corr_coef, 2),
        'z_score': round(z_score, 2),
        'bollinger_upper': round(bollinger_upper, 2),
        'bollinger_lower': round(bollinger_lower, 2),
        'rsi': round(rsi, 2),
        'macd': round(macd, 2),
        'signal': round(signal, 2),
        'macd_hist': round(macd_hist, 2)
    }
    return stats_dict, price_series_1, price_series_2

def update_leaderboard(game_code):
    """Update the leaderboard for a specific game code."""
    game_states = load_json(GAME_STATE_PATH)
    game = game_states[game_code]
    players = game['players']
    leaderboard = []
    for player, data in players.items():
        final_score = data['score'] - data['penalties']
        leaderboard.append({
            'Player': player,
            'Score': final_score,
            'Capital': round(data['capital'], 2),
            'Penalties': data['penalties'],
            'Decisions Made': len(data['decisions'])
        })
    leaderboard_df = pd.DataFrame(leaderboard)
    leaderboard_df = leaderboard_df.sort_values(by=['Score', 'Capital'], ascending=[False, False])
    game_states[game_code]['leaderboard'] = leaderboard_df.to_dict('records')
    save_json(GAME_STATE_PATH, game_states)
    return leaderboard_df

def plot_capital_history(player_data):
    """Plot the capital history of a player."""
    rounds = list(range(1, len(player_data['capital_history']) + 1))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rounds, y=player_data['capital_history'],
                             mode='lines+markers',
                             name='Capital'))
    fig.update_layout(title='📈 Capital Over Time',
                      xaxis_title='Round',
                      yaxis_title='Capital ($)',
                      template='plotly_dark')
    return fig

def plot_asset_prices(price_series_1, price_series_2, stats_dict, asset_pair):
    """Plot the asset prices along with statistical indicators."""
    df = pd.DataFrame({
        'Asset 1': price_series_1,
        'Asset 2': price_series_2
    })
    df.index = pd.RangeIndex(start=1, stop=len(df)+1, step=1)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Asset 1'], mode='lines', name=asset_pair.split(' & ')[0]))
    fig.add_trace(go.Scatter(x=df.index, y=df['Asset 2'], mode='lines', name=asset_pair.split(' & ')[1]))
    
    # Add Moving Averages
    fig.add_trace(go.Scatter(x=df.index, y=[stats_dict['ma_short_1']]*len(df), mode='lines', name='MA Short 1', line=dict(dash='dash')))
    fig.add_trace(go.Scatter(x=df.index, y=[stats_dict['ma_long_1']]*len(df), mode='lines', name='MA Long 1', line=dict(dash='dash')))
    
    # Add Bollinger Bands
    fig.add_trace(go.Scatter(x=df.index, y=[stats_dict['bollinger_upper']]*len(df), mode='lines', name='Bollinger Upper', line=dict(color='rgba(255,0,0,0.5)', dash='dot')))
    fig.add_trace(go.Scatter(x=df.index, y=[stats_dict['bollinger_lower']]*len(df), mode='lines', name='Bollinger Lower', line=dict(color='rgba(255,0,0,0.5)', dash='dot')))
    
    fig.update_layout(title=f'📉 Asset Prices and Indicators for {asset_pair}',
                      xaxis_title='Time',
                      yaxis_title='Price ($)',
                      template='plotly_dark',
                      legend=dict(x=0.01, y=0.99))
    return fig

def plot_heatmap(correlation_matrix, asset_names):
    """Plot a heatmap of asset correlations."""
    fig = px.imshow(correlation_matrix,
                    x=asset_names,
                    y=asset_names,
                    color_continuous_scale='Viridis',
                    title='🔍 Asset Correlation Heatmap')
    fig.update_layout(template='plotly_dark')
    return fig

def plot_z_score_distribution(z_scores):
    """Plot the distribution of Z-Scores."""
    fig = px.histogram(z_scores, nbins=20, title='📊 Z-Score Distribution', labels={'value':'Z-Score'}, template='plotly_dark')
    fig.update_layout(xaxis_title='Z-Score', yaxis_title='Frequency')
    return fig

def plot_decision_impact(player_data):
    """Plot the impact of player's decisions on their capital."""
    rounds = list(range(1, len(player_data['decisions']) + 1))
    rewards = [decision['reward'] for decision in player_data['decisions']]
    penalties = [decision['penalty'] for decision in player_data['decisions']]
    actions = [decision['action'] for decision in player_data['decisions']]
    
    df = pd.DataFrame({
        'Round': rounds,
        'Reward': rewards,
        'Penalty': penalties,
        'Action': actions
    })
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['Round'], y=df['Reward'], name='Rewards', marker_color='green'))
    fig.add_trace(go.Bar(x=df['Round'], y=df['Penalty'], name='Penalties', marker_color='red'))
    fig.update_layout(title='📉 Decision Impact on Capital',
                      xaxis_title='Round',
                      yaxis_title='Amount ($)',
                      barmode='relative',
                      template='plotly_dark')
    return fig

# ============================
# ====== STREAMLIT APP ========
# ============================

# Initialize game states and leaderboards
game_states = initialize_game_state()
leaderboards = initialize_leaderboards()

st.set_page_config(page_title="Statistical Arbitrage Showdown 📊⚖️", layout="wide", initial_sidebar_state="expanded")
st.title("📊⚖️ **Statistical Arbitrage Showdown**")

# Sidebar for Player Registration
st.sidebar.header("🔐 Player Registration")
player_name = st.sidebar.text_input("👤 Enter Your Name", max_chars=20)
game_code = st.sidebar.selectbox(
    "🎮 Select Game Code",
    options=list(PREDEFINED_GAME_CODES.keys()),
    format_func=lambda x: f"{x} - {PREDEFINED_GAME_CODES[x]['description']}"
)
join_button = st.sidebar.button("🚀 Join Game")

if join_button:
    if player_name.strip() == "":
        st.sidebar.error("❗ Please enter a valid name.")
    else:
        initialize_player(game_states, player_name, game_code)

# Refresh game states after potential updates
game_states = load_json(GAME_STATE_PATH)

# Proceed only if player has joined a game
if player_name and game_code:
    if player_name not in game_states[game_code]['players']:
        st.warning(f"You need to join the game '{game_code}' by clicking 'Join Game'.")
    else:
        game = game_states[game_code]
        player = game['players'][player_name]
        
        # Display Game Information
        st.subheader(f"🏆 **Game Code:** {game_code} - {PREDEFINED_GAME_CODES[game_code]['description']} 🏆")
        st.write(f"**Round:** {game['current_round']} / {game['num_rounds']}")
        st.write(f"**Capital:** ${player['capital']:.2f}")
        st.write(f"**Score:** {player['score']} | **Penalties:** {player['penalties']}")
        
        # Display Correlation Heatmap for All Assets
        st.markdown("### 🔍 **Asset Correlation Heatmap**")
        asset_names = game['assets']
        # Generate a correlation matrix for visualization
        # Using the 'asset_price_history' to compute correlations
        asset_price_history = game['asset_price_history']
        correlation_matrix = pd.DataFrame(asset_price_history).corr().values
        fig_heatmap = plot_heatmap(correlation_matrix, asset_names)
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # If game is ongoing
        if game['current_round'] <= game['num_rounds']:
            current_round = game['current_round']
            current_market = game['market_conditions'][current_round -1]
            st.markdown(f"### 📈 **Current Market Condition:** {current_market}")
            
            # Asset Selection
            st.subheader("📊 **Select Asset Pair for Arbitrage**")
            asset_options = game['assets']
            asset_pair = st.selectbox("🔀 Choose a pair of assets to trade:", 
                                      [f"{asset_options[i]} & {asset_options[j]}" 
                                       for i in range(len(asset_options)) 
                                       for j in range(i+1, len(asset_options))])
            asset_indices = [i for i in range(len(asset_options)) if asset_options[i] in asset_pair]
            if len(asset_indices) !=2:
                st.error("❗ Please select a valid pair of assets.")
                st.stop()
            asset_index_1, asset_index_2 = asset_indices
            
            # Display Asset Prices
            st.markdown("### 💲 **Current Asset Prices:**")
            asset_prices_display = ", ".join([f"{asset}: ${price:.2f}" for asset, price in zip(game['assets'], game['asset_initial_prices'])])
            st.write(asset_prices_display)
            
            # Calculate and Display Advanced Statistics
            stats_dict, price_series_1, price_series_2 = calculate_statistics(game['asset_initial_prices'], asset_index_1, asset_index_2)
            st.markdown("### 📉 **Statistical Indicators:**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🔗 Correlation", stats_dict['correlation'])
                st.metric("📊 Z-Score", stats_dict['z_score'])
            with col2:
                st.metric("📈 MA Short (5)", stats_dict['ma_short_1'])
                st.metric("📉 Bollinger Upper", stats_dict['bollinger_upper'])
            with col3:
                st.metric("📉 MA Long (20)", stats_dict['ma_long_1'])
                st.metric("📈 Bollinger Lower", stats_dict['bollinger_lower'])
            with col4:
                st.metric("🔺 RSI", stats_dict['rsi'])
                st.metric("📉 MACD Hist", stats_dict['macd_hist'])
            
            # Plot Asset Prices with Indicators
            st.markdown("### 📈 **Asset Price Movements with Indicators:**")
            fig_assets = plot_asset_prices(price_series_1, price_series_2, stats_dict, asset_pair)
            st.plotly_chart(fig_assets, use_container_width=True)
            
            # Plot Z-Score Distribution
            st.markdown("### 📊 **Z-Score Distribution:**")
            z_scores = [decision['z_score'] for decision in player['decisions']] if player['decisions'] else []
            if z_scores:
                fig_z = plot_z_score_distribution(z_scores)
                st.plotly_chart(fig_z, use_container_width=True)
            else:
                st.write("No Z-Score data available yet.")
            
            # Decision Making
            st.subheader("⚖️ **Your Decision**")
            action = st.radio("🕹️ Choose your action:", ("🔼 Go Long", "🔽 Go Short", "⏸️ Hold"))
            risk_level = st.slider("🎯 Risk Level:", 1, 10, 5)
            
            if st.button("✅ Execute Decision"):
                # Decision Logic
                reward = 0
                penalty = 0
                successful = False
                if action != "⏸️ Hold":
                    if (action == "🔼 Go Long" and stats_dict['z_score'] > 1) or (action == "🔽 Go Short" and stats_dict['z_score'] < -1):
                        # Successful Arbitrage
                        reward = risk_level * 1500  # Increased reward for higher difficulty
                        player['capital'] += reward
                        player['score'] += int(reward / 150)  # Adjusted scoring
                        successful = True
                        st.success(f"🎉 **Successful Arbitrage!** You earned **${reward}**.")
                    else:
                        # Failed Arbitrage
                        penalty = risk_level * 700  # Increased penalty for higher difficulty
                        player['capital'] -= penalty
                        player['penalties'] += penalty
                        st.error(f"⚠️ **Failed Arbitrage.** You lost **${penalty}**.")
                else:
                    st.info("🟡 You chose to hold. No action taken.")
                
                # Update Capital History
                player['capital_history'].append(player['capital'])
                
                # Record Decision
                player['decisions'].append({
                    'round': current_round,
                    'asset_pair': asset_pair,
                    'action': action,
                    'risk_level': risk_level,
                    'reward': reward,
                    'penalty': penalty,
                    'successful': successful,
                    'timestamp': datetime.utcnow().isoformat(),
                    'z_score': stats_dict['z_score']
                })
                
                # Update Asset Price History
                for i, asset in enumerate(game['assets']):
                    game['asset_price_history'][asset].append(game['asset_initial_prices'][i])
                
                # Simulate Market for Next Round
                new_prices = simulate_market(game['asset_initial_prices'], current_market)
                game['asset_initial_prices'] = new_prices
                
                # Update Leaderboard
                leaderboard_df = update_leaderboard(game_code)
                
                # Move to Next Round
                game['current_round'] +=1
                
                # Save updated game state
                game_states[game_code] = game
                save_json(GAME_STATE_PATH, game_states)
                
                # Optional: Add a brief pause before rerunning
                time.sleep(1)
                
                st.experimental_rerun()
            
            # Plot Decision Impact
            st.markdown("### 📉 **Decision Impact on Capital:**")
            fig_decision = plot_decision_impact(player)
            st.plotly_chart(fig_decision, use_container_width=True)
        
        else:
            # Game Over Section
            st.success("🏁 **Game Over!** 🏁")
            final_score = player['score'] - player['penalties']
            st.write(f"**Final Score:** {final_score}")
            st.write(f"**Final Capital:** ${player['capital']:.2f}")
            
            # Plot Capital History
            st.markdown("### 📈 **Your Capital Over Time:**")
            fig_capital = plot_capital_history(player)
            st.plotly_chart(fig_capital, use_container_width=True)
            
            # Plot Decision Impact
            st.markdown("### 📉 **Your Decision Impact:**")
            fig_decision = plot_decision_impact(player)
            st.plotly_chart(fig_decision, use_container_width=True)
            
            # Display Leaderboard
            st.markdown("### 🏆 **Leaderboard:**")
            leaderboard_df = pd.DataFrame(game['leaderboard'])
            if not leaderboard_df.empty:
                st.table(leaderboard_df)
            else:
                st.write("No leaderboard data available.")
            
            # Update Global Leaderboard
            leaderboards = load_json(LEADERBOARD_PATH)
            if game_code not in leaderboards:
                leaderboards[game_code] = []
            leaderboards[game_code].append({
                'Player': player_name,
                'Final Score': final_score,
                'Final Capital': round(player['capital'], 2),
                'Date': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
            })
            save_json(LEADERBOARD_PATH, leaderboards)
            
            st.markdown("---")
            st.markdown("**Statistical Arbitrage Showdown 📊⚖️** - Developed with ❤️ by [Shashank](https://github.com/shashoriginal). Empowering the next generation of Quantitative Finance professionals.")
    
else:
    st.info("🔍 **Join a Game** by entering your name and selecting a Game Code in the sidebar.")

# ============================
# ====== FOOTER SECTION ========
# ============================

st.markdown("---")
st.markdown("**Statistical Arbitrage Showdown 📊⚖️** - Developed with ❤️ by [Shashank](https://github.com/shashoriginal). Empowering the next generation of Quantitative Finance professionals.")

