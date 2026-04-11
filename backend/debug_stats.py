
from app.database import SessionLocal
from app import models
from app.services.teacher_service import get_managed_students_query
import asyncio

async def debug_stats():
    db = SessionLocal()
    phone = "13800010001"
    user = db.query(models.User).filter(models.User.phone == phone).first()
    if not user:
        print("Teacher not found")
        return

    student_query = await get_managed_students_query(user, db)
    managed_student_ids = [u.id for u in student_query.with_entities(models.User.id).all()]
    print(f"Teacher {user.name} manages {len(managed_student_ids)} students")

    pending_health = db.query(models.HealthRequest).filter(
        models.HealthRequest.status == "pending",
        models.HealthRequest.student_id.in_(managed_student_ids)
    ).count()
    print(f"Pending health requests: {pending_health}")

    pending_activities = db.query(models.Activity).filter(
        models.Activity.is_valid.is_(False),
        models.Activity.fail_reason.isnot(None),
        models.Activity.fail_reason != "",
        models.Activity.user_id.in_(managed_student_ids)
    ).count()
    print(f"Pending activities (exceptions): {pending_activities}")

    abnormal_students = student_query.filter(models.User.health_status != 'normal').all()
    print(f"Abnormal students (status != normal): {len(abnormal_students)}")
    for s in abnormal_students:
        print(f" - {s.name}: {s.health_status}")

    db.close()

if __name__ == "__main__":
    asyncio.run(debug_stats())
