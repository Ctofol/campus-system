from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import random
import string
import base64
import hashlib
from captcha.image import ImageCaptcha
from .. import models, schemas, database, config

router = APIRouter(prefix="/common", tags=["common"])

get_db = database.get_db

@router.get("/captcha")
def get_captcha():
    # Generate 4 random chars
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    
    # Generate image
    image = ImageCaptcha(width=120, height=50)
    data = image.generate(code)
    
    # Encode to base64
    base64_str = base64.b64encode(data.getvalue()).decode('utf-8')
    image_data = f"data:image/png;base64,{base64_str}"
    
    # Generate key (stateless verification)
    key_src = code.upper() + config.CAPTCHA_SECRET
    key = hashlib.md5(key_src.encode('utf-8')).hexdigest()
    
    return {"image": image_data, "key": key}

@router.get("/majors")
def get_majors(db: Session = Depends(get_db)):
    majors = db.query(models.Major).all()
    return [{"id": m.id, "name": m.name} for m in majors]

@router.get("/classes")
def get_classes_by_major(major_id: int, db: Session = Depends(get_db)):
    classes = db.query(models.Class).filter(models.Class.major_id == major_id).all()
    return [{"id": c.id, "name": c.name} for c in classes]

@router.get("/checkpoints")
def get_checkpoints(db: Session = Depends(get_db)):
    return db.query(models.Checkpoint).all()

@router.post("/checkpoints")
def create_checkpoint(
    checkpoint_in: schemas.CheckpointCreate,
    db: Session = Depends(get_db)
):
    db_checkpoint = models.Checkpoint(**checkpoint_in.dict())
    db.add(db_checkpoint)
    db.commit()
    db.refresh(db_checkpoint)
    return db_checkpoint
