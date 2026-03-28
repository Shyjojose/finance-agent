# Financial Guidance Agent with Session Memory

A Google ADK (Agent Development Kit) powered financial guidance chatbot with persistent session memory and real-time financial news integration. Built on AlloyDB for data persistence and Vertex AI for intelligent responses.

## 📋 Overview

This agent provides personalized financial guidance to users by:
- **Persistent Session Memory**: Saves user financial profiles to AlloyDB Data API
- **Intelligent Analysis**: Uses Gemini 2.5 Flash model for financial advice
- **Real-time News**: Integrates NewsAPI for current market insights
- **Secure Deployment**: Deployed on Google Cloud Run with secrets stored in Secret Manager

## ✨ Features

### 1. **Session Memory Management**
- Automatically loads user financial profiles from AlloyDB
- Saves and updates user financial information across sessions
- Stores: Annual income, monthly expenses, total debt, savings goals, investment horizon, risk tolerance
- JSONB data persistence with automatic timestamps

### 2. **Financial Tools**
- `get_user_financial_profile(user_id)` - Retrieve saved financial profile
- `save_user_financial_profile(user_id, ...)` - Save/update profile with new info
- `get_financial_news()` - Get latest market and finance news
- `get_stock_news(symbol)` - Get news for specific stocks (e.g., AAPL, GOOGL)
- `get_market_summary()` - Get top business headlines

### 3. **LLM-Powered Guidance**
- Personalized financial advice based on saved profile
- Step-by-step budgeting plans
- Debt payoff strategies
- Investment risk assessment
- Retirement planning recommendations

## 🏗️ Architecture

```
finance_agent/
├── agent.py                    # ADK Agent with tools
├── session_memory.py           # AlloyDB Data API integration
├── financial_news.py           # NewsAPI integration
├── requirements.txt            # Python dependencies
├── .env                        # Configuration (local dev)
└── __init__.py                 # Module entry point
```

### Technology Stack
- **Framework**: Google ADK v1.28.0
- **LLM**: Gemini 2.5 Flash (via Vertex AI)
- **Database**: Google Cloud AlloyDB PostgreSQL
- **News API**: NewsAPI.org (free tier)
- **Deployment**: Google Cloud Run
- **Secrets**: Google Cloud Secret Manager
- **Auth**: Google Application Default Credentials (ADC)

## 🚀 Deployment

### Production URL
```
https://finance-agent-1048149394600.us-central1.run.app
```

### Verify Agent is Live
```bash
curl https://finance-agent-1048149394600.us-central1.run.app/list-apps
# Response: ["finance_agent"]
```

## 🛠️ Local Development

### Prerequisites
- Python 3.13+
- Google Cloud SDK (`gcloud`)
- Active Google Cloud project (cohort-491613)
- ADK CLI v1.28.0+

### Setup

1. **Clone/Navigate to workspace:**
```bash
cd /Users/shyjojose/cohort/agent
```

2. **Create virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r finance_agent/requirements.txt
```

4. **Set environment variables:**
```bash
# Copy and customize .env
cp finance_agent/.env.example finance_agent/.env
# Edit finance_agent/.env with your credentials
```

5. **Run ADK Web locally:**
```bash
adk web
# Opens at http://localhost:8000
```

## 📝 Configuration

### Environment Variables

**AlloyDB Configuration:**
```env
ALLOYDB_PROJECT_ID=cohort-491613
ALLOYDB_LOCATION=us-central1
ALLOYDB_CLUSTER=free-trial-cluster
ALLOYDB_INSTANCE=primary
ALLOYDB_DATABASE=postgres
ALLOYDB_DB_USER=postgres
ALLOYDB_DB_PASSWORD=<secret stored in Secret Manager>
```

**Vertex AI Configuration:**
```env
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=cohort-491613
GOOGLE_CLOUD_LOCATION=us-central1
```

**API Keys (stored in Secret Manager):**
```env
NEWS_API_KEY=<secret stored in Secret Manager>
```

### Get News API Key
1. Go to https://newsapi.org/register
2. Sign up for free tier (100 requests/day)
3. Copy API key from dashboard
4. Add to Secret Manager or local `.env`

## 💾 Database Schema

### AlloyDB Table: `user_financial_profiles`

```sql
CREATE TABLE user_financial_profiles (
    user_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    annual_income INTEGER,
    monthly_expenses INTEGER,
    total_debt INTEGER,
    savings_goal TEXT,
    investment_horizon VARCHAR(255),
    risk_tolerance VARCHAR(255),
    profile_data JSONB,  -- Full profile as JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Query User Profile
```sql
SELECT * FROM user_financial_profiles WHERE user_id = 'user';
```

## 📊 Example Usage

### Save Financial Profile
```python
from finance_agent.agent import save_user_financial_profile

result = save_user_financial_profile(
    user_id="user",
    name="Financial User",
    annual_income=100000,
    monthly_expenses=5500,
    total_debt=308000,
    savings_goal="Emergency fund $33k, down payment for new home",
    investment_horizon="15 years",
    risk_tolerance="medium-high"
)
# Returns: {'status': 'ok', 'user_id': 'user', 'saved_fields': [...]}
```

### Retrieve Financial Profile
```python
from finance_agent.agent import get_user_financial_profile

profile = get_user_financial_profile("user")
# Returns: {'status': 'ok', 'user_id': 'user', 'profile': {...}}
```

### Get Financial News
```python
from finance_agent.agent import get_financial_news

news = get_financial_news()
# Returns: {'status': 'ok', 'count': 10, 'news': [...articles...]}
```

### Get Stock-Specific News
```python
from finance_agent.agent import get_stock_news

apple_news = get_stock_news("AAPL")
# Returns news articles about Apple Inc.
```

## 🔒 Security

### Production Deployment

#### Secret Manager Setup
Secrets are stored in Google Cloud Secret Manager:
- `alloydb-db-password` - AlloyDB credentials
- `news-api-key` - NewsAPI credentials

#### IAM Permissions
Cloud Run service account (`1048149394600-compute@developer.gserviceaccount.com`) has:
- `roles/secretmanager.secretAccessor` - Read secrets
- `roles/alloydb.databaseUser` - AlloyDB database access

#### Deployment Command (Secure)
```bash
adk deploy cloud_run \
  --project cohort-491613 \
  --region us-central1 \
  --service_name finance-agent \
  --with_ui finance_agent \
  -- --allow-unauthenticated \
  --set-env-vars=GOOGLE_GENAI_USE_VERTEXAI=1,GOOGLE_CLOUD_PROJECT=cohort-491613,... \
  --set-secrets=ALLOYDB_DB_PASSWORD=alloydb-db-password:latest,NEWS_API_KEY=news-api-key:latest
```

### Best Practices
1. **Never commit secrets** to version control
2. **Use Secret Manager** for production deployments (not env vars)
3. **Rotate credentials regularly** in Secret Manager
4. **Monitor Cloud Run logs** for unauthorized access attempts
5. **Restrict IAM permissions** to minimal required roles

## 🧪 Testing

### Local Development
```bash
cd /Users/shyjojose/cohort/agent
source .venv/bin/activate
set -a && source finance_agent/.env && set +a

# Test session memory
python - <<'PY'
from finance_agent.agent import (
    save_user_financial_profile,
    get_user_financial_profile
)

# Save profile
result = save_user_financial_profile(
    user_id="test_user",
    name="Test User",
    annual_income=80000,
    monthly_expenses=4500,
    total_debt=50000,
    savings_goal="Save $20k",
    investment_horizon="10 years",
    risk_tolerance="medium"
)
print("Save:", result)

# Retrieve profile
profile = get_user_financial_profile("test_user")
print("Retrieve:", profile)
PY
```

### Test Financial News
```bash
python - <<'PY'
from finance_agent.agent import (
    get_financial_news,
    get_stock_news,
    get_market_summary
)

print("Financial News:", get_financial_news())
print("Apple News:", get_stock_news("AAPL"))
print("Market Summary:", get_market_summary())
PY
```

### Cloud Run Endpoint Test
```bash
# Check if agent is discoverable
curl https://finance-agent-1048149394600.us-central1.run.app/list-apps

# Expected: ["finance_agent"]
```

## 📁 Project Structure

```
/Users/shyjojose/cohort/agent/
├── finance_agent/
│   ├── agent.py              # ADK Agent definition with 5 tools
│   ├── session_memory.py     # AlloyDB Data API client (HTTP-based)
│   ├── financial_news.py     # NewsAPI integration
│   ├── requirements.txt       # Dependencies
│   ├── .env                  # Local config (excluded from git)
│   └── __init__.py           # Package init
├── README.md                 # This file
└── .adk/                     # ADK configuration (auto-generated)
```

## 📦 Dependencies

```
google-auth[requests]>=2.47.0,<3.0.0   # Google Cloud authentication
requests==2.32.4                        # HTTP client for Data API
```

## 🔄 Workflow

### User Conversation Flow
1. User opens agent at: http://localhost:8000 or cloud-run-url
2. Agent calls `get_user_financial_profile()` to load saved data
3. Agent provides personalized recommendations based on profile
4. User shares new financial information
5. Agent calls `save_user_financial_profile()` to persist updates
6. Agent fetches real-time news via `get_financial_news()` or `get_stock_news()`
7. Next session: profile is automatically loaded

### Deployment Flow
1. Code changes committed to local git
2. Run: `adk deploy cloud_run --project cohort-491613 --region us-central1 ...`
3. ADK builds container and deploys to Cloud Run
4. Secrets auto-injected from Secret Manager at runtime
5. Agent available at: https://finance-agent-1048149394600.us-central1.run.app

## 🐛 Troubleshooting

### AlloyDB Connection Error
```
Failed to fetch profile: Failed to connect to AlloyDB
```
**Solution:**
- Verify ALLOYDB_* env vars are set correctly
- Check AlloyDB Data API is enabled: `gcloud alloydb instances describe primary --cluster free-trial-cluster --region us-central1 --format="value(dataApiAccess)"`
- Confirm IAM permissions: Service account must have `alloydb.databaseUser` role

### News API Returns Error
```
status: "error", message: "NewsAPI error"
```
**Solution:**
- Verify NEWS_API_KEY is set and valid
- Check API quota at https://newsapi.org/account
- Ensure internet connectivity to newsapi.org

### Agent Not Discoverable in ADK Web
```
list-apps returns: []
```
**Solution:**
- Verify agent folder structure: `finance_agent/agent.py` exists
- Restart ADK Web: `adk web`
- Check logs for import errors in `finance_agent/agent.py`

## 📖 Documentation Links

- [Google ADK Documentation](https://cloud.google.com/docs/adk)
- [AlloyDB Data API](https://cloud.google.com/alloydb/docs/api)
- [NewsAPI](https://newsapi.org/docs)
- [Google Cloud Run](https://cloud.google.com/run/docs)
- [Secret Manager](https://cloud.google.com/secret-manager/docs)

## 📊 Agent Tools Summary

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `get_user_financial_profile` | Load saved profile | `user_id` (default: "user") | Profile dict or error |
| `save_user_financial_profile` | Save/update profile | `user_id`, financial fields | Status and saved fields |
| `get_financial_news` | Market news | None | 10 latest finance articles |
| `get_stock_news` | Stock news | `symbol` (e.g., "AAPL") | Articles about stock |
| `get_market_summary` | Top headlines | None | Top 10 business headlines |

## 🎯 Next Steps

1. **Test locally**: Run `adk web` and chat with the agent
2. **Add more users**: Use different `user_id` values for multiple profiles
3. **Customize instructions**: Edit agent instruction in `agent.py` for different financial advice style
4. **Monitor production**: Check Cloud Run logs and metrics
5. **Rotate secrets**: Update credentials in Secret Manager monthly

## 🚧 Further Development Roadmap

### Phase 1: Reliability and Security
1. Add structured request logging with correlation IDs for each user session.
2. Enforce per-user authorization so profile access is tied to authenticated identity instead of default IDs.
3. Add rate-limiting and retry/backoff guards for NewsAPI and AlloyDB Data API calls.
4. Move local development secrets to `.env.example` placeholders and enforce secret scanning in CI.

### Phase 2: Better Financial Intelligence
1. Split debts into detailed fields (mortgage, student loan, auto loan, APR, minimum payment).
2. Add cash-flow analysis tools to calculate savings rate, debt-to-income ratio, and emergency fund runway.
3. Add scenario simulation tools ("pay debt first" vs "invest first") with monthly projections.
4. Introduce goal progress tracking with milestone alerts (emergency fund %, target date variance).

### Phase 3: Memory and Data Model Enhancements
1. Version user profile updates and keep a history table for auditability.
2. Add conversation summaries per session to improve long-running context recall.
3. Store periodic financial snapshots (monthly) for trend analysis and charts.
4. Normalize schema into profile, liabilities, goals, and preferences tables for cleaner queries.

### Phase 4: News and Market Insights
1. Add source diversification (e.g., Alpha Vantage, FMP, Finnhub) with fallback when one API fails.
2. Add ticker/entity extraction from user prompts and auto-fetch related headlines.
3. Add sentiment and relevance scoring so only actionable news is shown.
4. Add daily/weekly digest generation aligned with each user’s portfolio interests.

### Phase 5: Product and UX Improvements
1. Add onboarding flow to collect missing profile fields with guided prompts.
2. Add downloadable financial plan summaries (PDF/markdown).
3. Add notification hooks (email/Slack) for goal milestones and major market events.
4. Add multi-language response support and locale-aware financial examples.

### Phase 6: Testing and Operations
1. Add unit tests for `session_memory.py`, `financial_news.py`, and tool wrappers in `agent.py`.
2. Add integration tests for AlloyDB Data API save/load flows and Cloud Run smoke tests.
3. Add CI/CD pipeline with linting, type checks, and deployment gates.
4. Add dashboards for latency, tool usage frequency, error rates, and token consumption.

### Suggested Immediate Priorities
1. Implement authenticated user IDs (highest impact for safe multi-user production).
2. Add debt breakdown schema and derived metrics (core advice quality improvement).
3. Add automated tests and CI before larger feature expansion.

## 📝 Example Test Data

Your current saved profile (user_id: "user"):
- **Name**: Financial User
- **Annual Income**: $100,000
- **Monthly Expenses**: $5,500
- **Total Debt**: $308,000 (Mortgage: $285k, Student: $15k, Auto: $8k)
- **Savings Goal**: Emergency fund $33k, down payment for new home, retirement at 65 with 80% income replacement
- **Investment Horizon**: 15 years
- **Risk Tolerance**: Medium-high
- **Last Updated**: 2026-03-28 18:18:55 UTC

## 🤝 Support

For issues or questions:
1. Check Cloud Run logs: `gcloud run logs read finance-agent --region us-central1 --limit 50`
2. Review agent output in ADK Web UI
3. Test endpoints locally before deploying
4. Verify Secret Manager secrets are accessible

## 📄 License

Internal project for cohort-491613.

---

**Deployment Status**: ✅ Live on Cloud Run  
**Service URL**: https://finance-agent-1048149394600.us-central1.run.app  
**Last Updated**: March 28, 2026
