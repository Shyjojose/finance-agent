from __future__ import annotations

from typing import Any

from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool

from .session_memory import SessionMemoryManager
from .financial_news import FinancialNewsProvider


_memory_manager: SessionMemoryManager | None = None


def _get_memory_manager() -> SessionMemoryManager:
	global _memory_manager
	if _memory_manager is None:
		_memory_manager = SessionMemoryManager()
	return _memory_manager


_news_provider: FinancialNewsProvider | None = None


def _get_news_provider() -> FinancialNewsProvider:
	global _news_provider
	if _news_provider is None:
		_news_provider = FinancialNewsProvider()
	return _news_provider


def get_user_financial_profile(user_id: str = "user") -> dict[str, Any]:
	"""Load a user's saved financial profile from AlloyDB Data API.

	Args:
		user_id: Stable user identifier. Use the same id across sessions.

	Returns:
		A dictionary with status and profile data.
	"""
	try:
		profile = _get_memory_manager().get_user_profile(user_id)
		if profile is None:
			return {
				"status": "not_found",
				"user_id": user_id,
				"message": "No saved financial profile found for this user.",
			}
		return {
			"status": "ok",
			"user_id": user_id,
			"profile": profile,
		}
	except Exception as exc:
		return {
			"status": "error",
			"user_id": user_id,
			"message": f"Failed to load profile: {exc}",
		}


def save_user_financial_profile(
	user_id: str = "user",
	name: str | None = None,
	annual_income: int | None = None,
	monthly_expenses: int | None = None,
	total_debt: int | None = None,
	savings_goal: str | None = None,
	investment_horizon: str | None = None,
	risk_tolerance: str | None = None,
) -> dict[str, Any]:
	"""Save or update a user's financial profile in AlloyDB Data API.

	Only provided fields are updated.
	"""
	profile_data = {
		"name": name,
		"annual_income": annual_income,
		"monthly_expenses": monthly_expenses,
		"total_debt": total_debt,
		"savings_goal": savings_goal,
		"investment_horizon": investment_horizon,
		"risk_tolerance": risk_tolerance,
	}
	profile_data = {k: v for k, v in profile_data.items() if v is not None}

	if not profile_data:
		return {
			"status": "noop",
			"user_id": user_id,
			"message": "No profile fields supplied to save.",
		}

	try:
		manager = _get_memory_manager()
		existing = manager.get_user_profile(user_id) or {}

		merged = {
			"name": existing.get("name"),
			"annual_income": existing.get("annual_income"),
			"monthly_expenses": existing.get("monthly_expenses"),
			"total_debt": existing.get("total_debt"),
			"savings_goal": existing.get("savings_goal"),
			"investment_horizon": existing.get("investment_horizon"),
			"risk_tolerance": existing.get("risk_tolerance"),
		}
		merged.update(profile_data)

		manager.save_user_profile(user_id, merged)
		return {
			"status": "ok",
			"user_id": user_id,
			"saved_fields": sorted(profile_data.keys()),
		}
	except Exception as exc:
		return {
			"status": "error",
			"user_id": user_id,
			"message": f"Failed to save profile: {exc}",
		}


def get_financial_news() -> dict[str, Any]:
	"""Get latest financial and market news headlines.

	Returns:
		Dictionary with recent financial news articles.
	"""
	try:
		return _get_news_provider().get_financial_news()
	except Exception as exc:
		return {
			"status": "error",
			"message": f"Failed to fetch financial news: {exc}",
		}


def get_stock_news(symbol: str) -> dict[str, Any]:
	"""Get recent news articles for a specific stock symbol.

	Args:
		symbol: Stock ticker symbol (e.g., AAPL, GOOGL, MSFT, TSLA)

	Returns:
		Dictionary with news articles about the stock.
	"""
	if not symbol:
		return {
			"status": "error",
			"message": "Stock symbol is required (e.g., AAPL, GOOGL)",
		}

	try:
		return _get_news_provider().get_stock_news(symbol.upper())
	except Exception as exc:
		return {
			"status": "error",
			"message": f"Failed to fetch news for {symbol}: {exc}",
		}


def get_market_summary() -> dict[str, Any]:
	"""Get today's top business and market headlines.

	Returns:
		Dictionary with top market headlines.
	"""
	try:
		return _get_news_provider().get_market_summary()
	except Exception as exc:
		return {
			"status": "error",
			"message": f"Failed to fetch market summary: {exc}",
		}

# Agent with persistent session memory and financial news access
root_agent = Agent(
	model="gemini-2.5-flash",
	name="chat_agent",
	description="A financial guidance assistant with persistent session memory for budgeting, saving, and investing education.",
	instruction=(
		"You are a financial guidance assistant with persistent memory and real-time financial news access. "
		"Give clear, practical, and conservative financial advice for personal finance topics such as budgeting, "
		"debt payoff, emergency funds, credit building, retirement planning, and long-term investing basics. "
		"IMPORTANT - Session Memory Tools: Use get_user_financial_profile at the beginning of a conversation "
		"to load user context (default user_id is 'user' unless the user gives another stable id). "
		"When the user shares new or corrected profile facts, call save_user_financial_profile so future sessions "
		"can reuse them. Acknowledge key remembered context in your response. "
		"FINANCIAL NEWS TOOLS: Use get_financial_news() to provide current market insights. "
		"Use get_stock_news(symbol) when user mentions specific stocks or tickers. "
		"Use get_market_summary() for high-level market trends. Reference news when giving investment advice. "
		"Ask follow-up questions before giving recommendations: income range, monthly expenses, debt, "
		"timeline, financial goals, and risk tolerance. "
		"When useful, provide step-by-step plans, simple formulas, and example allocations, and "
		"explain trade-offs in plain language. "
		"Do not provide legal or tax advice. For complex, high-stakes, or jurisdiction-specific "
		"situations, recommend consulting a licensed financial professional. "
		"Never guarantee returns and always mention investment risk."
	),
	tools=[
		FunctionTool(get_user_financial_profile),
		FunctionTool(save_user_financial_profile),
		FunctionTool(get_financial_news),
		FunctionTool(get_stock_news),
		FunctionTool(get_market_summary),
	],
)
