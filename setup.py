from setuptools import setup, find_packages

setup(
    name="solana-bot-tournament",
    version="0.1.0",
    description="Automated Solana trading‑bot tournament with analytics, blog, Twitter & Streamlit dashboard",
    author="<Your Name>",
    author_email="<you@example.com>",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.32",
        "matplotlib>=3.9",
        "pandas>=2.2",
        "streamlit>=1.35",
        "tweepy>=4.14",
        "jinja2>=3.1",
        "pytest>=8.2",
        "PyJWT>=2.8.0",  # For Ghost blog publishing
    ],
    entry_points={
        "console_scripts": [
            "solana-bot=solana_bot_tournament.cli:main",
        ],
    },
    keywords=["solana", "trading", "bot", "helius", "streamlit"],
)