"""CP1 — Cấu hình theo 12-Factor.

Nguyên tắc: **không có giá trị cấu hình nào nằm trong code**. Tất cả đến từ
biến môi trường, để cùng một image chạy được ở laptop, staging và production
mà không phải sửa một dòng code nào.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Toàn bộ cấu hình của service.

    pydantic-settings đọc biến môi trường theo tên trường (không phân biệt
    hoa thường). ``api_token`` chấp nhận cả ``API_TOKEN`` và
    ``AGENT_API_KEY`` để tương thích với các checkpoint khác nhau của lab.

    ``api_token`` không có giá trị mặc định để app fail fast nếu secret chưa
    được cấu hình.
    """

    port: int = 8000
    api_token: str = Field(
        validation_alias=AliasChoices("API_TOKEN", "AGENT_API_KEY")
    )
    redis_url: str = "redis://localhost:6379/0"
    bucket_capacity: int = 10
    refill_per_minute: int = 10
    daily_budget_usd: float = 1.0
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("api_token")
    @classmethod
    def _validate_api_token(cls, value: str) -> str:
        token = value.strip()
        placeholder_tokens = {
            "",
            "changeme",
            "change-me",
            "change_me",
            "placeholder",
            "your-api-key",
            "your_api_key",
            "your-token",
            "your_token",
            "replace-me",
            "replace_me",
        }
        if token.lower() in placeholder_tokens:
            raise ValueError("api_token must be set to a real non-placeholder value")
        return token


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Đọc cấu hình một lần rồi cache lại (đọc env mỗi request là lãng phí)."""
    return Settings()
