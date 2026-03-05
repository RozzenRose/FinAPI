from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    POSTGRES_FOR_TESTS_HOST: str
    POSTGRES_FOR_TESTS_PORT: int
    POSTGRES_FOR_TESTS_USER: str
    POSTGRES_FOR_TESTS_PASSWORD: str
    POSTGRES_FOR_TESTS_DB: str

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def database_tests_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_FOR_TESTS_USER}:{self.POSTGRES_FOR_TESTS_PASSWORD}"
            f"@{self.POSTGRES_FOR_TESTS_HOST}:{self.POSTGRES_FOR_TESTS_PORT}/{self.POSTGRES_FOR_TESTS_DB}"
        )


settings = Settings()
