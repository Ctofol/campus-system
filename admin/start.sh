#!/bin/bash
cd /root/campus-system/admin/backend
nohup /usr/bin/python3.12 -m uvicorn app.main:app --host 0.0.0.0 --port 8092 --log-level info > /tmp/admin.log 2>&1 &
echo "Admin backend started"