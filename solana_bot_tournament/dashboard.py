"""Streamlit dashboard entry‑point."""
import streamlit as st
import pandas as pd
import logging
from pathlib import Path
from .config import START_DATE, HISTORY_FILE, TRADE_LOG_FILE, INITIAL_BALANCE_SOL, WALLETS
from .persistence import load_json
from .charts import balance_chart

def main():
    """Main dashboard function with proper error handling."""
    st.set_page_config(page_title="Solana Bot Dashboard", layout="wide")
    
    try:
        # Cache data loading
        @st.cache_data(ttl=300)  # Cache for 5 minutes
        def load_dashboard_data():
            hist = load_json(HISTORY_FILE, {})
            trades = load_json(TRADE_LOG_FILE, [])
            return hist, trades
        
        hist, all_trades = load_dashboard_data()
        
        if not hist:
            st.error("❌ No balance history found. Run the daily job first to populate data.")
            st.info("💡 Use: `python -m solana_bot_tournament.cli daily`")
            return
        
        # Sidebar controls
        st.sidebar.title("🤖 Bot Selection")
        sel_bot = st.sidebar.selectbox("Choose Bot:", list(WALLETS.keys()))
        
        # Main dashboard
        st.title("📊 Solana Bot Tournament Dashboard")
        
        # Balance chart
        days = sorted(map(int, hist.keys()))
        if days:
            balances = [hist[str(d)].get(sel_bot, INITIAL_BALANCE_SOL) for d in days]
            
            st.subheader(f"💰 {sel_bot} Balance History")
            chart_df = pd.DataFrame({"Day": days, "Balance (SOL)": balances})
            st.line_chart(chart_df.set_index("Day"))
            
            # Display current balance
            current_balance = balances[-1] if balances else INITIAL_BALANCE_SOL
            pnl = current_balance - INITIAL_BALANCE_SOL
            pnl_color = "green" if pnl >= 0 else "red"
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Balance", f"{current_balance:.4f} SOL")
            with col2:
                st.metric("Total PnL", f"{pnl:+.4f} SOL", delta_color="normal")
            with col3:
                roi = (pnl / INITIAL_BALANCE_SOL) * 100
                st.metric("ROI", f"{roi:+.2f}%")
        
        # Trade log section
        bot_trades = [t for t in all_trades if t.get('bot') == sel_bot]
        
        if bot_trades:
            st.subheader(f"📋 {sel_bot} Trade History")
            
            df = pd.DataFrame(bot_trades)
            
            # Add some formatting
            if 'ts' in df.columns:
                df['timestamp'] = pd.to_datetime(df['ts'], unit='s')
            
            # Display metrics
            total_trades = len(df)
            winning_trades = len(df[df['pnl'] > 0]) if 'pnl' in df.columns else 0
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Trades", total_trades)
            with col2:
                st.metric("Winning Trades", winning_trades)
            with col3:
                st.metric("Win Rate", f"{win_rate:.1f}%")
            
            # Trade table
            st.dataframe(df, use_container_width=True)
            
            # Strategy distribution
            if 'strategy' in df.columns:
                st.subheader(f"🎯 {sel_bot} Strategy Distribution")
                strategy_counts = df['strategy'].value_counts()
                st.bar_chart(strategy_counts)
        else:
            st.info(f"📭 No trades recorded yet for {sel_bot}.")
            st.markdown("*Trades will appear here after running the daily job.*")
    
    except Exception as e:
        st.error(f"❌ Dashboard error: {str(e)}")
        logging.error(f"Dashboard error: {e}")

if __name__ == "__main__":
    main()
else:
    main()  # Also run when imported as module