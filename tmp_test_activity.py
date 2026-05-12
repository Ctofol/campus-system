
import sys
sys.path.insert(0, 'backend')
from app import models, database, auth
from datetime import datetime

db = database.SessionLocal()
try:
    u = db.query(models.User).filter(models.User.name == 'TestStudent').first()
    if not u:
        hashed_password = auth.get_password_hash('123456')
        u = models.User(
            phone='13388888888',
            name='TestStudent',
            password_hash=hashed_password,
            role='student',
            student_id='ST001'
        )
        db.add(u)
        db.flush()
    
    g = db.query(models.RunGroup).filter(models.RunGroup.name == 'TestGroup').first()
    if not g:
        g = models.RunGroup(name='TestGroup', total_mileage=100.0, member_count=1, creator_id=u.id)
        db.add(g)
        db.flush()
    
    a = models.RunGroupActivity(
        group_id=g.id,
        title='TestActivity',
        description='Test description',
        status='upcoming',
        activity_time=datetime(2026, 3, 27, 10, 0),
        total_quota=10,
        apply_count=1,
        created_by=u.id,
        distance=5.0
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    print(f'ActivityID: {a.id}')
finally:
    db.close()
