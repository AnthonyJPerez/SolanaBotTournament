import pytest
from unittest.mock import patch, MagicMock
from solana_bot_tournament.api import helius_get, telegram_send, twitter_send


@patch('solana_bot_tournament.api._session')
def test_helius_get(mock_session):
    mock_response = MagicMock()
    mock_response.json.return_value = {"result": "success"}
    mock_session.get.return_value = mock_response
    
    with patch('solana_bot_tournament.api.HELIUS_API_KEY', 'test_key'):
        result = helius_get("/test", param1="value1")
    
    mock_session.get.assert_called_once()
    call_args = mock_session.get.call_args
    assert "/test" in call_args[0][0]
    assert call_args[1]['params']['api-key'] == 'test_key'
    assert call_args[1]['params']['param1'] == 'value1'
    assert result == {"result": "success"}


@patch('solana_bot_tournament.api._session')
@patch('solana_bot_tournament.api.TG_TOKEN', 'test_token')
@patch('solana_bot_tournament.api.TG_CHAT_ID', 'test_chat_id')
def test_telegram_send(mock_session):
    mock_session.post.return_value = MagicMock()
    
    telegram_send("Test message")
    
    mock_session.post.assert_called_once()
    call_args = mock_session.post.call_args
    assert "bot" in call_args[0][0]
    assert call_args[1]['json']['text'] == "Test message"
    assert call_args[1]['json']['chat_id'] == 'test_chat_id'


@patch('solana_bot_tournament.api.TG_TOKEN', '')
@patch('solana_bot_tournament.api._session')
def test_telegram_send_no_token(mock_session):
    telegram_send("Test message")
    mock_session.post.assert_not_called()


@patch('solana_bot_tournament.api.TWITTER_API_KEY', 'test_key')
def test_twitter_send_text_only():
    with patch('solana_bot_tournament.api.TW_API') as mock_tw_api:
        twitter_send("Test tweet")
        mock_tw_api.update_status.assert_called_once_with("Test tweet")


@patch('solana_bot_tournament.api.TWITTER_API_KEY', 'test_key')
def test_twitter_send_with_media():
    with patch('solana_bot_tournament.api.TW_API') as mock_tw_api:
        twitter_send("Test tweet", "/path/to/image.png")
        mock_tw_api.update_status_with_media.assert_called_once_with("Test tweet", "/path/to/image.png")


@patch('solana_bot_tournament.api.TWITTER_API_KEY', '')
def test_twitter_send_no_api_key():
    # Should not raise an error when no API key is set
    twitter_send("Test tweet")  # Should silently do nothing