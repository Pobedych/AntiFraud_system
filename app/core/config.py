"""
Централизованная конфигурация приложения.
Все значения берутся из переменных окружения — это требование ТЗ.
"""

import os

# ===== DATABASE =====
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ===== JWT =====
JWT_SECRET = os.getenv("RANDOM_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_SECONDS = 3600  # 1 час

# ===== INITIAL ADMIN =====
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_FULLNAME = os.getenv("ADMIN_FULLNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
