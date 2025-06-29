# app/db/base.py
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Импортируем модели, чтобы create_all их увидел
import app.db.models.document  # noqa
import app.db.models.embedding  # noqa
