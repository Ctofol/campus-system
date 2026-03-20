#!/bin/bash
PASS='@chenjunhong123456'
echo "$PASS" | sudo -S echo "Authorized"
PRJ_DIR="/project/campus-system/admin/frontend"
echo "Target directory: $PRJ_DIR"

if [ ! -d "$PRJ_DIR" ]; then
    echo "Creating directory $PRJ_DIR"
    echo "$PASS" | sudo -S mkdir -p "$PRJ_DIR"
fi

echo "Copying files from home directory..."
echo "$PASS" | sudo -S cp ~/Dockerfile "$PRJ_DIR/"
echo "$PASS" | sudo -S cp ~/dist.zip "$PRJ_DIR/"

echo "Unzipping in $PRJ_DIR..."
cd "$PRJ_DIR"
echo "$PASS" | sudo -S unzip -o dist.zip

echo "Rebuilding Docker container..."
cd /project/campus-system
echo "$PASS" | sudo -S docker-compose down admin-frontend
echo "$PASS" | sudo -S docker-compose up --build -d admin-frontend

echo "Updating host /var/www/campus-admin..."
echo "$PASS" | sudo -S mkdir -p /var/www/campus-admin
echo "$PASS" | sudo -S cp -rv "$PRJ_DIR/dist/"* /var/www/campus-admin/

echo "Finished."
