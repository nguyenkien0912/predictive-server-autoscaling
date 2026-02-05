# 🖥️ Predictive Server Autoscaling System

Hệ thống dự báo traffic và tự động điều chỉnh số lượng máy chủ (Autoscaling) sử dụng Machine Learning. Project này sử dụng dữ liệu NASA Web Server Access Logs (July-August 1995) để xây dựng mô hình dự báo và hệ thống autoscaling thông minh.

## 📋 Giới thiệu

Trong quản trị hệ thống đám mây, việc cấp phát tài nguyên cố định thường dẫn đến hai vấn đề:
- **Lãng phí tài nguyên** khi ít người truy cập
- **Sập hệ thống** khi lượng truy cập tăng đột biến

Hệ thống này giải quyết vấn đề bằng cách:
1. **Dự báo traffic** cho các khung thời gian 1, 5, 15 phút sử dụng XGBoost
2. **Tự động điều chỉnh** số lượng server dựa trên dự báo
3. **Tối ưu chi phí** vận hành hệ thống
4. **Giám sát real-time** qua dashboard trực quan

## 🏗️ Kiến trúc hệ thống

```
📁 predictive-server-autoscaling/
├── 📁 backend/                          # Backend API (Python + FastAPI)
│   ├── 📄 app.py                       # FastAPI application
│   ├── 📄 requirements.txt             # Python dependencies
│   ├── 📁 models/                      # Data models
│   │   ├── 📄 request_models.py        # Request schemas
│   │   ├── 📄 response_models.py       # Response schemas
│   │   └── 📄 trained/                 # Trained ML models (optional)
│   └── 📁 services/                    # Business logic
│       ├── 📄 data_service.py          # Data management
│       ├── 📄 prediction_service.py    # Traffic prediction
│       └── 📄 autoscaling_service.py   # Scaling recommendations
│
├── 📁 frontend/                         # Frontend Dashboard (TypeScript)
│   ├── 📄 index.html                   # Main HTML
│   ├── 📄 package.json                 # Node.js dependencies
│   ├── 📄 vite.config.ts               # Vite configuration
│   └── 📁 src/                         # Source code
│       ├── 📄 main.ts                  # Main application
│       ├── 📄 api.ts                   # API service
│       ├── 📄 charts.ts                # Chart management
│       ├── 📄 types.ts                 # TypeScript types
│       └── 📁 styles/
│           └── 📄 main.css             # Styles
│
├── 📁 data/                             # Data files
│   ├── 📄 access_log_Jul95.txt         # July logs (train)
│   ├── 📄 access_log_Aug95.txt         # August logs (test)
│   └── 📄 nasa_logs_processed.parquet  # Processed data
│
├── 📄 Final_Solution.ipynb              # Main notebook với models
├── 📄 Data_Processing.ipynb             # Data preprocessing
├── 📄 setup.bat                         # Windows setup script
├── 📄 start-backend.bat                 # Start backend
├── 📄 start-frontend.bat                # Start frontend
└── 📄 README.md                         # Documentation

```

## 🚀 Hướng dẫn cài đặt và chạy

### Yêu cầu hệ thống

- **Python 3.8+** (khuyến nghị 3.10)
- **Node.js 16+** (khuyến nghị 18+)
- **pip** và **npm**
- RAM: 4GB+
- OS: Windows, Linux, hoặc MacOS

### Bước 1: Setup Dependencies (Tự động)

**Trên Windows:**
```powershell
setup.bat
```

Script sẽ tự động:
- ✅ Kiểm tra Python và Node.js
- ✅ Cài đặt dependencies cho backend
- ✅ Cài đặt dependencies cho frontend

**Hoặc cài đặt thủ công:**

```powershell
# Backend
cd backend
pip install -r requirements.txt
cd ..

# Frontend
cd frontend
npm install
cd ..
```

### Bước 2: Chạy Backend Server

**Terminal 1:**
```powershell
start-backend.bat
```

Hoặc:
```powershell
cd backend
python app.py
```

Backend sẽ chạy tại: **http://localhost:5000**

### Bước 3: Chạy Frontend Dashboard

**Terminal 2 (mở terminal mới):**
```powershell
start-frontend.bat
```

Hoặc:
```powershell
cd frontend
npm run dev
```

Frontend sẽ chạy tại: **http://localhost:3000**

### Bước 4: Truy cập Dashboard

1. **Mở trình duyệt** và truy cập: **http://localhost:3000**
2. **Dashboard sẽ tự động kết nối** với backend
3. **Theo dõi real-time:**
   - 📊 Traffic patterns (requests/minute)
   - 🔮 Predictions (1, 5, 15 phút)
   - 🖥️ Server count và scaling events
   - 💰 Cost analysis
   - ⚡ System utilization

---

## 🐳 Chạy với Docker (Khuyến nghị)

### Yêu cầu

- **Docker Desktop** (Windows/Mac) hoặc **Docker Engine** (Linux)
- **Docker Compose** (thường đi kèm Docker Desktop)

### Cài đặt Docker

**Windows/Mac:**
- Tải Docker Desktop: https://www.docker.com/products/docker-desktop
- Cài đặt và khởi động Docker Desktop

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### Chạy với Docker - Cách đơn giản nhất 🚀

**Windows:**
```powershell
# Chỉ cần chạy 1 lệnh!
docker-run.bat
```

**Linux/Mac:**
```bash
# Cấp quyền thực thi (chỉ cần 1 lần)
chmod +x docker-run.sh

# Chạy
./docker-run.sh
```

Script sẽ tự động:
- ✅ Kiểm tra Docker
- ✅ Build containers (backend + frontend)
- ✅ Start services
- ✅ Mở browser tự động

**Hệ thống sẽ chạy tại:**
- 🌐 **Frontend Dashboard**: http://localhost
- 🔧 **Backend API**: http://localhost:5000

### Lệnh Docker nâng cao

**Build và start containers:**
```bash
docker-compose up -d
```

**Build lại (sau khi thay đổi code):**
```bash
docker-compose up --build -d
```

**Xem logs:**
```bash
# Xem tất cả logs
docker-compose logs -f

# Xem logs của backend
docker-compose logs -f backend

# Xem logs của frontend
docker-compose logs -f frontend
```

**Kiểm tra trạng thái containers:**
```bash
docker-compose ps
```

**Stop containers:**
```bash
# Dừng containers (giữ data)
docker-compose stop

# Hoặc dùng script
docker-stop.bat        # Windows
./docker-stop.sh       # Linux/Mac

# Stop và xóa containers
docker-compose down
```

**Restart containers:**
```bash
docker-compose restart
```

**Xem resource usage:**
```bash
docker stats
```

### Cấu trúc Docker

```
📁 predictive-server-autoscaling/
├── 📄 docker-compose.yml           # Orchestration file
├── 📄 docker-run.bat               # Windows run script
├── 📄 docker-run.sh                # Linux/Mac run script
├── 📄 docker-stop.bat              # Windows stop script
├── 📄 docker-stop.sh               # Linux/Mac stop script
│
├── 📁 backend/
│   ├── 📄 Dockerfile               # Backend container config
│   └── 📄 .dockerignore            # Files to exclude
│
└── 📁 frontend/
    ├── 📄 Dockerfile               # Frontend container config
    ├── 📄 nginx.conf               # Nginx config for production
    └── 📄 .dockerignore            # Files to exclude
```

### Troubleshooting Docker

**❌ "Docker is not running"**
```bash
# Khởi động Docker Desktop (Windows/Mac)
# Hoặc trên Linux:
sudo systemctl start docker
```

**❌ "Port already in use"**
```bash
# Kiểm tra port đang dùng
netstat -ano | findstr :5000    # Windows
lsof -i :5000                   # Linux/Mac

# Stop container đang chạy
docker-compose down
```

**❌ Containers bị lỗi**
```bash
# Xem logs để debug
docker-compose logs

# Rebuild từ đầu
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**❌ Thiếu dependencies**
```bash
# Xóa images cũ và rebuild
docker-compose down --rmi all
docker-compose up --build -d
```

### Ưu điểm của Docker

✅ **Không cần cài Python/Node.js** trên máy host  
✅ **Environment nhất quán** trên mọi hệ điều hành  
✅ **Dễ dàng deploy** lên production  
✅ **Tự động restart** khi có lỗi  
✅ **Isolated** - không ảnh hưởng system  
✅ **Scale dễ dàng** khi cần  

---

## 📊 Tính năng Dashboard

### 🎯 Real-time Monitoring
- **Current Traffic**: Hiển thị số requests/minute hiện tại
- **Predictions**: Dự báo traffic cho 1, 5, 15 phút tới
- **Active Servers**: Số lượng server đang hoạt động
- **System Utilization**: Tỷ lệ sử dụng tài nguyên (%)
- **Cost Tracking**: Chi phí vận hành theo giờ

### 📈 Interactive Charts
1. **Traffic Load Chart**: Biểu đồ so sánh actual vs predicted requests
2. **Server Count Chart**: Theo dõi số server qua thời gian
3. **Cost Analysis Chart**: Phân tích chi phí vận hành
4. **Predictions Panel**: Dự báo multi-interval với confidence scores
5. **Scaling Events Log**: Lịch sử các quyết định scaling
6. **System Information**: Cấu hình autoscaling

### ⚙️ Autoscaling Configuration

**Thông số mặc định:**
- **Min Servers**: 2
- **Max Servers**: 50
- **Target Utilization**: 70%
- **Scale-out Threshold**: 80% (scale out khi vượt)
- **Scale-in Threshold**: 50% (scale in khi dưới)
- **Requests per Server**: 200 requests/min
- **Cost per Server**: $0.50/hour

## 🔧 API Endpoints

### 1. Health Check
```http
GET /api/health
```
Kiểm tra trạng thái backend.

### 2. Get Forecast
```http
POST /api/forecast
Content-Type: application/json

{
  "current_time": "2024-01-01T10:30:00",
  "intervals": [1, 5, 15]
}
```

**Response:**
```json
{
  "timestamp": "2024-01-01T10:30:00",
  "predictions": [
    {
      "interval_minutes": 5,
      "predicted_requests": 150.5,
      "predicted_bytes": 3000000.0,
      "confidence": 0.87,
      "timestamp": "2024-01-01T10:35:00"
    }
  ],
  "status": "success"
}
```

### 3. Get Scaling Recommendation
```http
POST /api/recommend-scaling
Content-Type: application/json

{
  "current_servers": 5,
  "current_load": 850.0,
  "predicted_load": 1200.0,
  "current_utilization": 85.0
}
```

**Response:**
```json
{
  "timestamp": "2024-01-01T10:30:00",
  "current_servers": 5,
  "recommended_servers": 7,
  "action": "scale-out",
  "reason": "Predicted utilization (85.7%) exceeds threshold (80%)",
  "confidence": 0.9,
  "estimated_utilization": 71.4,
  "estimated_cost_change": 1.0
}
```

### 4. Get Historical Data
```http
GET /api/historical-data?interval=5m&limit=100
```

### 5. Get Metrics Summary
```http
GET /api/metrics/summary
```

### 6. Get Autoscaling Config
```http
GET /api/autoscaling/config
```

## 📁 Cấu trúc dữ liệu

### Dữ liệu đầu vào (NASA Logs)
- **Format**: ASCII text logs
- **Fields**: Host, Timestamp, Request, Status Code, Bytes
- **Period**: July 1 - August 31, 1995
- **Train Set**: Tháng 7 + 22 ngày đầu tháng 8
- **Test Set**: 23-31 tháng 8

### Features cho Model
```python
features = [
    'hour',           # Giờ trong ngày (0-23)
    'dayofweek',      # Thứ trong tuần (0-6)
    'is_weekend',     # Cuối tuần (0/1)
    'part_of_day',    # Buổi trong ngày (0-3)
    'hour_sin',       # Sin của giờ (cyclical)
    'hour_cos',       # Cos của giờ (cyclical)
    'lag_1',          # Requests 1 bước trước
    'lag_2',          # Requests 2 bước trước
    'lag_3',          # Requests 3 bước trước
    'rolling_mean',   # Mean của 3 bước trước
    'rolling_std',    # Std của 3 bước trước
    'rolling_max'     # Max của 3 bước trước
]
```

## 🎓 Machine Learning Models

### XGBoost Regressor
- **Framework**: XGBoost 2.0.2
- **Task**: Regression (dự báo số requests)
- **Intervals**: 1 phút, 5 phút, 15 phút
- **Hyperparameters**:
  - `n_estimators`: ~200-500 (với early stopping)
  - `learning_rate`: 0.01
  - `max_depth`: 6
  - `objective`: reg:squarederror

### Evaluation Metrics
- **RMSE** (Root Mean Square Error)
- **MSE** (Mean Square Error)
- **MAE** (Mean Absolute Error)
- **MAPE** (Mean Absolute Percentage Error)

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **ML Library**: XGBoost 2.0.2
- **Data Processing**: Pandas, NumPy
- **Server**: Uvicorn (ASGI)

### Frontend
- **Language**: TypeScript 5.3.3
- **Build Tool**: Vite 5.0.8
- **Charts**: Chart.js 4.4.1
- **No Framework**: Vanilla TypeScript (no React/Vue)

## 📝 Notebooks

### 1. Data_Processing.ipynb
- Load raw NASA logs
- Parse log format
- Extract features
- Resample to 1m, 5m, 15m intervals
- Save processed data

### 2. Final_Solution.ipynb
- Feature engineering
- Train/validation/test split
- XGBoost model training
- Hyperparameter tuning
- Model evaluation
- Results visualization

### 3. Autoscaling_Optimization.ipynb
- Cost analysis
- Scaling policy design
- Performance vs cost trade-offs

## 🧪 Testing

### Test Backend API
```powershell
# Test health endpoint
curl http://localhost:5000/api/health

# Test forecast endpoint
curl -X POST http://localhost:5000/api/forecast ^
  -H "Content-Type: application/json" ^
  -d "{\"current_time\":\"2024-01-01T10:00:00\",\"intervals\":[5]}"
```

### Test Frontend
1. Mở http://localhost:3000
2. Kiểm tra connection status
3. Verify các charts hiển thị đúng
4. Test predictions panel
5. Kiểm tra scaling events log

## 🐛 Troubleshooting

### Backend không start
- **Kiểm tra port 5000**: `netstat -ano | findstr :5000`
- **Cài lại dependencies**: `pip install -r backend/requirements.txt`
- **Kiểm tra Python version**: `python --version` (cần 3.8+)

### Frontend không kết nối Backend
- **Kiểm tra CORS**: Backend có enabled CORS
- **Verify backend URL**: Trong `frontend/src/api.ts`, check `API_BASE_URL`
- **Kiểm tra browser console**: F12 để xem errors

### Charts không hiển thị
- **Clear cache**: Ctrl+Shift+R
- **Kiểm tra Chart.js**: `npm list chart.js`
- **Check browser console**: Tìm JavaScript errors

## 📚 Tài liệu tham khảo

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [Chart.js Documentation](https://www.chartjs.org/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [NASA Logs Dataset](http://ita.ee.lbl.gov/html/contrib/NASA-HTTP.html)

## 👥 Team & Contact

**Project**: Predictive Server Autoscaling
**Competition**: DATAFLOW 2026 - The Alchemy of Minds
**Organization**: Câu lạc bộ Toán Tin HAMIC

## 📄 License

MIT License - See LICENSE file for details

---

**© 2026 Predictive Server Autoscaling System**
- **Scale-in Threshold**: 40% utilization  
- **Cooldown Period**: 5 minutes
- **Cost per Server**: $0.10/hour

### Demo Settings:
- **Streaming Speed**: 1 second = 5 minutes real-time (có thể tua nhanh)
- **Prediction Intervals**: [1, 5, 15] phút
- **Test Dataset Period**: 23-31 August 1995 (9 days)
- **Data Points**: ~2,590 records (5-minute intervals)

## 📈 Demo Scenarios

### 🌊 Scenario 1: Normal Traffic
- Hệ thống duy trì 2-4 servers
- Utilization ổn định 40-60%
- Cost optimization focus

### 🚀 Scenario 2: Traffic Spike 
- Prediction phát hiện spike sớm
- Scale-out proactive trước khi overload
- Maintain performance SLA

### 📉 Scenario 3: Traffic Drop
- Scale-in sau khi traffic giảm
- Cost saving optimization
- Avoid over-provisioning

## 🔧 Technical Details

### 🔙 Backend Architecture (Flask)

**🎮 DemoOrchestrator**: 
- Coordinate tất cả services
- Real-time data flow management  
- API endpoint orchestration

**📊 DataStreamer**: 
- Sequential streaming từ test CSV
- Configurable speed (1s = 5min real-time)
- Event-driven architecture

**🔮 PredictionService**:
- Moving average + trend analysis
- Multi-interval predictions (1, 5, 15 min)
- Confidence scoring

**⚡ AutoscalingEngine**:
- Threshold-based scaling logic
- Consecutive period requirements
- Cooldown protection
- Cost tracking

### 🎨 Frontend Architecture (Vanilla TypeScript)

**📊 Chart.js Integration**: Real-time data visualization
**🔌 REST API Polling**: 2-second intervals
**📱 Responsive Design**: Works on desktop/mobile
**🔧 TypeScript**: Full type safety
**⚡ Vite**: Fast development server

## 📋 API Endpoints

```http
GET  /api/status           # Demo status và progress
POST /api/demo/start       # Bắt đầu streaming demo
POST /api/demo/stop        # Dừng streaming demo
POST /api/demo/reset       # Reset về đầu dataset
GET  /api/data/current     # Current real-time data  
GET  /api/data/historical  # Historical data cho charts
GET  /api/config           # Configuration settings
GET  /                     # API info và health check
```

## 🎮 Demo Flow

1. **📂 Data Loading**: Load test dataset từ data/test_dataset.csv
2. **▶️ Streaming Start**: Bắt đầu sequential data streaming
3. **⚡ Real-time Processing**:
   - Nhận data point mới mỗi 1 giây (= 5 phút real-time)
   - Generate traffic predictions cho 1, 5, 15 phút
   - Make scaling decisions dựa trên 5-min prediction
   - Update dashboard real-time
4. **📊 Visualization**: Charts update với new data
5. **📈 Monitoring**: Track cost, utilization, scaling events

## ⚡ Performance Features

- **⚡ Real-time Updates**: 2-second polling interval
- **📱 Responsive Design**: Desktop + mobile friendly
- **🔄 Error Handling**: Graceful connection management
- **💾 Memory Management**: Limited history retention (1000 events)
- **🛡️ Type Safety**: Full TypeScript coverage
- **🔧 Auto-recovery**: Handles backend disconnections

## 🛠️ Troubleshooting

### 🔙 Backend Issues

```bash
# Kiểm tra Python version (cần 3.8+)
python --version

# Kiểm tra test dataset
ls data/test_dataset.csv

# Xem logs backend
cd backend && python app.py

# Kiểm tra port 5000 
netstat -an | grep 5000
```

### 🎨 Frontend Issues

```bash
# Kiểm tra Node.js version (cần 18+)  
node --version

# Reinstall dependencies
cd frontend && npm install

# Kiểm tra port 3000
netstat -an | grep 3000

# Build production version
npm run build
```

### 📊 Data Issues  

```bash
# Re-generate test dataset nếu bị lỗi
cd backend && python extract_test_data.py

# Kiểm tra original logs
ls data/access_log_*.txt

# Xem sample test data
head data/test_dataset.csv
```

## 📝 Development Notes

### 🔮 Prediction Model
- Hiện tại sử dụng **simple moving average + linear trend**
- Có thể thay thế bằng **advanced ML models** từ notebook
- Confidence score dựa trên recent variance

### ⚡ Scaling Logic
- **Threshold-based** với consecutive period requirements
- **Cooldown protection** để tránh thrashing
- **Buffer scaling** (+1 server) cho safety margin

### 📊 Data Processing  
- **5-minute aggregation** từ raw logs
- **Real-time streaming** với configurable speed
- **Memory-efficient** với rolling history

### 🎨 Frontend Technology
- **Vanilla TypeScript** (không React) theo yêu cầu
- **Chart.js** cho data visualization
- **CSS Grid/Flexbox** cho responsive layout
- **REST API polling** thay vì WebSocket để đơn giản

---

**✨ Demo này thể hiện đầy đủ pipeline của Predictive Autoscaling System theo yêu cầu đề bài, sử dụng đúng Test Set (23-31/08/1995) để mô phỏng streaming real-time với frontend vanilla TypeScript.**