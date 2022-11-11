import pydantic


class Settings(pydantic.BaseSettings):
    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "api"
    BACKEND_CORS_ORIGINS: list[pydantic.AnyHttpUrl] = []

    @pydantic.validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)


settings = Settings()
