from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
import os
from auth import AuthHandler

router = APIRouter()
auth_handler = AuthHandler()

@router.post("/api/upload_image/")
async def upload_image(item_id: int, file: UploadFile = File(...), _=Depends(auth_handler.auth_wrapper)):
    allowed_extensions = {"jpg", "jpeg", "png"}
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    path = "static/images/"
    filename = os.path.join(path, f"{item_id}.jpg")
    if os.path.exists(filename):
        raise HTTPException(status_code=400, detail="File already exists.")

    try:
        contents = await file.read()
        with open(filename, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    finally:
        await file.close()

    return {"filename": file.filename}