from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.cf_parser import parse_cf_file
import os
import shutil
import uuid

router = APIRouter(prefix="/api/v1/cf", tags=["cf"])

@router.post("/parse")
async def parse_cf(file: UploadFile = File(...)):
    # Генерируем уникальное имя для файла
    unique_name = f"{uuid.uuid4()}.cf"
    file_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    file_path = os.path.join(file_dir, unique_name)

    try:
        # Сохраняем загруженный файл
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        # Парсим через внешний сервис
        result = parse_cf_file(file_path)
        # Удаляем временный файл
        os.remove(file_path)
        return {"structure": result}
    except Exception as e:
        # Попытка удалить файл даже при ошибке
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass
        raise HTTPException(status_code=400, detail=f"Ошибка парсинга cf: {e}")
