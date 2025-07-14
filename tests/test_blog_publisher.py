import pytest
from unittest.mock import patch, MagicMock
from solana_bot_tournament.blog_publisher import (
    BlogPost, MediumPublisher, DevToPublisher, HashnodePublisher,
    BloggerPublisher, MultiPlatformPublisher, get_blog_status
)


def test_blog_post_creation():
    post = BlogPost(
        title="Test Post",
        content="# Test Content",
        tags=["test", "blog"],
        canonical_url="https://example.com/test",
        published=True
    )
    
    assert post.title == "Test Post"
    assert post.content == "# Test Content"
    assert post.tags == ["test", "blog"]
    assert post.canonical_url == "https://example.com/test"
    assert post.published is True
    assert post.created_at is not None


@patch('solana_bot_tournament.blog_publisher.MEDIUM_ACCESS_TOKEN', '')
def test_medium_publisher_not_configured():
    publisher = MediumPublisher()
    assert not publisher.is_configured()


@patch('solana_bot_tournament.blog_publisher.MEDIUM_ACCESS_TOKEN', 'test_token')
def test_medium_publisher_configured():
    publisher = MediumPublisher()
    assert publisher.is_configured()


@patch('solana_bot_tournament.blog_publisher.MEDIUM_ACCESS_TOKEN', 'test_token')
def test_medium_publisher_publish():
    publisher = MediumPublisher()
    
    # Mock the session responses
    user_response = MagicMock()
    user_response.json.return_value = {"data": {"id": "user123"}}
    
    post_response = MagicMock()
    post_response.json.return_value = {
        "data": {
            "id": "post123",
            "url": "https://medium.com/@user/test-post-123"
        }
    }
    
    with patch.object(publisher.session, 'get', return_value=user_response), \
         patch.object(publisher.session, 'post', return_value=post_response):
        
        post = BlogPost("Test Title", "Test content", ["test"])
        result = publisher.publish(post)
        
        assert result["success"] is True
        assert result["platform"] == "Medium"
        assert "url" in result
        assert "id" in result


@patch('solana_bot_tournament.blog_publisher.DEVTO_API_KEY', '')
def test_devto_publisher_not_configured():
    publisher = DevToPublisher()
    assert not publisher.is_configured()


@patch('solana_bot_tournament.blog_publisher.DEVTO_API_KEY', 'test_key')
def test_devto_publisher_configured():
    publisher = DevToPublisher()
    assert publisher.is_configured()


@patch('solana_bot_tournament.blog_publisher.DEVTO_API_KEY', 'test_key')
def test_devto_publisher_publish():
    publisher = DevToPublisher()
    
    response = MagicMock()
    response.json.return_value = {
        "id": 456,
        "url": "https://dev.to/user/test-post-456"
    }
    
    with patch.object(publisher.session, 'post', return_value=response):
        post = BlogPost("Test Title", "Test content", ["test", "dev"])
        result = publisher.publish(post)
        
        assert result["success"] is True
        assert result["platform"] == "Dev.to"
        assert result["url"] == "https://dev.to/user/test-post-456"


@patch('solana_bot_tournament.blog_publisher.HASHNODE_ACCESS_TOKEN', '')
@patch('solana_bot_tournament.blog_publisher.HASHNODE_PUBLICATION_ID', '')
def test_hashnode_publisher_not_configured():
    publisher = HashnodePublisher()
    assert not publisher.is_configured()


@patch('solana_bot_tournament.blog_publisher.HASHNODE_ACCESS_TOKEN', 'test_token')
@patch('solana_bot_tournament.blog_publisher.HASHNODE_PUBLICATION_ID', 'pub123')
def test_hashnode_publisher_configured():
    publisher = HashnodePublisher()
    assert publisher.is_configured()


@patch('solana_bot_tournament.blog_publisher.BLOGGER_CLIENT_ID', '')
@patch('solana_bot_tournament.blog_publisher.BLOGGER_CLIENT_SECRET', '')
@patch('solana_bot_tournament.blog_publisher.BLOGGER_BLOG_ID', '')
def test_blogger_publisher_not_configured():
    publisher = BloggerPublisher()
    assert not publisher.is_configured()


@patch('solana_bot_tournament.blog_publisher.BLOGGER_CLIENT_ID', 'test_client_id')
@patch('solana_bot_tournament.blog_publisher.BLOGGER_CLIENT_SECRET', 'test_client_secret')
@patch('solana_bot_tournament.blog_publisher.BLOGGER_BLOG_ID', '123456789')
def test_blogger_publisher_configured():
    publisher = BloggerPublisher()
    assert publisher.is_configured()


@patch('solana_bot_tournament.blog_publisher.BLOGGER_CLIENT_ID', 'test_client_id')
@patch('solana_bot_tournament.blog_publisher.BLOGGER_CLIENT_SECRET', 'test_client_secret')
@patch('solana_bot_tournament.blog_publisher.BLOGGER_BLOG_ID', '123456789')
def test_blogger_oauth_authorization_url():
    publisher = BloggerPublisher()
    auth_url = publisher.get_authorization_url()
    
    assert "client_id=test_client_id" in auth_url
    assert "response_type=code" in auth_url
    assert "scope=https://www.googleapis.com/auth/blogger" in auth_url
    assert "redirect_uri=urn:ietf:wg:oauth:2.0:oob" in auth_url
    assert auth_url.startswith("https://accounts.google.com/o/oauth2/auth")


@patch('solana_bot_tournament.blog_publisher.BLOGGER_CLIENT_ID', 'test_client_id')
@patch('solana_bot_tournament.blog_publisher.BLOGGER_CLIENT_SECRET', 'test_client_secret') 
@patch('solana_bot_tournament.blog_publisher.BLOGGER_BLOG_ID', '123456789')
def test_blogger_publish_without_token():
    publisher = BloggerPublisher()
    post = BlogPost("Test Title", "Test content", ["test"])
    
    # Mock the _get_access_token to return None (no token available)
    with patch.object(publisher, '_get_access_token', return_value=None):
        result = publisher.publish(post)
        
        assert result["success"] is False
        assert "access token not available" in result["error"]
        assert result["platform"] == "Blogger"


@patch('solana_bot_tournament.blog_publisher.BLOGGER_CLIENT_ID', 'test_client_id')
@patch('solana_bot_tournament.blog_publisher.BLOGGER_CLIENT_SECRET', 'test_client_secret') 
@patch('solana_bot_tournament.blog_publisher.BLOGGER_BLOG_ID', '123456789')
def test_blogger_token_validation():
    publisher = BloggerPublisher()
    
    # Mock a successful validation response
    mock_response = MagicMock()
    mock_response.status_code = 200
    
    with patch.object(publisher.session, 'get', return_value=mock_response):
        assert publisher._validate_token("valid_token") is True
    
    # Mock a failed validation response
    mock_response.status_code = 401
    
    with patch.object(publisher.session, 'get', return_value=mock_response):
        assert publisher._validate_token("invalid_token") is False


@patch('solana_bot_tournament.blog_publisher.BLOGGER_CLIENT_ID', 'test_client_id')
@patch('solana_bot_tournament.blog_publisher.BLOGGER_CLIENT_SECRET', 'test_client_secret') 
@patch('solana_bot_tournament.blog_publisher.BLOGGER_BLOG_ID', '123456789')
def test_blogger_markdown_to_html():
    publisher = BloggerPublisher()
    
    markdown = "# Header\n\n**bold** and *italic* text"
    html = publisher._markdown_to_html(markdown)
    
    assert "<h1>" in html
    assert "<strong>bold</strong>" in html
    assert "<em>italic</em>" in html


def test_multi_platform_publisher():
    publisher = MultiPlatformPublisher()
    
    # Test that all publisher types are included
    expected_platforms = {"medium", "devto", "hashnode", "blogger", "ghost"}
    assert set(publisher.publishers.keys()) == expected_platforms


@patch('solana_bot_tournament.blog_publisher.MEDIUM_ACCESS_TOKEN', 'test_token')
@patch('solana_bot_tournament.blog_publisher.DEVTO_API_KEY', 'test_key')
def test_multi_platform_get_configured():
    publisher = MultiPlatformPublisher()
    configured = publisher.get_configured_publishers()
    
    # Should include medium and devto based on our patches
    assert "medium" in configured
    assert "devto" in configured


def test_multi_platform_publish_no_configured():
    publisher = MultiPlatformPublisher()
    
    # Mock all publishers as not configured
    for pub in publisher.publishers.values():
        pub.is_configured = MagicMock(return_value=False)
    
    post = BlogPost("Test", "Content")
    results = publisher.publish_to_all(post)
    
    assert results == {}


@patch('solana_bot_tournament.blog_publisher.MEDIUM_ACCESS_TOKEN', 'test_token')
def test_multi_platform_publish_to_platform():
    publisher = MultiPlatformPublisher()
    
    # Mock medium publisher
    mock_result = {"success": True, "url": "https://medium.com/test", "id": "123"}
    publisher.publishers["medium"].publish = MagicMock(return_value=mock_result)
    
    post = BlogPost("Test", "Content")
    result = publisher.publish_to_platform(post, "medium")
    
    assert result == mock_result


def test_multi_platform_publish_unknown_platform():
    publisher = MultiPlatformPublisher()
    
    post = BlogPost("Test", "Content")
    result = publisher.publish_to_platform(post, "unknown")
    
    assert result["success"] is False
    assert "Unknown platform" in result["error"]


def test_get_blog_status():
    with patch('solana_bot_tournament.blog_publisher.MEDIUM_ACCESS_TOKEN', 'test_token'), \
         patch('solana_bot_tournament.blog_publisher.DEVTO_API_KEY', ''):
        
        status = get_blog_status()
        
        assert status["medium"] is True
        assert status["devto"] is False
        assert "hashnode" in status
        assert "blogger" in status
        assert "ghost" in status


def test_blog_post_default_values():
    post = BlogPost("Title", "Content")
    
    assert post.tags == []
    assert post.canonical_url is None
    assert post.published is True
    assert post.created_at is not None