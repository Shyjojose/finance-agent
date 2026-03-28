import json
import os
from typing import Any
from urllib.parse import urlparse

import google.auth
from google.auth.transport.requests import Request
import requests
from datetime import datetime

class SessionMemoryManager:
    """Manages user financial profile persistence via AlloyDB Data API."""

    def __init__(self, db_uri: str | None = None):
        project = os.getenv("ALLOYDB_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("ALLOYDB_LOCATION") or os.getenv("GOOGLE_CLOUD_LOCATION")
        cluster = os.getenv("ALLOYDB_CLUSTER")
        instance = os.getenv("ALLOYDB_INSTANCE")

        if not all([project, location, cluster, instance]):
            raise ValueError(
                "Missing AlloyDB Data API settings. Required: ALLOYDB_PROJECT_ID, "
                "ALLOYDB_LOCATION, ALLOYDB_CLUSTER, ALLOYDB_INSTANCE"
            )

        self.database = os.getenv("ALLOYDB_DATABASE", "postgres")
        self.db_user = os.getenv("ALLOYDB_DB_USER", "postgres")
        self.db_password = os.getenv("ALLOYDB_DB_PASSWORD")

        if not self.db_password and db_uri:
            parsed = urlparse(db_uri)
            self.db_password = parsed.password
            if parsed.username:
                self.db_user = parsed.username
            if parsed.path and parsed.path != "/":
                self.database = parsed.path.lstrip("/")

        if not self.db_password:
            uri = os.getenv("DATABASE_URL")
            if uri:
                parsed = urlparse(uri)
                self.db_password = parsed.password
                if parsed.username:
                    self.db_user = parsed.username
                if parsed.path and parsed.path != "/":
                    self.database = parsed.path.lstrip("/")

        if not self.db_password:
            raise ValueError("Missing DB password. Set ALLOYDB_DB_PASSWORD or DATABASE_URL")

        self.endpoint = (
            "https://alloydb.googleapis.com/v1beta/"
            f"projects/{project}/locations/{location}/clusters/{cluster}/instances/{instance}:executeSql"
        )

        self._ensure_table()

    def _get_access_token(self) -> str:
        credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        credentials.refresh(Request())
        return credentials.token

    def _execute_sql(self, sql_statement: str) -> dict[str, Any]:
        token = self._get_access_token()
        payload = {
            "database": self.database,
            "user": self.db_user,
            "password": self.db_password,
            "sqlStatement": sql_statement,
        }
        response = requests.post(
            self.endpoint,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        body = response.json()
        metadata = body.get("metadata", {})
        if metadata.get("status") == "ERROR":
            raise RuntimeError(metadata.get("message", "Unknown Data API error"))
        return body

    @staticmethod
    def _sql_text(value: str | None) -> str:
        if value is None:
            return "NULL"
        escaped = value.replace("'", "''")
        return f"'{escaped}'"

    @staticmethod
    def _sql_int(value: int | None) -> str:
        if value is None:
            return "NULL"
        return str(value)

    @staticmethod
    def _row_to_dict(columns: list[dict[str, Any]], row: dict[str, Any]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        values = row.get("values", [])
        for idx, col in enumerate(columns):
            name = col.get("name")
            raw = values[idx].get("value") if idx < len(values) else None
            if isinstance(name, str):
                out[name] = raw
        return out

    def _ensure_table(self) -> None:
        self._execute_sql(
            """
            CREATE TABLE IF NOT EXISTS user_financial_profiles (
                user_id TEXT PRIMARY KEY,
                name TEXT NULL,
                annual_income INTEGER NULL,
                monthly_expenses INTEGER NULL,
                total_debt INTEGER NULL,
                savings_goal TEXT NULL,
                investment_horizon TEXT NULL,
                risk_tolerance TEXT NULL,
                profile_data JSONB NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """.strip()
        )
    
    def save_user_profile(self, user_id: str, profile_data: dict[str, Any]) -> None:
        """Save or update user financial profile."""
        name = self._sql_text(profile_data.get("name"))
        annual_income = self._sql_int(profile_data.get("annual_income"))
        monthly_expenses = self._sql_int(profile_data.get("monthly_expenses"))
        total_debt = self._sql_int(profile_data.get("total_debt"))
        savings_goal = self._sql_text(profile_data.get("savings_goal"))
        investment_horizon = self._sql_text(profile_data.get("investment_horizon"))
        risk_tolerance = self._sql_text(profile_data.get("risk_tolerance"))
        profile_json = self._sql_text(json.dumps(profile_data))
        user_id_sql = self._sql_text(user_id)

        upsert_sql = f"""
            INSERT INTO user_financial_profiles (
                user_id,
                name,
                annual_income,
                monthly_expenses,
                total_debt,
                savings_goal,
                investment_horizon,
                risk_tolerance,
                profile_data,
                created_at,
                updated_at
            ) VALUES (
                {user_id_sql},
                {name},
                {annual_income},
                {monthly_expenses},
                {total_debt},
                {savings_goal},
                {investment_horizon},
                {risk_tolerance},
                {profile_json}::jsonb,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
            ON CONFLICT (user_id) DO UPDATE SET
                name = EXCLUDED.name,
                annual_income = EXCLUDED.annual_income,
                monthly_expenses = EXCLUDED.monthly_expenses,
                total_debt = EXCLUDED.total_debt,
                savings_goal = EXCLUDED.savings_goal,
                investment_horizon = EXCLUDED.investment_horizon,
                risk_tolerance = EXCLUDED.risk_tolerance,
                profile_data = EXCLUDED.profile_data,
                updated_at = CURRENT_TIMESTAMP
        """.strip()

        self._execute_sql(upsert_sql)
    
    def get_user_profile(self, user_id: str) -> dict[str, Any] | None:
        """Retrieve user financial profile."""
        user_id_sql = self._sql_text(user_id)
        query_sql = f"""
            SELECT
                name,
                annual_income,
                monthly_expenses,
                total_debt,
                savings_goal,
                investment_horizon,
                risk_tolerance,
                updated_at,
                profile_data
            FROM user_financial_profiles
            WHERE user_id = {user_id_sql}
            LIMIT 1
        """.strip()

        body = self._execute_sql(query_sql)
        results = body.get("sqlResults", [])
        if not results:
            return None

        columns = results[0].get("columns", [])
        rows = results[0].get("rows", [])
        if not rows:
            return None

        row = self._row_to_dict(columns, rows[0])
        profile_raw = row.get("profile_data")
        profile_obj = None
        if isinstance(profile_raw, str):
            try:
                profile_obj = json.loads(profile_raw)
            except json.JSONDecodeError:
                profile_obj = None

        def to_int(value: Any) -> int | None:
            if value is None:
                return None
            try:
                return int(value)
            except (TypeError, ValueError):
                return None

        return {
            "name": row.get("name"),
            "annual_income": to_int(row.get("annual_income")),
            "monthly_expenses": to_int(row.get("monthly_expenses")),
            "total_debt": to_int(row.get("total_debt")),
            "savings_goal": row.get("savings_goal"),
            "investment_horizon": row.get("investment_horizon"),
            "risk_tolerance": row.get("risk_tolerance"),
            "last_updated": row.get("updated_at"),
            "all_data": profile_obj,
        }
