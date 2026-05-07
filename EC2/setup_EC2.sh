#!/bin/bash
# EC2 Setup Script — Team 82
# Run from inside /home/ubuntu/app (the project root)
# Usage: bash EC2/setup_ec2.sh

set -e

echo "=== [1/5] Update packages ==="
sudo apt-get update -y -q
sudo apt-get install -y -q python3 python3-pip python3-venv

echo "=== [2/5] Create virtual environment ==="
python3 -m venv venv
source venv/bin/activate

echo "=== [3/5] Install dependencies ==="
pip install --quiet flask flask_cors boto3 requests gunicorn

echo "=== [4/5] Create log folder ==="
mkdir -p logs

echo "=== [5/5] Start app on port 80 ==="
# gunicorn runs as root so it can bind to port 80 (ports below 1024 need root)
# EC2.appEC2 means: inside the EC2/ folder, the appEC2.py file
# --daemon puts it in the background
sudo venv/bin/gunicorn \
    --workers 2 \
    --bind 0.0.0.0:80 \
    --daemon \
    --pid logs/gunicorn.pid \
    --access-logfile logs/access.log \
    --error-logfile  logs/error.log \
    EC2.appEC2:app

echo ""
echo "=== Done! ==="
echo "App is running on port 80"
echo ""
echo "Test it: curl http://localhost/login"
echo ""
echo "To stop:  sudo kill \$(cat logs/gunicorn.pid)"
echo "To restart: bash EC2/setup_ec2.sh"
echo "View logs:  tail -f logs/error.log"