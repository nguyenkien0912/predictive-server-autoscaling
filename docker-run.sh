#!/bin/bash

echo "========================================"
echo " Predictive Server Autoscaling - Docker"
echo "========================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker is not installed"
    echo "Please install Docker from https://www.docker.com/get-started"
    exit 1
fi

echo "[INFO] Docker is installed"
echo ""

# Check if Docker is running
if ! docker ps &> /dev/null; then
    echo "[ERROR] Docker is not running"
    echo "Please start Docker and try again"
    exit 1
fi

echo "[INFO] Docker is running"
echo ""

# Build and start containers
echo "[INFO] Building and starting Docker containers..."
echo "This may take a few minutes on first run..."
echo ""

docker-compose up --build -d

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Failed to start containers"
    exit 1
fi

echo ""
echo "========================================"
echo " Containers started successfully!"
echo "========================================"
echo ""
echo "Backend API:    http://localhost:5000"
echo "Frontend UI:    http://localhost"
echo ""
echo "To view logs:   docker-compose logs -f"
echo "To stop:        docker-compose stop"
echo "To remove:      docker-compose down"
echo ""

# Wait for services to start
sleep 3

# Check container status
echo "[INFO] Container status:"
docker-compose ps

echo ""
echo "Opening browser in 3 seconds..."
sleep 3

# Open browser (works on most Linux systems)
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost
elif command -v gnome-open &> /dev/null; then
    gnome-open http://localhost
fi

echo "Press any key to continue..."
read -n 1
