@echo off
echo Backing up project...
cd C:\Users\Ritika Bobhate\OneDrive\Desktop\5why-project

REM Save Docker images to file
docker save ritika2020/rca-backend:latest -o rca-backend.tar
docker save ritika2020/rca-frontend:latest -o rca-frontend.tar

echo Backup complete!
pause