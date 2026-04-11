import sys
import os

sys.path.append(os.getcwd())

from app.routers import (
    teacher, courses, approvals, student, 
    upload, run_groups, admin, common, 
    auth, user, activity
)
print("ALL ROUTERS OK")
