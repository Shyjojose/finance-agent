"""Financial news provider using NewsAPI."""

import os
import requests
from typing import Any


class FinancialNewsProvider:
    """Fetch financial news from NewsAPI."""

    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY", "")
        self.base_url = "https://newsapi.org/v2"

    def get_financial_news(self, category: str = "business") -> dict[str, Any]:
        """Fetch latest financial and business news.

        Args:
            category: News category (business, finance, technology, etc.)

        Returns:
            Dictionary with news articles and metadata.
        """
        if not self.api_key:
            return {
                "status": "error",
                "message": "NEWS_API_KEY not configured. Get a free key from https://newsapi.org",
            }

        try:
            url = f"{self.base_url}/everything"
            params = {
                "q": "finance OR stock market OR economy OR investing",
                "sortBy": "publishedAt",
                "language": "en",
                "apiKey": self.api_key,
                "pageSize": 10,
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "error":
                return {
                    "status": "error",
                    "message": data.get("message", "NewsAPI error"),
                }

            articles = data.get("articles", [])
            return {
                "status": "ok",
                "count": len(articles),
                "news": [
                    {
                        "title": a.get("title"),
                        "source": a.get("source", {}).get("name"),
                        "published": a.get("publishedAt"),
                        "description": a.get("description"),
                        "url": a.get("url"),
                    }
                    for a in articles
                ],
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Failed to fetch news: {str(e)}",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing news: {str(e)}",
            }

    def get_stock_news(self, symbol: str) -> dict[str, Any]:
        """Get news for a specific stock symbol.

        Args:
            symbol: Stock ticker symbol (e.g., AAPL, GOOGL, MSFT)

        Returns:
            Dictionary with articles about the stock.
        """
        if not self.api_key:
            return {
                "status": "error",
                "message": "NEWS_API_KEY not configured. Get a free key from https://newsapi.org",
            }

        try:
            url = f"{self.base_url}/everything"
            params = {
                "q": symbol,
                "sortBy": "publishedAt",
                "language": "en",
                "apiKey": self.api_key,
                "pageSize": 10,
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "error":
                return {
                    "status": "error",
                    "message": data.get("message", "NewsAPI error"),
                }

            articles = data.get("articles", [])
            return {
                "status": "ok",
                "symbol": symbol,
                "count": len(articles),
                "news": [
                    {
                        "title": a.get("title"),
                        "source": a.get("source", {}).get("name"),
                        "published": a.get("publishedAt"),
                        "description": a.get("description"),
                        "url": a.get("url"),
                    }
                    for a in articles
                ],
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Failed to fetch news for {symbol}: {str(e)}",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing news: {str(e)}",
            }

    def get_market_summary(self) -> dict[str, Any]:
        """Get market-related news headlines.

        Returns:
            Dictionary with top market headlines.
        """
        if not self.api_key:
            return {
                "status": "error",
                "message": "NEWS_API_KEY not configured. Get a free key from https://newsapi.org",
            }

        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                "category": "business",
                "apiKey": self.api_key,
                "pageSize": 10,
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "error":
                return {
                    "status": "error",
                    "message": data.get("message", "NewsAPI error"),
                }

            articles = data.get("articles", [])
            return {
                "status": "ok",
                "category": "market_summary",
                "count": len(articles),
                "headlines": [
                    {
                        "title": a.get("title"),
                        "source": a.get("source", {}).get("name"),
                        "published": a.get("publishedAt"),
                        "url": a.get("url"),
                    }
                    for a in articles
                ],
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Failed to fetch market summary: {str(e)}",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing market data: {str(e)}",
            }
