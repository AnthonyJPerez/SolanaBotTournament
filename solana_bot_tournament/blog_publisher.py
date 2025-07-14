"""Blog publishing module for multiple platforms."""
from __future__ import annotations
import logging
import json
import hashlib
import hmac
import time
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

import requests

from .config import (
    MEDIUM_ACCESS_TOKEN, DEVTO_API_KEY, HASHNODE_ACCESS_TOKEN, HASHNODE_PUBLICATION_ID,
    BLOGGER_CLIENT_ID, BLOGGER_CLIENT_SECRET, BLOGGER_BLOG_ID,
    GHOST_API_URL, GHOST_ADMIN_API_KEY
)


class BlogPost:
    """Represents a blog post to be published."""
    
    def __init__(self, title: str, content: str, tags: List[str] = None, 
                 canonical_url: str = None, published: bool = True):
        self.title = title
        self.content = content
        self.tags = tags or []
        self.canonical_url = canonical_url
        self.published = published
        self.created_at = datetime.now()


class BlogPublisher:
    """Base class for blog publishing."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "SolanaBotTournament/1.0"})
    
    def publish(self, post: BlogPost) -> Dict[str, any]:
        """Publish a blog post. Override in subclasses."""
        raise NotImplementedError
    
    def is_configured(self) -> bool:
        """Check if the publisher is properly configured."""
        raise NotImplementedError


class MediumPublisher(BlogPublisher):
    """Publisher for Medium.com"""
    
    def __init__(self):
        super().__init__()
        self.access_token = MEDIUM_ACCESS_TOKEN
        self.base_url = "https://api.medium.com/v1"
        
        if self.access_token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            })
    
    def is_configured(self) -> bool:
        return bool(self.access_token)
    
    def publish(self, post: BlogPost) -> Dict[str, any]:
        """Publish to Medium."""
        if not self.is_configured():
            return {"success": False, "error": "Medium not configured"}
        
        try:
            # Get user ID first
            user_response = self.session.get(f"{self.base_url}/me")
            user_response.raise_for_status()
            user_id = user_response.json()["data"]["id"]
            
            # Prepare post data
            post_data = {
                "title": post.title,
                "contentFormat": "markdown",
                "content": post.content,
                "tags": post.tags[:5],  # Medium allows max 5 tags
                "publishStatus": "public" if post.published else "draft"
            }
            
            if post.canonical_url:
                post_data["canonicalUrl"] = post.canonical_url
            
            # Publish post
            response = self.session.post(
                f"{self.base_url}/users/{user_id}/posts",
                json=post_data
            )
            response.raise_for_status()
            
            result = response.json()
            return {
                "success": True,
                "url": result["data"]["url"],
                "id": result["data"]["id"],
                "platform": "Medium"
            }
            
        except Exception as e:
            logging.error(f"Failed to publish to Medium: {e}")
            return {"success": False, "error": str(e), "platform": "Medium"}


class DevToPublisher(BlogPublisher):
    """Publisher for Dev.to"""
    
    def __init__(self):
        super().__init__()
        self.api_key = DEVTO_API_KEY
        self.base_url = "https://dev.to/api"
        
        if self.api_key:
            self.session.headers.update({
                "api-key": self.api_key,
                "Content-Type": "application/json"
            })
    
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    def publish(self, post: BlogPost) -> Dict[str, any]:
        """Publish to Dev.to"""
        if not self.is_configured():
            return {"success": False, "error": "Dev.to not configured"}
        
        try:
            post_data = {
                "article": {
                    "title": post.title,
                    "body_markdown": post.content,
                    "published": post.published,
                    "tags": post.tags[:4]  # Dev.to allows max 4 tags
                }
            }
            
            if post.canonical_url:
                post_data["article"]["canonical_url"] = post.canonical_url
            
            response = self.session.post(f"{self.base_url}/articles", json=post_data)
            response.raise_for_status()
            
            result = response.json()
            return {
                "success": True,
                "url": result["url"],
                "id": result["id"],
                "platform": "Dev.to"
            }
            
        except Exception as e:
            logging.error(f"Failed to publish to Dev.to: {e}")
            return {"success": False, "error": str(e), "platform": "Dev.to"}


class HashnodePublisher(BlogPublisher):
    """Publisher for Hashnode"""
    
    def __init__(self):
        super().__init__()
        self.access_token = HASHNODE_ACCESS_TOKEN
        self.publication_id = HASHNODE_PUBLICATION_ID
        self.base_url = "https://gql.hashnode.com"
        
        if self.access_token:
            self.session.headers.update({
                "Authorization": self.access_token,
                "Content-Type": "application/json"
            })
    
    def is_configured(self) -> bool:
        return bool(self.access_token and self.publication_id)
    
    def publish(self, post: BlogPost) -> Dict[str, any]:
        """Publish to Hashnode using GraphQL API"""
        if not self.is_configured():
            return {"success": False, "error": "Hashnode not configured"}
        
        try:
            # GraphQL mutation for publishing
            mutation = """
            mutation PublishPost($input: PublishPostInput!) {
                publishPost(input: $input) {
                    post {
                        id
                        url
                        title
                    }
                }
            }
            """
            
            variables = {
                "input": {
                    "title": post.title,
                    "contentMarkdown": post.content,
                    "tags": [{"slug": tag.lower().replace(" ", "-")} for tag in post.tags[:5]],
                    "publicationId": self.publication_id,
                    "publishedAt": post.created_at.isoformat() if post.published else None
                }
            }
            
            if post.canonical_url:
                variables["input"]["originalArticleURL"] = post.canonical_url
            
            response = self.session.post(
                self.base_url,
                json={"query": mutation, "variables": variables}
            )
            response.raise_for_status()
            
            result = response.json()
            if "errors" in result:
                raise Exception(f"GraphQL errors: {result['errors']}")
            
            post_data = result["data"]["publishPost"]["post"]
            return {
                "success": True,
                "url": post_data["url"],
                "id": post_data["id"],
                "platform": "Hashnode"
            }
            
        except Exception as e:
            logging.error(f"Failed to publish to Hashnode: {e}")
            return {"success": False, "error": str(e), "platform": "Hashnode"}


class BloggerPublisher(BlogPublisher):
    """Publisher for Google Blogger using OAuth 2.0"""
    
    def __init__(self):
        super().__init__()
        self.client_id = BLOGGER_CLIENT_ID
        self.client_secret = BLOGGER_CLIENT_SECRET
        self.blog_id = BLOGGER_BLOG_ID
        self.base_url = "https://www.googleapis.com/blogger/v3"
        self.oauth_url = "https://accounts.google.com/o/oauth2"
        self.scope = "https://www.googleapis.com/auth/blogger"
        self._access_token = None
        
    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret and self.blog_id)
    
    def _get_access_token(self) -> Optional[str]:
        """Get access token dynamically using OAuth flow."""
        if self._access_token:
            return self._access_token
            
        # Check for existing token file
        token_file = Path("blogger_token.txt")
        if token_file.exists():
            try:
                with open(token_file, 'r') as f:
                    token_data = f.read().strip()
                    # Validate token by making a test API call
                    if token_data and len(token_data) > 20:
                        if self._validate_token(token_data):
                            self._access_token = token_data
                            return self._access_token
                        else:
                            logging.info("Existing Blogger token is invalid or expired")
                            # Remove invalid token file
                            token_file.unlink()
            except Exception as e:
                logging.warning(f"Error reading token file: {e}")
        
        # No valid token found - initiate OAuth flow
        logging.info("No valid Blogger token found. Initiating OAuth flow...")
        return self._initiate_oauth_flow()
    
    def _initiate_oauth_flow(self) -> Optional[str]:
        """Initiate OAuth flow to get access token."""
        try:
            redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
            auth_url = self.get_authorization_url(redirect_uri)
            
            print("\n" + "="*60)
            print("BLOGGER OAUTH AUTHORIZATION REQUIRED")
            print("="*60)
            print("To publish to Blogger, please complete this one-time setup:")
            print()
            print("1. Open this URL in your browser:")
            print(f"   {auth_url}")
            print()
            print("2. Sign in to your Google account and click 'Allow'")
            print("3. Copy the authorization code from the page")
            print()
            
            # Get authorization code from user
            code = input("Enter the authorization code: ").strip()
            
            if not code:
                logging.error("No authorization code provided")
                return None
            
            # Exchange code for token
            result = self.exchange_code_for_token(code, redirect_uri)
            
            if result["success"]:
                token = result["token"]["access_token"]
                
                # Save token for future use
                token_file = Path("blogger_token.txt")
                with open(token_file, 'w') as f:
                    f.write(token)
                
                print("\n[OK] Blogger authorization successful!")
                print("Token saved for future use.")
                self._access_token = token
                return token
            else:
                logging.error(f"Failed to exchange code for token: {result['error']}")
                return None
                
        except KeyboardInterrupt:
            print("\n[INFO] OAuth flow cancelled by user")
            return None
        except Exception as e:
            logging.error(f"Error in OAuth flow: {e}")
            return None
    
    def _validate_token(self, token: str) -> bool:
        """Validate access token by making a test API call."""
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Make a simple API call to validate the token
            response = self.session.get(
                f"{self.base_url}/blogs/{self.blog_id}",
                headers=headers,
                timeout=10
            )
            
            # Token is valid if we get a successful response
            return response.status_code == 200
            
        except Exception as e:
            logging.debug(f"Token validation failed: {e}")
            return False
    
    def publish(self, post: BlogPost) -> Dict[str, any]:
        """Publish to Blogger"""
        if not self.is_configured():
            return {"success": False, "error": "Blogger OAuth not configured"}
        
        # Get access token
        access_token = self._get_access_token()
        if not access_token:
            return {
                "success": False, 
                "error": "Blogger access token not available. Please complete OAuth flow.",
                "platform": "Blogger"
            }
        
        try:
            # Set authorization header
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Convert markdown to HTML for Blogger
            content_html = self._markdown_to_html(post.content)
            
            post_data = {
                "title": post.title,
                "content": content_html,
                "labels": post.tags
            }
            
            # Create the post
            response = self.session.post(
                f"{self.base_url}/blogs/{self.blog_id}/posts",
                json=post_data,
                headers=headers
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Publish the post if it should be published
            if post.published:
                publish_response = self.session.post(
                    f"{self.base_url}/blogs/{self.blog_id}/posts/{result['id']}/publish",
                    headers=headers
                )
                publish_response.raise_for_status()
                result = publish_response.json()
            
            return {
                "success": True,
                "url": result["url"],
                "id": result["id"],
                "platform": "Blogger"
            }
            
        except Exception as e:
            logging.error(f"Failed to publish to Blogger: {e}")
            return {"success": False, "error": str(e), "platform": "Blogger"}
    
    def _markdown_to_html(self, markdown_content: str) -> str:
        """Convert markdown to HTML for Blogger."""
        # Simple markdown to HTML conversion
        html = markdown_content
        
        # Convert headers
        html = html.replace('# ', '<h1>').replace('\n', '</h1>\n', 1) if '# ' in html else html
        html = html.replace('## ', '<h2>').replace('\n', '</h2>\n', 1) if '## ' in html else html
        html = html.replace('### ', '<h3>').replace('\n', '</h3>\n', 1) if '### ' in html else html
        
        # Convert bold and italic
        import re
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # Convert line breaks to paragraphs
        paragraphs = html.split('\n\n')
        html = ''.join(f'<p>{p}</p>' for p in paragraphs if p.strip())
        
        return html
    
    def get_authorization_url(self, redirect_uri: str = "urn:ietf:wg:oauth:2.0:oob") -> str:
        """Generate OAuth authorization URL."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": self.scope,
            "access_type": "offline"
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.oauth_url}/auth?{query_string}"
    
    def exchange_code_for_token(self, code: str, redirect_uri: str = "urn:ietf:wg:oauth:2.0:oob") -> Dict:
        """Exchange authorization code for access token."""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        
        try:
            response = requests.post(f"{self.oauth_url}/token", data=data)
            response.raise_for_status()
            token_data = response.json()
            
            # Save token to file for future use
            token_file = Path("blogger_token.txt")
            with open(token_file, 'w') as f:
                f.write(token_data["access_token"])
            
            self._access_token = token_data["access_token"]
            return {"success": True, "token": token_data}
            
        except Exception as e:
            logging.error(f"Failed to exchange code for token: {e}")
            return {"success": False, "error": str(e)}


class GhostPublisher(BlogPublisher):
    """Publisher for Ghost CMS"""
    
    def __init__(self):
        super().__init__()
        self.api_url = GHOST_API_URL
        self.admin_api_key = GHOST_ADMIN_API_KEY
        
        if self.api_url and self.admin_api_key:
            # Parse the admin API key
            id_key = self.admin_api_key.split(':')
            if len(id_key) == 2:
                self.key_id, self.secret = id_key
            else:
                self.key_id = self.secret = None
    
    def is_configured(self) -> bool:
        return bool(self.api_url and self.admin_api_key and 
                   hasattr(self, 'key_id') and self.key_id)
    
    def _generate_jwt_token(self) -> str:
        """Generate JWT token for Ghost Admin API"""
        import jwt
        
        iat = int(time.time())
        header = {"alg": "HS256", "typ": "JWT", "kid": self.key_id}
        payload = {
            "iat": iat,
            "exp": iat + 5 * 60,  # 5 minutes
            "aud": "/admin/"
        }
        
        return jwt.encode(payload, bytes.fromhex(self.secret), algorithm="HS256", headers=header)
    
    def publish(self, post: BlogPost) -> Dict[str, any]:
        """Publish to Ghost"""
        if not self.is_configured():
            return {"success": False, "error": "Ghost not configured"}
        
        try:
            # Generate JWT token
            token = self._generate_jwt_token()
            
            headers = {
                "Authorization": f"Ghost {token}",
                "Content-Type": "application/json"
            }
            
            post_data = {
                "posts": [{
                    "title": post.title,
                    "markdown": post.content,
                    "status": "published" if post.published else "draft",
                    "tags": [{"name": tag} for tag in post.tags]
                }]
            }
            
            response = self.session.post(
                f"{self.api_url}/ghost/api/admin/posts/",
                json=post_data,
                headers=headers
            )
            response.raise_for_status()
            
            result = response.json()
            post_result = result["posts"][0]
            
            return {
                "success": True,
                "url": post_result["url"],
                "id": post_result["id"],
                "platform": "Ghost"
            }
            
        except Exception as e:
            logging.error(f"Failed to publish to Ghost: {e}")
            return {"success": False, "error": str(e), "platform": "Ghost"}


class MultiPlatformPublisher:
    """Publishes to multiple blog platforms simultaneously."""
    
    def __init__(self):
        self.publishers = {
            "medium": MediumPublisher(),
            "devto": DevToPublisher(),
            "hashnode": HashnodePublisher(),
            "blogger": BloggerPublisher(),
            "ghost": GhostPublisher()
        }
    
    def get_configured_publishers(self) -> List[str]:
        """Get list of configured publishers."""
        return [name for name, pub in self.publishers.items() if pub.is_configured()]
    
    def publish_to_all(self, post: BlogPost) -> Dict[str, Dict]:
        """Publish to all configured platforms."""
        results = {}
        configured = self.get_configured_publishers()
        
        if not configured:
            logging.warning("No blog platforms configured")
            return {}
        
        logging.info(f"Publishing to {len(configured)} platforms: {', '.join(configured)}")
        
        for platform_name in configured:
            try:
                publisher = self.publishers[platform_name]
                result = publisher.publish(post)
                results[platform_name] = result
                
                if result["success"]:
                    logging.info(f"[OK] Published to {platform_name}: {result['url']}")
                else:
                    logging.error(f"[FAIL] Failed to publish to {platform_name}: {result['error']}")
                    
            except Exception as e:
                logging.error(f"[ERROR] Error publishing to {platform_name}: {e}")
                results[platform_name] = {"success": False, "error": str(e)}
        
        return results
    
    def publish_to_platform(self, post: BlogPost, platform: str) -> Dict:
        """Publish to a specific platform."""
        if platform not in self.publishers:
            return {"success": False, "error": f"Unknown platform: {platform}"}
        
        publisher = self.publishers[platform]
        if not publisher.is_configured():
            return {"success": False, "error": f"{platform} not configured"}
        
        return publisher.publish(post)


def publish_blog_post(title: str, content: str, tags: List[str] = None) -> Dict[str, Dict]:
    """Convenience function to publish a blog post to all configured platforms."""
    post = BlogPost(title=title, content=content, tags=tags or [])
    publisher = MultiPlatformPublisher()
    return publisher.publish_to_all(post)


def get_blog_status() -> Dict[str, bool]:
    """Get status of all blog platform configurations."""
    publisher = MultiPlatformPublisher()
    return {name: pub.is_configured() for name, pub in publisher.publishers.items()}