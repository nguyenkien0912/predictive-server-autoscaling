#!/bin/bash

echo "========================================"
echo " Stopping Docker Containers"
echo "========================================"
echo ""

docker-compose down

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to stop containers"
    exit 1
fi

echo ""
echo "[INFO] All containers stopped and removed"
echo ""
