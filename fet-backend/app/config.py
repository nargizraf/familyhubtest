from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://familyhub:familyhub@localhost:5432/familyhub"
    test_database_url: str = "postgresql+psycopg://familyhub:familyhub@localhost:5432/familyhub_test"
    jwt_secret: str = "dev-only-change-me-use-a-long-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    demo_user_email: str = "demo@example.com"
    demo_user_password: str = "Demo123!"
    demo_user_name: str = "Demo User"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
