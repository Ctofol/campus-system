#!/bin/bash
cd /root/campus-system/admin/backend
exec /usr/bin/python3.12 -m uvicorn app.main:app --host 0.0.0.0 --port 8093