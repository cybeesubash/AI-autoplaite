# AI-Theft-Vehicle-Tracke
# 🚗 AI Theft Vehicle Tracker

> **AI-powered vehicle theft detection, tracking, and alert system**

AI Theft Vehicle Tracker is an intelligent security platform designed to detect suspicious vehicle movement, identify stolen vehicles using number-plate recognition, track authorized vehicles using GPS/IoT devices, and generate real-time alerts.

## 🎯 Problem Statement

Vehicle theft is a major security problem. Traditional GPS trackers can provide location information, but they generally do not provide intelligent theft detection or automated vehicle identification.

This project combines **AI + Computer Vision + GPS + IoT + Real-Time Monitoring** to create a smarter vehicle security system.

## 💡 Solution

The system combines:

* 🤖 AI-based vehicle detection
* 🔢 Automatic Number Plate Recognition (ANPR)
* 📍 GPS-based vehicle tracking
* 🚨 Theft and tamper detection
* 🗺️ Real-time location monitoring
* 🧠 AI-powered risk analysis
* 🔔 Real-time alerts
* 📊 Security dashboard

## 🏗️ System Architecture

```text
                    ┌─────────────────┐
                    │   CCTV / Camera │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Vehicle Detection│
                    │     YOLO        │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ ANPR + OCR      │
                    │ Number Plate    │
                    └────────┬────────┘
                             │
                             ▼
              ┌──────────────────────────┐
              │      AI Risk Engine      │
              └────────────┬─────────────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
      ┌──────────────┐            ┌──────────────┐
      │ Stolen Vehicle│            │ GPS / IoT    │
      │ Database      │            │ Tracker      │
      └──────┬───────┘            └──────┬───────┘
             │                           │
             └─────────────┬─────────────┘
                           ▼
                  ┌─────────────────┐
                  │ Alert Engine     │
                  └────────┬────────┘
                           ▼
             ┌─────────────────────────┐
             │ Owner / Security       │
             │ Monitoring Dashboard   │
             └─────────────────────────┘
```

## 🔥 Key Features

### 1. Vehicle Detection

Detect vehicles from CCTV/video streams using computer vision.

Supported detection can include:

* Cars
* Motorcycles
* Buses
* Trucks
* Other configured vehicle classes

### 2. Number Plate Recognition

The system extracts vehicle registration numbers from camera footage using:

```text
Camera
   ↓
Vehicle Detection
   ↓
Number Plate Detection
   ↓
OCR
   ↓
Registration Number
```

### 3. Stolen Vehicle Matching

Detected registration numbers are compared against an authorized test database.

```text
Detected Plate
      ↓
Normalize Plate
      ↓
Database Search
      ↓
Match?
 ┌────┴────┐
YES       NO
 ↓         ↓
ALERT     NORMAL
```

### 4. GPS Tracking

An authorized IoT tracker can periodically transmit:

* Latitude
* Longitude
* Timestamp
* Device status
* Speed
* Movement status

### 5. Geofencing

Define an authorized geographical area.

Example:

```text
Vehicle enters allowed zone
        ↓
       SAFE

Vehicle leaves zone
        ↓
   Suspicious Event
        ↓
     AI Analysis
        ↓
      Alert
```

### 6. Tamper Detection

The system can detect suspicious tracker/device events such as:

* Unexpected device disconnect
* Tracker offline
* Sudden movement
* GPS signal interruption
* Unauthorized movement

### 7. AI Risk Score

The system generates a risk level based on multiple signals.

| Risk        | Example                             |
| ----------- | ----------------------------------- |
| 🟢 LOW      | Normal vehicle movement             |
| 🟡 MEDIUM   | Geofence violation                  |
| 🟠 HIGH     | Suspicious movement + tracker event |
| 🔴 CRITICAL | Stolen-vehicle database match       |

### 8. Real-Time Dashboard

Dashboard can display:

* Vehicle status
* Current location
* Last known location
* Number plate
* Risk score
* Alerts
* Movement history
* Camera detections
* Device health

## 🧠 AI Pipeline

```text
Video Stream
     ↓
YOLO Vehicle Detection
     ↓
Vehicle Tracking
     ↓
Plate Detection
     ↓
OCR
     ↓
Plate Normalization
     ↓
Database Matching
     ↓
Risk Analysis
     ↓
Alert Generation
```

## 🛠️ Technology Stack

### Frontend

* React.js
* Tailwind CSS
* JavaScript / TypeScript
* Map integration
* WebSocket client

### Backend

* Python
* FastAPI
* REST API
* WebSockets

### AI / Computer Vision

* YOLO
* OpenCV
* OCR
* NumPy
* PyTorch

### Database

* PostgreSQL
* Supabase

### IoT

* ESP32
* GPS module
* Optional vehicle sensors

### Infrastructure

* Docker
* GitHub
* Cloud deployment
* HTTPS

## 📁 Project Structure

```text
ai-theft-vehicle-tracker/
│
├── frontend/
│   ├── src/
│   ├── components/
│   ├── pages/
│   └── services/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── models/
│   │   ├── services/
│   │   └── database/
│   │
│   └── requirements.txt
│
├── ai/
│   ├── vehicle_detection/
│   ├── plate_detection/
│   ├── ocr/
│   └── risk_engine/
│
├── iot/
│   ├── esp32/
│   └── gps/
│
├── database/
│   └── schema.sql
│
├── docs/
│   ├── architecture/
│   └── screenshots/
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## 🔐 Security Design

Security is a core component of the system.

### API Security

* JWT authentication
* Role-based access control
* Input validation
* Rate limiting
* Secure API endpoints

### IoT Security

* Device authentication
* Encrypted communication
* Device identity
* Secure telemetry transmission

### Data Security

* Password hashing
* Database access control
* Environment variables for secrets
* HTTPS/TLS
* Audit logging

## 🗄️ Example Database Model

### Vehicles

```text
vehicles
├── id
├── registration_number
├── vehicle_type
├── make
├── model
├── color
├── owner_id
├── status
└── created_at
```

### GPS Telemetry

```text
gps_telemetry
├── id
├── vehicle_id
├── latitude
├── longitude
├── speed
├── timestamp
└── device_status
```

### Alerts

```text
alerts
├── id
├── vehicle_id
├── alert_type
├── severity
├── message
├── location
├── timestamp
└── status
```

## 🚨 Example Alert

```text
🚨 CRITICAL VEHICLE ALERT

Vehicle: TN XX XXXX
Event: Stolen Vehicle Match
Location: Test Location
Risk Score: 97/100
Detected At: 14:32:18

Action Required:
Verify the vehicle and follow authorized
security/law-enforcement procedures.
```

## 🚀 Installation

### Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-theft-vehicle-tracker.git

cd ai-theft-vehicle-tracker
```

### Backend

```bash
cd backend

python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run API:

```bash
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend

npm install

npm run dev
```

## ⚙️ Environment Variables

Create a `.env` file:

```env
DATABASE_URL=your_database_url

JWT_SECRET=your_secret

GPS_DEVICE_KEY=your_device_key

OCR_API_KEY=your_api_key

SUPABASE_URL=your_supabase_url

SUPABASE_KEY=your_supabase_key
```

**Never commit real API keys, passwords, JWT secrets, or device credentials to GitHub.**

## 📡 ESP32 Concept

The authorized GPS device can send telemetry:

```text
ESP32
  ↓
GPS Module
  ↓
Read Latitude / Longitude
  ↓
Create JSON Payload
  ↓
HTTPS
  ↓
FastAPI Backend
  ↓
Database
  ↓
Dashboard
```

Example telemetry:

```json
{
  "device_id": "VEHICLE-001",
  "latitude": 11.0168,
  "longitude": 76.9558,
  "speed": 42,
  "timestamp": "2026-09-09T12:30:00Z"
}
```

## 🧪 Testing

For development and hackathons, use:

* Simulated GPS coordinates
* Test vehicle numbers
* Sample CCTV footage
* Synthetic theft events
* Authorized test IoT devices

Do not use the system to track vehicles or individuals without proper authorization.

## 📊 Future Improvements

* 🔥 AI-based abnormal route detection
* 🧠 Vehicle re-identification
* 📹 Multi-camera tracking
* 🛰️ Advanced GPS anomaly detection
* 🗺️ Real-time fleet visualization
* 🤖 AI security assistant
* 📱 Mobile application
* 🔐 Zero-trust IoT architecture
* 📈 Theft hotspot analytics
* ☁️ Scalable cloud architecture

## 🎯 Project Goal

The ultimate goal is to build a **real-time AI-powered vehicle security platform** that combines:

```text
AI
+
Computer Vision
+
IoT
+
GPS
+
Cybersecurity
+
Real-Time Analytics
=
Smart Vehicle Theft Detection
```

## 👨‍💻 Author

**Subash Kumar**

Cyber Security Engineering Student

### Areas of Interest

* Cybersecurity
* AI Security
* Computer Vision
* Ethical Hacking
* IoT Security
* AI-powered Security Systems

## ⚠️ Disclaimer

This project is intended for **educational, research, and authorized security applications**.

Only monitor vehicles, devices, cameras, and data for which you have appropriate authorization. This project should not be used for unauthorized surveillance or tracking.

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐.

---

**Built with AI + Cybersecurity + IoT 🚀**

`AI Theft Vehicle Tracker`
