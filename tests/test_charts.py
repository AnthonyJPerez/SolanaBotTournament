import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from solana_bot_tournament.charts import balance_chart


@patch('solana_bot_tournament.charts.plt')
@patch('solana_bot_tournament.charts.WALLETS', {"Bot1": "addr1", "Bot2": "addr2"})
@patch('solana_bot_tournament.charts.INITIAL_BALANCE_SOL', 50.0)
def test_balance_chart(mock_plt):
    test_history = {
        "1": {"Bot1": 50.5, "Bot2": 49.8},
        "2": {"Bot1": 51.0, "Bot2": 50.2},
        "3": {"Bot1": 50.8, "Bot2": 49.5}
    }
    
    outfile = Path("/tmp/test_chart.png")
    
    balance_chart(test_history, outfile)
    
    # Verify matplotlib calls
    mock_plt.figure.assert_called_once_with(figsize=(10, 6))
    mock_plt.plot.assert_called()  # Should be called for each bot
    mock_plt.xlabel.assert_called_once_with("Day")
    mock_plt.ylabel.assert_called_once_with("SOL Balance")
    mock_plt.title.assert_called_once_with("Bot Tournament - Balance History")
    mock_plt.grid.assert_called_once_with(True, alpha=0.3)
    mock_plt.legend.assert_called_once()
    mock_plt.tight_layout.assert_called_once()
    # Check savefig was called with the correct arguments
    mock_plt.savefig.assert_called_once()
    call_args = mock_plt.savefig.call_args
    assert call_args[0][0] == outfile
    assert call_args[1]['dpi'] == 300
    assert call_args[1]['bbox_inches'] == 'tight'
    mock_plt.close.assert_called_once()


@patch('solana_bot_tournament.charts.plt')
@patch('solana_bot_tournament.charts.WALLETS', {"SingleBot": "addr1"})
@patch('solana_bot_tournament.charts.INITIAL_BALANCE_SOL', 100.0)
def test_balance_chart_single_bot(mock_plt):
    test_history = {
        "1": {"SingleBot": 105.0},
        "2": {"SingleBot": 98.0}
    }
    
    outfile = Path("/tmp/single_bot_chart.png")
    
    balance_chart(test_history, outfile)
    
    # Should still create chart for single bot
    mock_plt.figure.assert_called_once()
    mock_plt.plot.assert_called()
    # Check savefig was called with the correct file
    mock_plt.savefig.assert_called_once()
    call_args = mock_plt.savefig.call_args
    assert call_args[0][0] == outfile