from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_name: str = "~/models/meltemi7b.q4km.gguf"
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    embedding_model: str = "intfloat/multilingual-e5-large"
    api_token: str = "secret-token"

    class Config:
        env_file = ".env"


settings = Settings()
