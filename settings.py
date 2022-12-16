from pydantic import BaseSettings


class Settings(BaseSettings):
    server_host: str = '127.0.0.1'
    server_port: int = 8000
    database_url: str
    async_database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    email: str
    email_access: str

    class Config:
        env_file = '.env'
        env_file_encoding = "utf-8"


settings = Settings()


