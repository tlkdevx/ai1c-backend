from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/v1/upload-cf", tags=["upload-cf"])

@router.post("/", status_code=201)
async def upload_cf(
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    # Пока только заглушка — возвращаем имя и размер файла
    content = await file.read()
    return {
        "filename": file.filename,
        "size_bytes": len(content),
        "message": "Файл принят! Разбор .cf/.epf будет реализован позже."
    }
