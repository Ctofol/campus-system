
from app.database import SessionLocal, engine
from app import models, auth

def create_admin_user():
    db = SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(models.User).filter(models.User.role == "admin").first()
        if admin:
            print(f"Admin already exists: {admin.phone}")
            return

        # Create admin
        hashed_password = auth.get_password_hash("admin123")
        new_admin = models.User(
            phone="admin",
            name="Administrator",
            password_hash=hashed_password,
            role="admin",
            student_id="ADMIN001"
        )
        db.add(new_admin)
        db.commit()
        print("Admin user created successfully.")
        print("Username: admin")
        print("Password: admin123")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
