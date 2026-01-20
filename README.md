# 🌱 AI-Based Farming Dashboard

An intelligent agricultural dashboard that empowers farmers with AI-driven insights for crop management, disease detection, soil health analysis, market trends, and weather forecasting.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Installation & Setup](#installation--setup)
- [API Endpoints](#api-endpoints)
- [Frontend Pages](#frontend-pages)
- [Configuration](#configuration)
- [Deployment](#deployment)

---

## 🎯 Project Overview

This is a **full-stack farming advisory system** that combines:
- **Machine Learning Models** for disease detection, soil nutrient analysis, and price prediction
- **Real-time Weather Data** from Open-Meteo API
- **AI-Powered Chatbot** using Google Gemini 2.5 Flash
- **Interactive React Dashboard** with Shadcn UI components
- **Rule-Based & ML-Driven Recommendations** for crop and fertilizer management

**Target Users:** Farmers in Karnataka, India (extensible to other regions)

---

## ✨ Features

### 1. 🌾 Disease Diagnosis (Crop Doctor)
- Upload plant images for AI-powered disease detection
- Returns disease name in Kannada (phonetic English)
- Provides 3+ treatment options available in Indian markets
- Region-specific advice for Karnataka areas (Mandya, Dharwad, Shimoga)

### 2. 🧪 Soil Health Analysis
- Analyzes soil nutrient levels (Nitrogen, Phosphorus, Potassium)
- Considers environmental factors (pH, temperature, humidity, rainfall)
- Recommends fertilizers with:
  - Dosage per acre
  - Application timing
  - Expected benefits
  - Impact if ignored
- Calculates soil health score (40-100)
- Estimates yield improvement percentage
- Provides confidence percentage for recommendations

### 3. 🌤️ Weather Forecasting
- Real-time current weather (temperature, humidity, wind speed)
- 7-day forecast with daily highs/lows and precipitation
- Location-based (Bangalore, extendable to other regions)

### 4. 💰 Market Price Prediction
- Predict crop prices by district and commodity
- Market trend analysis for profit planning
- Helps farmers make informed selling decisions

### 5. 🤖 AI Assistant Chatbot
- Powered by Google Gemini 2.5 Flash
- Answers farming-related questions
- Topics: crop selection, market trends, weather insights, farming practices
- Provides concise, easy-to-understand responses

### 6. 🌱 Crop Recommendation
- AI-powered crop suggestions based on soil and climate
- Sentiment analysis of crop health
- Market viability assessment

### 7. 📊 Yield Planning
- Forecast crop yield based on input parameters
- Historical data analysis
- Growth projection tools

### 8. 🔐 User Authentication
- Secure login system
- Session persistence with localStorage
- Farmer profile management
- Dual role support: Farmers & Farm Heads

### 9. 📍 Supply Chain & Logistics
- Food surplus & deficit mapping
- Route optimization for food distribution
- Farmer location visualization
- Shipment tracking and planning
- Shelf life prediction for perishables

---

## 📁 Project Structure

```
EL_3/
├── .gitignore                          # Git ignore rules
├── README.md                           # Project documentation
│
├── scripts/                            # Backend Python modules
│   ├── __init__.py                     # Python package marker
│   └── backend/
│       ├── __init__.py                 # Python package marker
│       ├── app.py                      # Main Flask application (all endpoints)
│       ├── disease_classifier.py       # Plant disease detection model
│       ├── sentiment_analyser_model.py # Crop sentiment analysis
│       ├── database/
│       │   ├── __init__.py            # Python package marker
│       │   ├── db.py                   # Database connection manager
│       │   ├── init_db.py              # Database initialization & schema
│       │   └── agriculture.db          # SQLite database
│       ├── price_predictor/
│       │   ├── app.py                  # Price prediction model
│       │   └── models/
│       │       └── global_lstm.h5      # Trained LSTM model
│       ├── static/
│       │   └── maps/                   # Generated logistics maps (not committed)
│       ├── surplus_deficit/            # Supply chain & logistics module
│       │   ├── __init__.py            # Python package marker
│       │   ├── requirements.txt        # Logistics dependencies
│       │   ├── data/
│       │   │   ├── clustered_data.csv
│       │   │   ├── farmer_map.html
│       │   │   ├── optimized_shipments_with_latlon.csv
│       │   │   └── processed_data.csv  # (not committed)
│       │   └── scripts/
│       │       ├── __init__.py        # Python package marker
│       │       ├── add_latlon.py
│       │       ├── clustering_and_coords.py
│       │       ├── data_preprocessing.py
│       │       ├── farmer_api.py
│       │       ├── farmer_map.py
│       │       ├── optimization.py
│       │       ├── results_analysis.py
│       │       ├── shelf_life_prediction.py
│       │       ├── visualization_routes.py  # Logistics map visualization
│       │       └── requirements.txt
│       └── requirements.txt            # Backend dependencies
│
├── soil_nutrient_recommender/          # Soil nutrient analysis module
│   ├── .gitignore
│   ├── nutrient_model.py              # Soil nutrient analyzer script
│   ├── soil_nutrient_model.pkl        # Trained ML model (not committed)
│   ├── Crop_recommendation.csv        # Training dataset
│   └── requirements.txt                # Module dependencies
│
└── prompt-genie-main/                  # React Frontend
    ├── public/
    │   └── robots.txt
    ├── src/
    │   ├── App.tsx                     # Main application component
    │   ├── App.css
    │   ├── index.css
    │   ├── main.tsx                    # React entry point
    │   ├── pages/
    │   │   ├── Login.tsx              # Farmer login page
    │   │   ├── Signup.tsx             # Farmer registration
    │   │   ├── Dashboard.tsx          # Main dashboard with weather
    │   │   ├── AIAssistant.tsx        # Chatbot interface
    │   │   ├── CropDoctor.tsx         # Disease diagnosis
    │   │   ├── SoilHealth.tsx         # Soil analysis
    │   │   ├── Climate.tsx            # Weather forecasting
    │   │   ├── MarketProfit.tsx       # Price prediction
    │   │   ├── CropRecommendation.tsx # Crop suggestions
    │   │   ├── YieldPlanning.tsx      # Yield forecasting
    │   │   └── NotFound.tsx           # 404 error page
    │   ├── components/
    │   │   ├── NavLink.tsx            # Navigation link component
    │   │   ├── layout/
    │   │   │   ├── DashboardLayout.tsx    # Main layout wrapper
    │   │   │   ├── Sidebar.tsx            # Navigation sidebar
    │   │   │   └── TopBar.tsx             # Top navigation bar
    │   │   └── ui/                    # Shadcn UI components
    │   │       └── (30+ reusable components)
    │   ├── contexts/
    │   │   ├── AuthContext.tsx        # User authentication state
    │   │   ├── FarmerSelectionContext.tsx  # Selected farmer for farm heads
    │   │   └── LanguageContext.tsx    # Multi-language support
    │   ├── hooks/
    │   │   ├── use-mobile.tsx         # Mobile screen detection
    │   │   ├── use-toast.ts           # Toast notification hook
    │   │   └── useWeather.ts          # Weather data hook
    │   ├── lib/
    │   │   └── utils.ts               # Utility functions
    │   ├── data/
    │   │   └── cropDistrictMap.ts     # Crop-district mapping
    │   └── test/
    │       ├── example.test.ts
    │       └── setup.ts
    ├── package.json                    # Frontend dependencies
    ├── vite.config.ts                  # Vite build configuration
    ├── tsconfig.json                   # TypeScript configuration
    ├── tailwind.config.ts              # Tailwind CSS configuration
    ├── postcss.config.js               # PostCSS configuration
    ├── eslint.config.js                # ESLint configuration
    ├── components.json                 # Shadcn UI config
    ├── index.html                      # HTML entry point
    └── README.md
```
    │   │
    │   ├── components/
    │   │   ├── layout/
    │   │   │   ├── DashboardLayout.tsx # Main layout wrapper
    │   │   │   ├── Sidebar.tsx         # Navigation sidebar
    │   │   │   └── TopBar.tsx          # Header component
    │   │   ├── ui/                     # Shadcn UI components
    │   │   └── NavLink.tsx             # Navigation helper
    │   │
    │   ├── contexts/
    │   │   ├── AuthContext.tsx         # User auth state + localStorage
    │   │   └── LanguageContext.tsx     # Multi-language support
    │   │
    │   ├── hooks/
    │   │   ├── use-mobile.tsx          # Mobile detection hook
    │   │   └── use-toast.ts            # Toast notification hook
    │   │
    │   ├── lib/
    │   │   └── utils.ts                # Utility functions
    │   │
    │   ├── App.tsx                     # Main app component
    │   ├── main.tsx                    # React entry point
    │   └── index.css                   # Global styles
    │
    ├── public/
    ├── package.json                    # Node dependencies
    ├── vite.config.ts                  # Vite build config
    ├── tailwind.config.ts              # Tailwind CSS config
    ├── tsconfig.json                   # TypeScript config
    └── index.html                      # HTML entry point
```

---

## 🛠️ Tech Stack

### Backend
| Component | Technology |
|-----------|-----------|
| Framework | Flask (Python) |
| API Type | RESTful JSON API |
| CORS | Flask-CORS |
| AI Models | scikit-learn, TensorFlow/PyTorch (pickled) |
| External AI | Google Gemini 2.5 Flash API |
| Weather Data | Open-Meteo API (free, no auth) |
| Environment | Python 3.8+ |

### Frontend
| Component | Technology |
|-----------|-----------|
| Framework | React 18+ |
| Language | TypeScript |
| Build Tool | Vite |
| Styling | Tailwind CSS |
| UI Components | Shadcn UI (Radix UI based) |
| State Management | React Context API |
| HTTP Client | Fetch API |
| Testing | Vitest |

### Deployment
| Component | Details |
|-----------|---------|
| Backend Server | Flask (localhost:5000 or cloud) |
| Frontend Server | Vite dev server (localhost:5173) |
| CORS Policy | Enabled for frontend-backend communication |

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or bun package manager
- Google Gemini API Key

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd scripts/backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set environment variables:**
```bash
export GOOGLE_API_KEY="your-gemini-api-key"
# On Windows: set GOOGLE_API_KEY=your-gemini-api-key
```

5. **Install surplus deficit module dependencies (optional):**
```bash
pip install -r surplus_deficit/requirements.txt
```

6. **Run Flask server:**
```bash
python app.py
```
Server will start on `http://0.0.0.0:5000`

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd prompt-genie-main
```

2. **Install dependencies:**
```bash
npm install
# or
bun install
```

3. **Start development server:**
```bash
npm run dev
# or
bun run dev
```
Frontend will start on `http://localhost:5173`

### Important Notes

#### Python Module Structure
- The `scripts/` directory is a Python package with `__init__.py` files
- Backend imports use relative paths: `from backend.surplus_deficit.scripts import visualization_routes`
- Path resolution is handled automatically by Python's module system

#### Path Handling in Python Scripts
- Logistics visualization uses relative paths via `os.path` for cross-platform compatibility
- Example: `os.path.join(script_dir, "..", "data")` to resolve data directory
- This ensures scripts work regardless of where the project is located

---

## 🔌 API Endpoints

### Authentication Endpoints

#### 1. **Farmer Signup**
```
POST /api/auth/farmer/signup
Content-Type: application/json

Request:
{
  "username": "farmer123",
  "password": "secure_password",
  "full_name": "Rajesh Kumar",
  "village": "Mandya",
  "district": "Mandya",
  "latitude": 12.5,         // Optional
  "longitude": 75.8         // Optional
}

Response (201 Created):
{
  "success": true,
  "message": "Farmer account created successfully"
}

Error (409 Conflict):
{
  "error": "Username already exists"
}
```

#### 2. **Farmer Login**
```
POST /api/auth/farmer/login
Content-Type: application/json

Request:
{
  "username": "farmer123",
  "password": "secure_password"
}

Response (200 OK):
{
  "success": true,
  "farmer": {
    "id": 1,
    "username": "farmer123",
    "village": "Mandya",
    "district": "Mandya"
  }
}

Error (401 Unauthorized):
{
  "error": "Invalid username or password"
}
```

#### 3. **Farmer Head Signup**
```
POST /api/auth/head/signup
Content-Type: application/json

Request:
{
  "username": "head_user",
  "password": "secure_password",
  "full_name": "Officer Name",
  "role": "head"           // Optional, default: "head"
}

Response (201 Created):
{
  "success": true,
  "message": "Farmer head account created successfully"
}
```

#### 4. **Farmer Head Login**
```
POST /api/auth/head/login
Content-Type: application/json

Request:
{
  "username": "head_user",
  "password": "secure_password"
}

Response (200 OK):
{
  "success": true,
  "head": {
    "id": 1,
    "username": "head_user",
    "full_name": "Officer Name",
    "role": "head"
  }
}
```

---

### Soil & Nutrient Analysis

#### 5. **Soil Nutrient Recommendation**
```
POST /nutrient
Content-Type: application/json

Request:
{
  "nitrogen": 45,           // kg/acre (required)
  "phosphorus": 25,         // kg/acre (required)
  "potassium": 35,          // kg/acre (required)
  "temperature": 28.5,      // °C (required)
  "humidity": 65,           // % (required)
  "ph": 6.8,                // 0-14 (required)
  "rainfall": 500           // mm (required)
}

Response (200 OK):
{
  "success": true,
  "soil_analysis": {
    "nitrogen": {
      "status": "Low",
      "severity": "Moderate",
      "value": 45
    },
    "phosphorus": {
      "status": "Low",
      "severity": "Moderate",
      "value": 25
    },
    "potassium": {
      "status": "Low",
      "severity": "Normal",
      "value": 35
    }
  },
  "soil_health_score": 55,
  "issues_identified": ["Urea", "DAP"],
  "recommendations": [
    {
      "fertilizer": "Urea",
      "dosage": "45–50 kg per acre",
      "timing": "Early vegetative stage",
      "benefit": "Improves leaf growth and green colour",
      "if_ignored": "Poor leaf growth and reduced yield"
    },
    {
      "fertilizer": "DAP",
      "dosage": "40–45 kg per acre",
      "timing": "At sowing time",
      "benefit": "Improves root development and flowering",
      "if_ignored": "Weak roots and poor flowering"
    }
  ],
  "expected_yield_improvement": "25–30%",
  "confidence_percentage": 87,
  "sustainability_note": "Avoid over-application. Excess fertilizer can damage soil health."
}

Error (400 Bad Request):
{
  "error": "Missing required fields: temperature, humidity"
}
```

---

### Disease Detection & Plant Health

#### 6. **Plant Disease Diagnosis**
```
POST /api/diagnose
Content-Type: multipart/form-data

Request: Image file in "file" field (JPG, PNG)

Response (200 OK):
{
  "status": "success",
  "plant": "Tomato",
  "disease": "Early Blight",
  "karnataka_advice": "Kannada name: Tomatina Moggu (ಟೊಮ್ಯಾಟಿನ ಮೊಗ್ಗು)\n\nTreatments:\n1. Copper sulfate spray (Bordeaux mixture 1%)\n2. Chlorothalonil fungicide (5 ml per 10L water)\n3. Mancozeb 75% WP (2.5g per liter)\n\nCommon in Mandya and Shimoga districts during monsoon season."
}

Error (400 Bad Request):
{
  "error": "No image uploaded"
}
```

#### 7. **Crop Sentiment Analysis**
```
GET /analyze/<crop>

Example: GET /analyze/rice

Response (200 OK):
{
  "crop": "rice",
  "sentiment": "positive",
  "market_trend": "increasing",
  "recommendation": "Good time to sell"
}

Or with negative sentiment:
{
  "crop": "cotton",
  "sentiment": "negative",
  "market_trend": "decreasing",
  "recommendation": "Hold inventory; prices may recover"
}
```

---

### Weather & Climate Data

#### 8. **Weather Forecast**
```
GET /api/weather

Response (200 OK):
{
  "current_weather": {
    "time": "2026-01-17T10:00",
    "temperature": 28.5,
    "wind_speed": 12.3,
    "humidity": 65,
    "unit": "°C"
  },
  "seven_day_forecast": [
    {
      "date": "2026-01-17",
      "temp_max": 32.1,
      "temp_min": 22.5,
      "precipitation": 0.0
    },
    {
      "date": "2026-01-18",
      "temp_max": 31.5,
      "temp_min": 21.8,
      "precipitation": 2.5
    },
    ...
  ]
}

Error (500 Internal Server Error):
{
  "error": "Failed to retrieve data: Connection timeout"
}
```

**Data Source:** Open-Meteo Free API (Bangalore coordinates)

---

### Market & Price Prediction

#### 9. **Market Price Prediction**
```
GET /predict?district=Mandya&commodity=Rice

Required Query Parameters:
- district: District name (e.g., Mandya, Dharwad, Bangalore)
- commodity: Crop name (e.g., Rice, Wheat, Cotton)

Response (200 OK):
{
  "predicted_price": 2450,
  "currency": "INR",
  "unit": "per quintal",
  "confidence": 0.87,
  "trend": "stable"
}

Error (400 Bad Request):
{
  "error": "Both 'district' and 'commodity' query parameters are required"
}
```

**Model:** LSTM Neural Network trained on historical market data

---

### AI Assistant

#### 10. **AI Chatbot (Gemini)**
```
POST /api/assistant
Content-Type: application/json

Request:
{
  "message": "What should I plant in my soil with low nitrogen?"
}

Response (200 OK):
{
  "reply": "Based on your low nitrogen levels, I recommend growing legumes like chickpea or lentil, which can fix nitrogen naturally. You can also consider nitrogen-fixing cover crops like clover before your main crop. This will help restore soil nitrogen balance sustainably."
}

Error (400 Bad Request):
{
  "error": "Please enter a message."
}
```

**AI Model:** Google Gemini 2.5 Flash

---

## � State Management (React Contexts)

### AuthContext
Manages user authentication state and login/logout operations.

**Provided Values:**
- `user`: Current logged-in user object
- `role`: User role ('farmer' or 'head')
- `login()`: Function to authenticate user
- `logout()`: Function to clear authentication

### FarmerSelectionContext
Allows farm heads to select a specific farmer to view their data.

**Provided Values:**
- `selectedFarmer`: Currently selected farmer object
- `setSelectedFarmer()`: Function to update selected farmer
- `farmers`: List of available farmers (for farm heads)

### LanguageContext
Provides multi-language support for the dashboard.

**Provided Values:**
- `language`: Current language setting
- `t()`: Translation function for getting localized strings
- `setLanguage()`: Function to change language

---

## 📱 Frontend Pages

| Page | Route | Purpose |
|------|-------|---------|
| Dashboard | `/` | Overview of farm metrics & quick stats with weather |
| Login | `/login` | User authentication (farmer & farm head) |
| Soil Health | `/soil-health` | Nutrient analysis & fertilizer recommendations |
| Crop Doctor | `/crop-doctor` | Disease detection via plant image upload |
| Climate | `/climate` | Weather forecasts & climate risk assessment |
| Market Profit | `/market-profit` | Price predictions & market trend analysis |
| Crop Recommendation | `/crop-recommendation` | AI-suggested crops based on conditions |
| Yield Planning | `/yield-planning` | Yield forecasting & growth projections |
| AI Assistant | `/ai-assistant` | Chatbot interface for farming advice |
| Not Found | `/404` | Error page for undefined routes |

---

## ⚙️ Configuration

### Environment Variables (Backend)
```bash
GOOGLE_API_KEY=your-gemini-api-key-here
FLASK_ENV=development
FLASK_DEBUG=True
```

### Weather API Configuration
- **Provider:** Open-Meteo (free, no authentication required)
- **Location:** Bangalore (lat: 12.9, long: 77.58)
- **Data Points:** Current weather + 7-day forecast
- **Update Frequency:** Real-time

### Soil Nutrient Thresholds
- **Nitrogen (N):** Low < 50, High > 120 kg/acre
- **Phosphorus (P):** Low < 30, High > 80 kg/acre
- **Potassium (K):** Low < 30, High > 80 kg/acre

### Authentication
- Stores user session in **localStorage** for persistence
- Survives page refresh
- Logout clears session

---

## �️ Database Structure

The application uses **SQLite** for data persistence. Database file: `scripts/backend/database/agriculture.db`

### Table: `farmers`
Stores individual farmer profiles and login credentials.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Unique farmer identifier |
| `username` | TEXT UNIQUE NOT NULL | Login username |
| `password_hash` | TEXT NOT NULL | Hashed password (bcrypt) |
| `full_name` | TEXT | Farmer's full name |
| `phone` | TEXT | Contact number |
| `email` | TEXT | Email address |
| `village` | TEXT NOT NULL | Village name |
| `district` | TEXT NOT NULL | District (e.g., Mandya, Dharwad) |
| `state` | TEXT DEFAULT 'Karnataka' | State (default: Karnataka) |
| `latitude` | REAL | GPS latitude |
| `longitude` | REAL | GPS longitude |
| `created_at` | DATETIME DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |
| `last_login` | DATETIME | Last login timestamp |
| `is_active` | INTEGER DEFAULT 1 | Account status (0=inactive, 1=active) |

### Table: `farmer_crops`
Tracks crops planted by each farmer.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Unique crop record ID |
| `farmer_id` | INTEGER NOT NULL | Foreign key to `farmers` table |
| `crop_name` | TEXT NOT NULL | Name of crop (e.g., Rice, Wheat) |
| `season` | TEXT | Growing season (Kharif/Rabi) |
| `area_acres` | REAL | Area planted in acres |
| `sowing_date` | DATE | Date of sowing |
| `expected_harvest` | DATE | Expected harvest date |
| `is_active` | INTEGER DEFAULT 1 | Crop status (0=harvested, 1=active) |

**Relationships:** `farmer_id` → `farmers.id`

### Table: `soil_reports`
Stores soil nutrient analysis results.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Unique report ID |
| `farmer_id` | INTEGER NOT NULL | Foreign key to `farmers` table |
| `nitrogen` | REAL NOT NULL | Nitrogen level (kg/acre) |
| `phosphorus` | REAL NOT NULL | Phosphorus level (kg/acre) |
| `potassium` | REAL NOT NULL | Potassium level (kg/acre) |
| `ph` | REAL | Soil pH value |
| `temperature` | REAL | Temperature (°C) at testing |
| `humidity` | REAL | Humidity (%) at testing |
| `rainfall` | REAL | Annual rainfall (mm) |
| `soil_health_score` | INTEGER | Overall health score (40-100) |
| `confidence_percentage` | INTEGER | Model confidence level (0-100%) |
| `created_at` | DATETIME DEFAULT CURRENT_TIMESTAMP | Test date/time |

**Relationships:** `farmer_id` → `farmers.id`

### Table: `disease_reports`
Records plant disease diagnoses and treatments.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Unique diagnosis ID |
| `farmer_id` | INTEGER NOT NULL | Foreign key to `farmers` table |
| `crop_name` | TEXT | Name of affected crop |
| `disease_name` | TEXT | Identified disease name |
| `severity` | TEXT | Severity level (Low/Moderate/High) |
| `image_path` | TEXT | Path to uploaded plant image |
| `ai_advice` | TEXT | Gemini-generated treatment advice |
| `created_at` | DATETIME DEFAULT CURRENT_TIMESTAMP | Diagnosis timestamp |

**Relationships:** `farmer_id` → `farmers.id`

### Table: `farmer_heads`
Stores data for agricultural extension officers/supervisors.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Unique head identifier |
| `username` | TEXT UNIQUE NOT NULL | Login username |
| `password_hash` | TEXT NOT NULL | Hashed password |
| `full_name` | TEXT | Full name |
| `role` | TEXT DEFAULT 'head' | Role type (e.g., 'head', 'supervisor') |
| `created_at` | DATETIME DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |
| `last_login` | DATETIME | Last login timestamp |
| `is_active` | INTEGER DEFAULT 1 | Account status (0=inactive, 1=active) |

### Table: `farmer_access`
Manages access control between heads and farmers.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Unique access record ID |
| `head_id` | INTEGER NOT NULL | Foreign key to `farmer_heads` table |
| `farmer_id` | INTEGER NOT NULL | Foreign key to `farmers` table |
| `can_view_soil` | INTEGER DEFAULT 1 | Permission to view soil reports (0/1) |
| `can_view_crops` | INTEGER DEFAULT 1 | Permission to view crop data (0/1) |
| `can_view_disease` | INTEGER DEFAULT 1 | Permission to view disease reports (0/1) |
| `granted_at` | DATETIME DEFAULT CURRENT_TIMESTAMP | Access grant timestamp |
| `UNIQUE(head_id, farmer_id)` | — | One access record per head-farmer pair |

**Relationships:**
- `head_id` → `farmer_heads.id`
- `farmer_id` → `farmers.id`

### Database Initialization
Initialize the database by running:
```bash
cd scripts/backend/database
python init_db.py
```
This will create all tables with proper constraints and relationships.

---

## �🚀 Deployment

### Backend Deployment (Flask)
```bash
# Production server (Gunicorn recommended)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Frontend Deployment (Vite)
```bash
# Build for production
npm run build

# Output: dist/ folder
# Deploy to Vercel, Netlify, GitHub Pages, or any static host
```

### Docker Deployment (Optional)
Create `Dockerfile` and `docker-compose.yml` for containerized deployment.

---

## 📊 Data Flow

```
User (Frontend React)
    ↓
API Request (JSON)
    ↓
Flask Backend
    ├─ Disease Classification Model
    ├─ Soil Nutrient ML Model
    ├─ Price Prediction Model
    ├─ Open-Meteo Weather API
    └─ Google Gemini 2.5 Flash API
    ↓
JSON Response
    ↓
React Component (Display Data)
    ↓
User Dashboard
```

---

## 🔐 Security Features

- ✅ CORS enabled for secure frontend-backend communication
- ✅ Environment variable for sensitive API keys
- ✅ Input validation on all endpoints
- ✅ Error handling with proper HTTP status codes
- ✅ Session persistence with localStorage (client-side)

---

## 🎓 Model Information

### Soil Nutrient Model
- **Type:** Hybrid (Rule-based + ML confidence scoring)
- **Input Features:** N, P, K, temperature, humidity, pH, rainfall
- **Output:** Fertilizer recommendations + confidence %
- **File:** `soil_nutrient_model.pkl`

### Disease Classifier
- **Input:** Plant leaf image
- **Output:** Disease name, severity, treatment options
- **Regionalization:** Uses Gemini to localize for Karnataka

### Price Predictor
- **Input:** District, commodity name
- **Output:** Predicted price, confidence level
- **Update Frequency:** Based on market data updates

---

## 📞 Support & Troubleshooting

### Backend won't start
```
Error: GOOGLE_API_KEY not set
→ Set environment variable: export GOOGLE_API_KEY="your-key"
```

### CORS errors on frontend
→ Ensure `CORS(app)` is enabled in `app.py`

### Model not loading
→ Check file path: `../../soil_nutrient_recommender/soil_nutrient_model.pkl`

### Weather API timeout
→ Open-Meteo might be temporarily unavailable; try again in a few moments

---

## 📝 License

This project is developed for agricultural advisory. Use responsibly and always validate with agronomists before making farming decisions.

---

## 👥 Contributors

- **Project Lead:** Sudeep Xavier Roche
- **Backend Development:** Flask API & ML Integration
- **Frontend Development:** React Dashboard with Shadcn UI
- **ML Models:** Disease detection, soil analysis, price prediction

---

## 🌱 Future Enhancements

- [ ] Multi-region support (beyond Karnataka)
- [ ] IoT sensor integration for real-time soil monitoring
- [ ] Mobile app (React Native)
- [ ] Multilingual interface (Hindi, Kannada, Tamil, Telugu)
- [ ] Drone image analysis for large-scale farm monitoring
- [ ] Farmer community forum
- [ ] Video tutorials in regional languages
- [ ] Integration with agriculture extension services

---

**Last Updated:** January 17, 2026
