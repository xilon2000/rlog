import textwrap

from pydantic_settings import (
    BaseSettings, 
    SettingsConfigDict
)


class Settings(BaseSettings):
    @property
    def correlation_id_header_name(self) -> str:
        return "X-Request-ID"

    FOLLOWER_1_URL: str = "http://follower-1:8000"
    FOLLOWER_2_URL: str = "http://follower-2:8000"
    
    @property
    def follower_urls(self) -> tuple[str, ...]:
        return (self.FOLLOWER_1_URL, self.FOLLOWER_2_URL)
    
    APP_NAME: str = "Remote Log Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    NODE_ID: str = "unassigned"
    LEADER_SWAGGER_HOST_URL: str = "http://localhost:8000/docs"
    FOLLOWER_1_SWAGGER_HOST_URL: str = "http://localhost:8001/docs"
    FOLLOWER_2_SWAGGER_HOST_URL: str = "http://localhost:8002/docs"

    @property
    def title(self) -> str:
        return self.APP_NAME
    
    @property
    def description(self) -> str:
        return textwrap.dedent(
            f"""
            **Service Info:** `{self.NODE_ID}`; `v{self.APP_VERSION}`; `debug={str(self.DEBUG).lower()}`

            **Swagger Links:** [`leader`]({self.LEADER_SWAGGER_HOST_URL}); [`follower-1`]({self.FOLLOWER_1_SWAGGER_HOST_URL}); [`follower-2`]({self.FOLLOWER_2_SWAGGER_HOST_URL})
            """
        )

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
