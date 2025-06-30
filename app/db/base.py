from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Импортируем модели, чтобы alembic увидел их
import app.db.models.document  # noqa
import app.db.models.embedding  # noqa
import app.db.models.user  # ⬅️ ВАЖНО: добавляем эту строку
