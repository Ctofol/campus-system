
from app.database import SessionLocal
from app import models

def clean_class_names():
    db = SessionLocal()
    classes = db.query(models.Class).all()
    for c in classes:
        if c.major and c.name.startswith(c.major.name):
            old_name = c.name
            new_name = old_name.replace(c.major.name, "").strip()
            print(f"Renaming class '{old_name}' to '{new_name}'")
            c.name = new_name
    db.commit()
    db.close()

if __name__ == "__main__":
    clean_class_names()
