from flask import Flask
from flask_cors import CORS # 1. Import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db
from flask import jsonify, request
from disease_classifier import diagnose_plant_image
from sentiment_analyser_model import analyze_crop
from price_predictor.app import predict
import google.generativeai as genai
import requests
import os
import pickle
import sys



app = Flask(__name__)
CORS(app) # 2. Enable CORS

#genai API CONFIG
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("GOOGLE_API_KEY not set in environment")
genai.configure(api_key=api_key)





# ==========================================================
# SOIL NUTRIENT MODEL SETUP
# ==========================================================
def load_nutrient_model():
    """Load the trained soil nutrient recommendation model"""
    try:
        model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'soil_nutrient_recommender', 'soil_nutrient_model.pkl')
        model = pickle.load(open(model_path, "rb"))
        return model
    except Exception as e:
        print(f"Warning: Could not load nutrient model: {e}")
        return None

nutrient_model = load_nutrient_model()

def nutrient_status(value, low, high):
    """Determine nutrient status"""
    if value < low:
        return "Low"
    elif value > high:
        return "High"
    else:
        return "Medium"

def severity_level(value, low):
    """Determine severity level of deficiency"""
    if value < low * 0.7:
        return "High"
    elif value < low:
        return "Moderate"
    else:
        return "Normal"

def soil_health_score(statuses):
    """Calculate overall soil health score"""
    score = 100
    for s in statuses:
        if s == "Low":
            score -= 15
        elif s == "High":
            score -= 5
    return max(score, 40)

# Knowledge base for recommendations
DOSAGE_MAP = {
    "Urea": "45–50 kg per acre",
    "DAP": "40–45 kg per acre",
    "MOP": "20–25 kg per acre",
    "None": "Not required"
}

TIMING_MAP = {
    "Urea": "Early vegetative stage",
    "DAP": "At sowing time",
    "MOP": "During soil preparation",
    "None": "No application required"
}

BENEFIT_MAP = {
    "Urea": "Improves leaf growth and green colour",
    "DAP": "Improves root development and flowering",
    "MOP": "Improves disease resistance and crop quality",
    "None": "Soil nutrients are balanced"
}

IMPACT_MAP = {
    "Urea": "Poor leaf growth and reduced yield",
    "DAP": "Weak roots and poor flowering",
    "MOP": "Low disease resistance and poor fruit quality"
}




def get_weather():
    # Bangalore Coordinates
    lat = 12.9
    long =  77.58
    
    # API Endpoint with parameters for current weather and 7-day daily forecast
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": long,
        "current": ["temperature_2m", "wind_speed_10m", "relative_humidity_2m"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
        "timezone": "auto",  # Automatically detects Asia/Kolkata for these coordinates
        "forecast_days": 7
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Check for HTTP errors
        data = response.json()

        # Extract Current Weather
        current = data.get("current", {})
        
        # Extract and format 7-Day Forecast
        daily = data.get("daily", {})
        forecast = []
        for i in range(len(daily.get("time", []))):
            forecast.append({
                "date": daily["time"][i],
                "temp_max": daily["temperature_2m_max"][i],
                "temp_min": daily["temperature_2m_min"][i],
                "precipitation": daily["precipitation_sum"][i]
            })

        return {
            "current_weather": {
                "time": current.get("time"),
                "temperature": current.get("temperature_2m"),
                "wind_speed": current.get("wind_speed_10m"),
                "humidity": current.get("relative_humidity_2m"),
                "unit": "°C"
            },
            "seven_day_forecast": forecast
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to retrieve data: {str(e)}"}



#===========================================
#                   ROUTES 
#===========================================
@app.route("/api/auth/farmer/signup", methods=["POST"])
def farmer_signup():
    data = request.get_json()

    required = ["username", "password", "village", "district"]
    missing = [f for f in required if f not in data]

    if missing:
        return jsonify({
            "error": f"Missing fields: {', '.join(missing)}"
        }), 400

    username = data["username"].strip()
    password = data["password"]

    password_hash = generate_password_hash(password)

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO farmers (
                username, password_hash,
                full_name, village, district,
                latitude, longitude
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            username,
            password_hash,
            data.get("full_name"),
            data["village"],
            data["district"],
            data.get("latitude"),
            data.get("longitude")
        ))

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Farmer account created successfully"
        }), 201

    except Exception as e:
        return jsonify({
            "error": "Username already exists"
        }), 409

    finally:
        conn.close()


@app.route("/api/auth/farmer/login", methods=["POST"])
def farmer_login():
    data = request.get_json()

    if "username" not in data or "password" not in data:
        return jsonify({
            "error": "Username and password required"
        }), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, username, password_hash, village, district
        FROM farmers
        WHERE username = ? AND is_active = 1
    """, (data["username"],))

    farmer = cursor.fetchone()
    conn.close()

    if not farmer:
        return jsonify({
            "error": "Invalid username or password"
        }), 401

    if not check_password_hash(farmer["password_hash"], data["password"]):
        return jsonify({
            "error": "Invalid username or password"
        }), 401

    return jsonify({
        "success": True,
        "farmer": {
            "id": farmer["id"],
            "username": farmer["username"],
            "village": farmer["village"],
            "district": farmer["district"]
        }
    })



@app.route("/api/auth/head/signup", methods=["POST"])
def farmer_head_signup():
    data = request.get_json()

    required = ["username", "password"]
    missing = [f for f in required if f not in data]

    if missing:
        return jsonify({
            "error": f"Missing fields: {', '.join(missing)}"
        }), 400

    username = data["username"].strip()
    password = data["password"]
    role = data.get("role", "head")

    password_hash = generate_password_hash(password)

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO farmer_heads (
                username, password_hash,
                full_name, role
            )
            VALUES (?, ?, ?, ?)
        """, (
            username,
            password_hash,
            data.get("full_name"),
            role
        ))

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Farmer head account created successfully"
        }), 201

    except Exception:
        return jsonify({
            "error": "Username already exists"
        }), 409

    finally:
        conn.close()


@app.route("/api/auth/head/login", methods=["POST"])
def farmer_head_login():
    data = request.get_json()

    if "username" not in data or "password" not in data:
        return jsonify({
            "error": "Username and password required"
        }), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, username, password_hash, full_name, role
        FROM farmer_heads
        WHERE username = ? AND is_active = 1
    """, (data["username"],))

    head = cursor.fetchone()
    conn.close()

    if not head:
        return jsonify({
            "error": "Invalid username or password"
        }), 401

    if not check_password_hash(head["password_hash"], data["password"]):
        return jsonify({
            "error": "Invalid username or password"
        }), 401

    return jsonify({
        "success": True,
        "head": {
            "id": head["id"],
            "username": head["username"],
            "full_name": head["full_name"],
            "role": head["role"]
        }
    })



@app.route("/analyze/<crop>", methods=["GET"])
def analyze(crop: str):
    return analyze_crop(crop)

@app.route("/api/weather", methods=["GET"])
def weather():
    return get_weather()

from flask import request

@app.get("/predict")
def prediction():
    district = request.args.get("district")
    commodity = request.args.get("commodity")

    if not district or not commodity:
        return {
            "error": "Both 'district' and 'commodity' query parameters are required"
        }, 400

    return predict(district, commodity)


@app.route("/api/assistant", methods=["POST"])
def assistant():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please enter a message."}), 400


    prompt = f"""
You are a highly knowledgeable assistant for an agricultural dashboard that helps farmers with overall farming advice, crop selection, market trends, and weather insights.
Your task is to provide concise and accurate answers to user queries based on the following

Rules:
- Be concise and to the point
- Use simple language that is easy to understand
- Do not share any sensitive information
- If you do not know the answer, respond with "I'm sorry, I don't have that information."
User question:
{user_message}
"""
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)

    return jsonify({
        "reply": response.text
    })


@app.route("/api/diagnose", methods=["POST"])
def diagnose():
    if 'file' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files['file']
    image_bytes = file.read()
    
    # 1. Local AI Model diagnosis
    result = diagnose_plant_image(image_bytes)
    
    if result["status"] == "success":
        # 2. Use Gemini to provide localized advice for Karnataka
        # This makes the "Generic" AI model feel regional.
        local_prompt = f"""
        A farmer in Karnataka has a {result['plant']} plant with {result['disease']}.
        1. Give the name of this disease in Kannada (phonetic English).
        2. Provide 3 specific organic or chemical treatments available in Indian markets.
        3. Mention if this is common in regions like Mandya, Dharwad, or Shimoga.
        Keep it very brief (max 100 words).
        """
        
        model = genai.GenerativeModel("gemini-2.5-flash")
        ai_response = model.generate_content(local_prompt)
        result["karnataka_advice"] = ai_response.text
    return jsonify(result)


@app.route("/nutrient", methods=["POST"])
def soil_nutrient_recommendation():
    """
    Analyzes soil nutrient levels and provides fertilizer recommendations.
    
    Expected JSON input:
    {
        "nitrogen": float,      # N level in kg/acre
        "phosphorus": float,    # P level in kg/acre
        "potassium": float,     # K level in kg/acre
        "temperature": float,   # Temperature in °C
        "humidity": float,      # Humidity in %
        "ph": float,            # Soil pH value
        "rainfall": float       # Rainfall in mm
    }
    """
    
    try:
        print("_______________________________________________________________________________")
        data = request.get_json()
        # Validate required fields
        required_fields = [
            "farmer_id",
            "nitrogen", "phosphorus", "potassium",
            "temperature", "humidity", "ph", "rainfall"
        ]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        try:
            farmer_id = int(data["farmer_id"])
        except (ValueError, TypeError):
            return jsonify({
                "error": "farmer_id must be a valid integer"
            }), 400
        
        print("RAW REQUEST DATA:", data)

        # Extract and validate inputs
        try:
            N = float(data["nitrogen"])
            P = float(data["phosphorus"])
            K = float(data["potassium"])
            temperature = float(data["temperature"])
            humidity = float(data["humidity"])
            ph = float(data["ph"])
            rainfall = float(data["rainfall"])
        except ValueError:
            return jsonify({
                "error": "All fields must be numeric values"
            }), 400
        
        # Perform soil analysis
        N_status = nutrient_status(N, 50, 120)
        P_status = nutrient_status(P, 30, 80)
        K_status = nutrient_status(K, 30, 80)
        
        N_sev = severity_level(N, 50)
        P_sev = severity_level(P, 30)
        K_sev = severity_level(K, 30)
        
        statuses = [N_status, P_status, K_status]
        health_score = soil_health_score(statuses)
        
        # Generate multi-nutrient recommendations
        recommendations = []
        yield_gain = 0
        
        if N_status == "Low":
            recommendations.append("Urea")
            yield_gain += 15
        
        if P_status == "Low":
            recommendations.append("DAP")
            yield_gain += 10
        
        if K_status == "Low":
            recommendations.append("MOP")
            yield_gain += 10
        
        if not recommendations:
            recommendations.append("None")
        
        # Calculate model confidence
        confidence = 85  # default fallback
        if nutrient_model:
            try:
                prob = max(nutrient_model.predict_proba([[N, P, K, temperature, humidity, ph, rainfall]])[0])
                confidence = int(prob * 100)
            except:
                pass
        
        # Build detailed recommendations
        detailed_recommendations = []
        for fertilizer in recommendations:
            if fertilizer != "None":
                detailed_recommendations.append({
                    "fertilizer": fertilizer,
                    "dosage": DOSAGE_MAP[fertilizer],
                    "timing": TIMING_MAP[fertilizer],
                    "benefit": BENEFIT_MAP[fertilizer],
                    "if_ignored": IMPACT_MAP[fertilizer]
                })
        
        if not detailed_recommendations:
            detailed_recommendations.append({
                "fertilizer": "None",
                "dosage": "Not required",
                "timing": "No application required",
                "benefit": "Soil nutrients are well balanced",
                "if_ignored": None
            })
        

        #insert into database
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO soil_reports (
                    farmer_id,
                    nitrogen, phosphorus, potassium,
                    ph, temperature, humidity, rainfall,
                    soil_health_score, confidence_percentage
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                farmer_id,
                N, P, K,
                ph, temperature, humidity, rainfall,
                health_score, confidence
            ))

            conn.commit()
            conn.close()
            print(f"✅ Soil report saved successfully for farmer_id: {farmer_id}")
        except Exception as db_error:
            print(f"❌ Database error while saving soil report: {str(db_error)}")
            return jsonify({
                "error": f"Failed to save soil report to database: {str(db_error)}"
            }), 500


        # Build response
        return jsonify({
            "success": True,
            "soil_analysis": {
                "nitrogen": {
                    "status": N_status,
                    "severity": N_sev,
                    "value": N
                },
                "phosphorus": {
                    "status": P_status,
                    "severity": P_sev,
                    "value": P
                },
                "potassium": {
                    "status": K_status,
                    "severity": K_sev,
                    "value": K
                }
            },
            "soil_health_score": health_score,
            "issues_identified": [r for r in recommendations if r != "None"],
            "recommendations": detailed_recommendations,
            "expected_yield_improvement": f"{yield_gain}–{yield_gain + 5}%" if yield_gain > 0 else "Yield expected to remain stable",
            "confidence_percentage": confidence,
            "sustainability_note": "Avoid over-application. Excess fertilizer can damage soil health."
        })
    
    except Exception as e:
        return jsonify({
            "error": f"Error processing request: {str(e)}"
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)