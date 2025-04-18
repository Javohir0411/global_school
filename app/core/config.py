from pydantic_settings import BaseSettings

"""
.env faylidagi manzilni pydantic tekshiradi ma'lumot bormi yoki yo'q.
Agar mavjud bo'lsa, bazaga ulanish ishlaydi, aks xolda, xatolik chiqaradi.
"""


class Settings(BaseSettings):
    DATABASE_URL: str
    # DB_NAME: str = "product_inventory"
    # DB_USER: str = "postgres"
    # DB_PASSWORD: str = "your_password"
    # DB_HOST: str = "localhost"
    # DB_PORT: int = 5432

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()