import pydantic


class Settings(pydantic.BaseSettings):
    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "api"


settings = Settings()
