#  Predictive Server Autoscaling System

Hệ thống dự báo traffic và tự động điều chỉnh số lượng máy chủ (Autoscaling) sử dụng Machine Learning. Project này sử dụng dữ liệu NASA Web Server Access Logs (July-August 1995) để xây dựng mô hình dự báo và hệ thống autoscaling thông minh.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-009688.svg)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-blue.svg)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![LightGBM](https://img.shields.io/badge/LightGBM-4.6-yellow.svg)](https://lightgbm.readthedocs.io/)

---

##  Mục lục

- [Giới thiệu vấn đề](#-giới-thiệu-vấn-đề)
- [Giải pháp](#-giải-pháp)
- [Tính năng chính](#-tính-năng-chính)
- [Cấu trúc dự án](#-cấu-trúc-dự-án)
- [Yêu cầu hệ thống](#-yêu-cầu-hệ-thống)
- [Hướng dẫn cài đặt](#-hướng-dẫn-cài-đặt)
- [Sử dụng Dashboard](#-sử-dụng-dashboard)
- [API Endpoints](#-api-endpoints)
- [Machine Learning Model](#-machine-learning-model)
- [Troubleshooting](#-troubleshooting)

---

##  Giới thiệu vấn đề

Trong quản trị hệ thống cloud computing, việc cấp phát tài nguyên máy chủ gặp phải **3 thách thức lớn**:

| Thách thức | Mô tả | Hậu quả |
|------------|-------|---------|
| **Static Allocation** | Cấp phát số server cố định dựa trên peak load | Lãng phí 60-80% tài nguyên khi traffic thấp |
| **Manual Scaling** | DevOps phải theo dõi và scale thủ công | Phản ứng chậm  Downtime khi traffic spike |
| **Reactive Autoscaling** | Scale sau khi hệ thống đã overload | Performance degradation, user experience kém |

**Ví dụ thực tế:**
- Một website có 1000 users vào giờ cao điểm (20h) nhưng chỉ 100 users lúc 3h sáng
- Nếu cấp phát 10 servers cố định  Lãng phí 90% tài nguyên vào ban đêm
- Nếu cấp phát 2 servers  Sập hệ thống vào giờ cao điểm

---

##  Giải pháp

Hệ thống **Predictive Autoscaling** sử dụng Machine Learning để giải quyết các vấn đề trên:

```

                    PREDICTIVE AUTOSCALING                       

  1. Thu thập dữ liệu traffic lịch sử                           
                                                                
  2. Huấn luyện ML model (LightGBM) để học patterns             
                                                                
  3. Dự báo traffic 1, 5, 15 phút tới                           
                                                                

###  Real-time Dashboard
- **Live metrics**: Current traffic, predictions, server count, utilization
- **Interactive charts**: Traffic load, server scaling, cost analysis
- **Scaling events log**: Lịch sử các quyết định scaling
- **Auto-refresh**: Update mỗi 5 giây

###  Docker Deployment
- **Containerized**: Backend và Frontend đóng gói trong Docker containers
- **Health checks**: Tự động restart khi service fail
- **Easy deployment**: Chạy 1 lệnh để start toàn bộ hệ thống

###  Time Simulation
- **Accelerated demo**: 5 giây thực = 1 phút NASA data
- **Full patterns**: Xem đủ daily patterns trong vài phút
- **Historical replay**: Test với dữ liệu thực từ NASA 1995

---

## 📁 Cấu trúc dự án


predictive-server-autoscaling/
│
├── backend/                            # Backend API Server│   ├── requirements.txt                # Python dependencies
│   ├── Dockerfile                      # Docker configuration
│   ├── .dockerignore
│   │
│   ├── models/                         # Pydantic models
│   │   ├── __init__.py
│   │   ├── request_models.py           # API request schemas
│   │   └── response_models.py          # API response schemas
│   │
│   └── services/                       # Business logic services
│       ├── __init__.py
│       ├── data_service.py             # Data loading and 
│       ├── prediction_service.py       # ML prediction service
│       ├── autoscaling_service.py      # Autoscaling logic
│       └── cost_tracker_service.py     # Cost tracking service
│
├── frontend/                           # Frontend Dashboard
│   ├── index.html                      # Main HTML file
│   ├── package.json                    # Node.js dependencies
│   ├── package-lock.json
│   ├── tsconfig.json                   # TypeScript 
│   ├── vite.config.ts                  # Vite build 
│   ├── Dockerfile                      # Docker configuration
│   ├── nginx.conf                      # Nginx configuration 
│   ├── .dockerignore
│   │
│   └── src/                            # TypeScript source files
│       ├── main.ts                     # Main application logic
│       ├── api.ts                      # API client
│       ├── charts.ts                   # Chart.js configurations
│       ├── types.ts                    # TypeScript type 
│       └── styles/
│           └── main.css                # Application styles
│
├── data/                               # Data Files
│   ├── access_log_Jul95.txt            # NASA logs July 1995 
│   ├── access_log_Aug95.txt            # NASA logs August 1995 
│   ├── nasa_logs_processed.parquet     # Processed data
│   ├── best_model_lgbm_5m.pkl          # Trained LightGBM model
│   ├── prediction_results_5m.csv       # Model predictions
│   └── raw/                            # Raw data backup
│
├── notebooks/                          # Jupyter Notebooks
│   ├── Data_Processing.ipynb           # Data parsing and EDA
│   ├── Basic_Experiment.ipynb          # Initial experiments
│   ├── Final_Solution.ipynb            # Final model training
│   └── Autoscaling_Optimization.ipynb  # Autoscaling policy 
│
├── docker-compose.yml                  # Docker Compose 
├── .dockerignore                       # Docker ignore rules
│
├── scripts/                            # Utility Scripts
│   ├── docker-run.bat                  # Windows: Start Docker 
│   ├── docker-run.sh                   # Linux/Mac: Start Docker 
│   ├── docker-stop.bat                 # Windows: Stop 
│   ├── docker-stop.sh                  # Linux/Mac: Stop 
│   ├── setup.bat                       # Windows: Setup script
│   ├── start-backend.bat               # Windows: Start backend 
│   └── start-frontend.bat              # Windows: Start frontend 
│
├── .env.example                        # Environment variables template
├── .gitignore                          # Git ignore rules
├── requirements.txt                    # Root Python dependencies
├── README.md                           # This file
└── LICENSE                             # MIT License


---

##  Yêu cầu hệ thống

### Phần cứng tối thiểu

| Component | Minimum | Khuyến nghị |
|-----------|---------|-------------|
| **OS** | Windows 10, Ubuntu 20.04, macOS 11 | Windows 11, Ubuntu 22.04, macOS 13 |
| **CPU** | 2 cores | 4 cores |
| **RAM** | 4 GB | 8 GB |
| **Disk** | 5 GB free | 10 GB free |
| **Network** | Internet connection | Stable connection |

### Phần mềm

**Phương án 1 - Docker (Khuyến nghị cho production):**
- [Docker Desktop](https://www.docker.com/products/docker-desktop) 20.10+
- Docker Compose v2.20+ (đi kèm Docker Desktop)

**Phương án 2 - Manual (Khuyến nghị cho development):**
- [Python](https://www.python.org/downloads/) 3.11+
- [Node.js](https://nodejs.org/) 20 LTS+
- pip 23+ (đi kèm Python)
- npm 9+ (đi kèm Node.js)

---

##  Hướng dẫn cài đặt

### Phương án 1: Docker (Khuyến nghị)

>  **Ưu điểm của Docker:**
> - Không cần cài Python/Node.js
> - Environment nhất quán trên mọi OS
> - Dễ deploy lên production
> - Auto-restart khi có lỗi

#### Bước 1: Cài đặt Docker Desktop

**Windows:**
1. Tải Docker Desktop: https://www.docker.com/products/docker-desktop
2. Chạy **Docker Desktop Installer.exe**
3. Chọn "Use WSL 2 instead of Hyper-V" (khuyến nghị)
4. Chờ cài đặt hoàn tất (3-5 phút)
5. Khởi động lại máy nếu được yêu cầu
6. Mở Docker Desktop từ Start Menu
7. Đợi Docker engine start (icon chuyển màu xanh)

**macOS:**
1. Tải Docker Desktop for Mac
   - Intel chip: Download Intel version
   - Apple Silicon (M1/M2/M3): Download Apple Silicon version
2. Mở file .dmg và kéo Docker.app vào Applications
3. Mở Docker từ Applications
4. Đợi Docker engine start

**Linux (Ubuntu/Debian):**
```bash
# Cài đặt Docker
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Cho phép chạy Docker không cần sudo
sudo usermod -aG docker $USER
# Logout và login lại để áp dụng
```

**Kiểm tra cài đặt:**
```bash
docker --version
# Output: Docker version 24.0.x

docker compose version
# Output: Docker Compose version v2.20+
```

#### Bước 2: Clone/Download Project

**Option A - Clone với Git:**
```bash
git clone https://github.com/your-username/predictive-server-autoscaling.git
cd predictive-server-autoscaling
```

**Option B - Download ZIP:**
1. Download ZIP từ GitHub repository
2. Giải nén vào thư mục `predictive-server-autoscaling`
3. Mở Terminal/PowerShell tại thư mục này

#### Bước 3: Build và Start Containers

**Windows:**
```powershell
# Chạy script tự động
.\docker-run.bat
```

**Linux/macOS:**
```bash
# Cấp quyền thực thi (chỉ lần đầu)
chmod +x docker-run.sh

# Chạy script
./docker-run.sh
```

**Hoặc chạy manual với docker-compose:**
```bash
# Build và start containers (chạy background)
docker-compose up -d --build

# Xem build logs
docker-compose logs -f

# Kiểm tra status
docker-compose ps
```

**Thời gian build:**
- Lần đầu: 3-5 phút (download images + install dependencies)
- Các lần sau: 5-10 giây (cached)

#### Bước 4: Kiểm tra và Truy cập

**Kiểm tra containers đang chạy:**
```bash
docker-compose ps

# Output mong đợi:
# NAME                   STATUS              PORTS
# autoscaling-backend    Up (healthy)        0.0.0.0:5000->5000/tcp
# autoscaling-frontend   Up                  0.0.0.0:3000->80/tcp
```

**Truy cập hệ thống:**

| Service | URL | Mô tả |
|---------|-----|-------|
| **Dashboard** | http://localhost:3000 | Giao diện chính |
| **API Docs** | http://localhost:5000/docs | Swagger UI |
| **Health Check** | http://localhost:5000/api/health | Kiểm tra backend |

#### Quản lý Containers

```bash
# Dừng containers (giữ data)
docker-compose stop

# Khởi động lại containers đã dừng
docker-compose start

# Dừng và xóa containers
docker-compose down

# Rebuild khi thay đổi code
docker-compose down
docker-compose up -d --build

# Xem logs real-time
docker-compose logs -f

# Xem logs của service cụ thể
docker-compose logs -f backend
docker-compose logs -f frontend

# Xem resource usage
docker stats
```

---

### Phương án 2: Cài đặt thủ công

>  **Khi nào dùng Manual:**
> - Development và debugging
> - Không có Docker
> - Muốn customize environment

#### Bước 1: Kiểm tra Prerequisites

```bash
# Kiểm tra Python
python --version
# Cần: Python 3.11.x hoặc mới hơn

# Kiểm tra pip
pip --version
# Cần: pip 23.x+

# Kiểm tra Node.js
node --version
# Cần: v20.x.x hoặc mới hơn

# Kiểm tra npm
npm --version
# Cần: 9.x+
```

**Nếu chưa cài Python:**
- Windows: https://www.python.org/downloads/ (chọn "Add Python to PATH")
- macOS: `brew install python@3.11`
- Linux: `sudo apt install python3.11 python3.11-venv python3-pip`

**Nếu chưa cài Node.js:**
- Windows/macOS: https://nodejs.org/ (Download LTS version)
- Linux: `curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt-get install -y nodejs`

#### Bước 2: Clone Project

```bash
git clone https://github.com/your-username/predictive-server-autoscaling.git
cd predictive-server-autoscaling
```

#### Bước 3: Setup Backend

```bash
# Di chuyển vào thư mục backend
cd backend

# Tạo virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Cài đặt dependencies
pip install -r requirements.txt

# Thời gian: 2-3 phút (download khoảng 500MB packages)
```

**Kiểm tra cài đặt backend:**
```bash
# Test imports
python -c "import fastapi; import lightgbm; import pandas; print(' All packages OK')"
```

#### Bước 4: Setup Frontend

```bash
# Quay lại root directory
cd ..

# Di chuyển vào frontend
cd frontend

# Cài đặt dependencies
npm install

# Thời gian: 1-2 phút (download khoảng 200MB node_modules)
```

**Kiểm tra cài đặt frontend:**
```bash
# Test build
npm run build
# Nếu thấy thư mục "dist" được tạo  Success!
```

#### Bước 5: Chạy Backend (Terminal 1)

```bash
# Di chuyển vào backend
cd backend

# Activate venv (nếu chưa)
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Chạy server
python app.py
```

**Output mong đợi:**
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
```

 Backend chạy tại: **http://localhost:5000**

#### Bước 6: Chạy Frontend (Terminal 2 - Mở terminal MỚI)

```bash
# Di chuyển vào frontend
cd frontend

# Chạy development server
npm run dev
```

**Output mong đợi:**
```
VITE v6.x.x  ready in xxx ms

  Local:   http://localhost:5173/
  Network: use --host to expose
```

 Frontend chạy tại: **http://localhost:5173**

#### Bước 7: Truy cập Dashboard

| Service | URL |
|---------|-----|
| **Dashboard** | http://localhost:5173 |
| **API Docs** | http://localhost:5000/docs |

**Lưu ý quan trọng:**
- Frontend (manual) chạy port **5173**, không phải 3000 như Docker
- Backend phải chạy trước để frontend có thể connect

#### Dừng Servers

```bash
# Backend: Nhấn Ctrl+C trong terminal backend

# Frontend: Nhấn Ctrl+C trong terminal frontend

# Deactivate venv (backend)
deactivate
```

---

##  Sử dụng Dashboard

### Giao diện tổng quan

Khi truy cập Dashboard, bạn sẽ thấy:

```

   Predictive Server Autoscaling        [Connected ]   

                                                            
          
   Current    Predicted  Active     Cost/         
   Requests   (5min)     Servers    Hour          
     42         56          3        $0.30        
          
                                                            
    
             Traffic Load Chart                        
     Actual     Predicted                    
    
                                                            
     
    Server Count         Scaling Events           
                          10:05 Scale-out 23         
                          10:02 Maintain 2            
     

```

### Main Metrics (Top Cards)

| Metric | Ý nghĩa | Giá trị mẫu |
|--------|---------|-------------|
| **Current Requests** | Số requests/minute hiện tại | 42 req/min |
| **Predicted (5M)** | Dự báo traffic 5 phút tới | 56 req/min |
| **Active Servers** | Số servers đang active | 3 servers |
| **Utilization** | % capacity đang sử dụng | 70% |
| **Cost/Hour** | Chi phí vận hành | $0.30/hour |

### Charts

**1. Traffic Load Chart:**
- **Actual (xanh)**: Traffic thực tế
- **Predicted (cam)**: Traffic dự báo
- Update mỗi 5 giây
- Hiển thị 10 phút gần nhất

**2. Server Count Chart:**
- Số servers theo thời gian
- Highlight khi có scaling event

**3. Cost Analysis Chart:**
- Chi phí tích lũy theo thời gian
- Tính theo số servers  $0.10/hour

### Predictions Panel

Hiển thị 3 predictions với confidence scores:

| Interval | Prediction | Confidence |
|----------|------------|------------|
| 1 minute | 45 req/min | 94% |
| 5 minutes | 56 req/min | 90% |
| 15 minutes | 72 req/min | 80% |

### Scaling Events Log

Lịch sử các quyết định scaling:
```
10:05:00  SCALE-OUT  2  3 servers  "Predicted utilization 85% > threshold 80%"
10:02:00  MAINTAIN   2 servers      "Utilization 65% within normal range"
09:55:00  SCALE-IN   3  2 servers  "Utilization 35% < threshold 40%"
```

### Autoscaling Configuration

| Parameter | Value | Mô tả |
|-----------|-------|-------|
| Min Servers | 1 | Số server tối thiểu |
| Max Servers | 50 | Số server tối đa |
| Scale-out Threshold | 80% | Scale-out khi utilization > 80% |
| Scale-in Threshold | 40% | Scale-in khi utilization < 40% |
| Cooldown Period | 2 min | Thời gian chờ giữa 2 lần scale |
| Requests per Server | 200 | Capacity mỗi server |
| Cost per Server | $0.10/hour | Chi phí mỗi server |

### NASA Time Simulation

Dashboard sử dụng **time-accelerated simulation**:
- **5 giây thực = 1 phút NASA data**
- Data bắt đầu từ August 25, 1995, 06:00 AM
- Xem đủ daily traffic patterns trong vài phút thực

---

##  API Endpoints

### Overview

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/health` | Health check |
| GET | `/api/current-traffic` | Traffic hiện tại |
| POST | `/api/forecast` | Dự báo traffic |
| POST | `/api/scaling-recommendation` | Scaling recommendation |
| GET | `/api/dashboard-data` | Full dashboard data |
| GET | `/api/scaling-events` | Lịch sử scaling events |
| GET | `/api/config` | Autoscaling configuration |

### Chi tiết từng Endpoint

#### 1. Health Check
```bash
curl http://localhost:5000/api/health
```
```json
{
  "status": "healthy",
  "timestamp": "1995-08-25T10:30:00",
  "version": "1.0.0"
}
```

#### 2. Current Traffic
```bash
curl http://localhost:5000/api/current-traffic
```
```json
{
  "timestamp": "1995-08-25T10:30:00",
  "current_requests": 42,
  "current_bytes": 1250000
}
```

#### 3. Forecast
```bash
curl -X POST http://localhost:5000/api/forecast \
  -H "Content-Type: application/json" \
  -d '{"intervals": [1, 5, 15]}'
```
```json
{
  "timestamp": "1995-08-25T10:30:00",
  "predictions": [
    {"interval": 1, "predicted_requests": 45, "confidence": 0.94},
    {"interval": 5, "predicted_requests": 56, "confidence": 0.90},
    {"interval": 15, "predicted_requests": 72, "confidence": 0.80}
  ]
}
```

#### 4. Scaling Recommendation
```bash
curl -X POST http://localhost:5000/api/scaling-recommendation \
  -H "Content-Type: application/json" \
  -d '{
    "current_servers": 2,
    "current_requests": 350,
    "predicted_requests": 450
  }'
```
```json
{
  "current_servers": 2,
  "recommended_servers": 3,
  "action": "scale-out",
  "reason": "Predicted utilization (112%) exceeds threshold (80%)",
  "estimated_utilization": 75.0,
  "estimated_cost_change": 0.10
}
```

#### 5. Dashboard Data
```bash
curl http://localhost:5000/api/dashboard-data
```
Trả về full data cho dashboard: metrics, predictions, scaling events, config.

**Full API Documentation:** http://localhost:5000/docs (Swagger UI)

---

##  Machine Learning Model

### Dataset

**Source:** NASA Kennedy Space Center WWW Server Logs
- **URL:** http://ita.ee.lbl.gov/html/contrib/NASA-HTTP.html
- **Period:** July 1 - August 31, 1995
- **Total requests:** ~3.4 million

**Data Split:**
| Set | Period | Records | Dùng cho |
|-----|--------|---------|----------|
| Training | July 1995 | ~1.9M | Train model |
| Validation | Aug 1-22 | ~1.2M | Tune hyperparameters |
| Test | Aug 23-31 | ~300K | Evaluate & Demo |

### Feature Engineering

**Time-based Features (6):**
```python
'hour'           # Giờ trong ngày (0-23)
'dayofweek'      # Thứ trong tuần (0=Monday, 6=Sunday)
'is_weekend'     # Cuối tuần (0/1)
'part_of_day'    # Buổi: 0=night, 1=morning, 2=afternoon, 3=evening
'hour_sin'       # sin(2π  hour/24) - cyclic encoding
'hour_cos'       # cos(2π  hour/24) - cyclic encoding
```

**Lag Features (3):**
```python
'lag_1'          # Traffic 1 interval trước
'lag_2'          # Traffic 2 intervals trước
'lag_3'          # Traffic 3 intervals trước
```

**Rolling Statistics (3):**
```python
'rolling_mean'   # Mean của 5 intervals gần nhất
'rolling_std'    # Standard deviation của 5 intervals
'rolling_max'    # Max của 5 intervals
```

### Model: LightGBM

**Algorithm:** Light Gradient Boosting Machine
- Nhanh hơn XGBoost 10-20x
- Memory efficient
- Tốt với large datasets

**Hyperparameters:**
```python
{
    'n_estimators': 500,
    'learning_rate': 0.01,
    'max_depth': 6,
    'num_leaves': 31,
    'min_child_samples': 20,
    'objective': 'regression',
    'metric': 'rmse'
}
```

### Performance Metrics

**5-minute Interval (Primary):**

| Metric | Value | Ý nghĩa |
|--------|-------|---------|
| **MAE** | 4.5 req/min | Trung bình sai số 4.5 requests |
| **RMSE** | 6.2 req/min | Root mean square error |
| **R** | 0.88 | Giải thích 88% variance |
| **Accuracy** | 90% | % predictions trong 10% actual |

**Comparison across intervals:**

| Interval | MAE | RMSE | R | Accuracy |
|----------|-----|------|-----|----------|
| 1 min | 2.3 | 3.1 | 0.92 | 94% |
| 5 min | 4.5 | 6.2 | 0.88 | 90% |
| 15 min | 8.1 | 11.3 | 0.78 | 80% |

### Jupyter Notebooks

| Notebook | Mô tả |
|----------|-------|
| `Data_Processing.ipynb` | Parse raw logs, EDA, feature engineering |
| `Final_Solution.ipynb` | Model training, hyperparameter tuning, evaluation |
| `Autoscaling_Optimization.ipynb` | Scaling policy optimization, cost analysis |

---

##  Troubleshooting

### Docker Issues

| Vấn đề | Nguyên nhân | Giải pháp |
|--------|-------------|-----------|
| "Docker is not running" | Docker Desktop chưa start | Mở Docker Desktop, đợi icon xanh |
| Containers không start | Lỗi trong code hoặc config | `docker-compose logs` để xem chi tiết |
| Port already in use | Port 5000/3000 đã bị chiếm | Kill process: `netstat -ano \| findstr :5000` |
| Build lỗi | Cache bị corrupt | `docker-compose down --rmi all` rồi rebuild |
| Backend unhealthy | Dependencies lỗi | `docker-compose build --no-cache backend` |

**Debug commands:**
```bash
# Xem logs chi tiết
docker-compose logs -f

# Xem logs của 1 service
docker-compose logs -f backend

# Kiểm tra container status
docker-compose ps

# Restart 1 service
docker-compose restart backend

# Rebuild từ đầu
docker-compose down --volumes
docker-compose up -d --build
```

### Manual Installation Issues

| Vấn đề | Nguyên nhân | Giải pháp |
|--------|-------------|-----------|
| "Module not found" | Dependencies chưa cài đủ | `pip install -r requirements.txt --force-reinstall` |
| "venv not activated" | Quên activate venv | `venv\Scripts\activate` (Windows) |
| Frontend không connect | Backend chưa chạy | Kiểm tra http://localhost:5000/api/health |
| CORS error | Backend CORS config | Kiểm tra `allow_origins` trong app.py |
| npm install lỗi | npm cache corrupt | `npm cache clean --force` rồi install lại |
| Port 5000 in use | Process khác đang dùng | Kill process hoặc đổi port |

**Debug commands:**
```bash
# Kiểm tra port
netstat -ano | findstr :5000   # Windows
lsof -i :5000                  # Linux/Mac

# Kill process (Windows)
taskkill /PID <PID> /F

# Test backend imports
cd backend
python -c "import app; print('OK')"

# Test API
curl http://localhost:5000/api/health
```

### Common Errors

**1. "LightGBM model not found"**
```bash
# Model file missing
# Giải pháp: Chạy notebook Final_Solution.ipynb để train model
```

**2. "Data file not found"**
```bash
# NASA logs missing
# Kiểm tra: ls data/access_log_Aug95.txt
# Download từ: http://ita.ee.lbl.gov/html/contrib/NASA-HTTP.html
```

**3. "Connection refused" trên Dashboard**
```bash
# Backend chưa chạy hoặc khác port
# Kiểm tra backend đã start và chạy đúng port 5000
curl http://localhost:5000/api/health
```

---

##  Tech Stack

### Backend
- **Python 3.11** - Programming language
- **FastAPI 0.128** - Modern web framework
- **LightGBM 4.6** - ML model
- **Pandas 3.0** - Data processing
- **NumPy** - Numerical computing
- **Uvicorn 0.40** - ASGI server
- **Pydantic** - Data validation

### Frontend
- **TypeScript 5.7** - Type-safe JavaScript
- **Vite 6.1** - Fast build tool
- **Chart.js 4.4** - Data visualization
- **Vanilla TS** - No framework (lightweight)

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Container orchestration
- **Nginx** - Reverse proxy (production)

---

##  License

MIT License - See [LICENSE](LICENSE) file for details.

---

<div align="center">

** Star this repo if you find it useful! **

Made with  by **HAMIC AI Team**

**Competition:** DATAFLOW 2026 - The Alchemy of Minds

[ Back to top](#-predictive-server-autoscaling-system)

</div>
