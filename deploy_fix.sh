#!/bin/bash
echo "Starting deployment script..."
PASS='@chenjunhong123456'

echo "Unzipping dist.zip..."
unzip -o ~/dist.zip -d ~/fresh_dist

echo "Updating Docker container campus-admin-frontend..."
echo $PASS | sudo -S docker cp ~/fresh_dist/. campus-admin-frontend:/usr/share/nginx/html/

echo "Updating host /var/www/campus-admin (just in case)..."
echo $PASS | sudo -S mkdir -p /var/www/campus-admin
echo $PASS | sudo -S cp -r ~/fresh_dist/* /var/www/campus-admin/

echo "Checking for '8002' string in Docker container..."
echo $PASS | sudo -S docker exec campus-admin-frontend grep -rn "8002" /usr/share/nginx/html

echo "Checking for '8002' string in host /var/www/campus-admin..."
echo $PASS | sudo -S grep -rn "8002" /var/www/campus-admin

echo "Deployment complete."
