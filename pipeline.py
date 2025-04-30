# pipeline.py
import os
import logging
import time
import schedule
from dotenv import load_dotenv
from deeplearning import fetch_sentinel_data, analyze_spill_with_deep_learning, send_email_alert, send_sms_alert, generate_pdf_report
from main import haversine, predict_spill_spread, generate_anomaly_plot
from llm_integration import analyze_spill_report
import requests
import pandas as pd
from sklearn.ensemble import IsolationForest
from datetime import datetime, timedelta
import folium

# Load environment variables
load_dotenv()

# Credentials from .env
CLIENT_ID = os.getenv("CLIENT_ID")
SECRET_KEY = os.getenv("SECRET_KEY")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
RECIPIENT_NUMBER = os.getenv("RECIPIENT_NUMBER")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Configure logging
logging.basicConfig(filename='oil_spill_pipeline.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_weather_data(lat, lon):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        logging.error("OPENWEATHER_API_KEY not found in environment variables")
        return 5.0, 0
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
    try:
        response = requests.get(url).json()
        wind_speed = response["wind"]["speed"]
        wind_dir = response["wind"]["deg"]
        logging.info(f"Weather data fetched: Wind Speed {wind_speed} m/s, Direction {wind_dir}°")
        return wind_speed, wind_dir
    except Exception as e:
        logging.error(f"Failed to fetch weather data: {e}")
        return 5.0, 0

def process_ais_data():
    try:
        ais_data = pd.read_csv(os.path.join("data", "ais_sample.csv"), dtype={'ColumnName': 'str'}, low_memory=False)
        ais_data = ais_data.dropna()
        ais_data['BaseDateTime'] = pd.to_datetime(ais_data['BaseDateTime'], errors='coerce').dropna()
        ais_data = ais_data.sort_values(by=['MMSI', 'BaseDateTime']).reset_index(drop=True)

        ais_data['delta_sog'] = ais_data.groupby('MMSI')['SOG'].diff().fillna(0)
        ais_data['delta_cog'] = ais_data.groupby('MMSI')['COG'].diff().fillna(0)
        ais_data['prev_lon'] = ais_data.groupby('MMSI')['LON'].shift()
        ais_data['prev_lat'] = ais_data.groupby('MMSI')['LAT'].shift()
        ais_data['Distance_Traveled'] = ais_data.apply(
            lambda row: haversine(row['prev_lon'], row['prev_lat'], row['LON'], row['LAT']), axis=1).fillna(0)

        features = ['SOG', 'COG', 'delta_sog', 'delta_cog', 'Distance_Traveled']
        model = IsolationForest(contamination=0.01, random_state=42)
        ais_data['anomaly'] = model.fit_predict(ais_data[features])
        anomalies = ais_data[ais_data['anomaly'] == -1]

        generate_anomaly_plot(ais_data, anomalies, os.path.join("static", "anomaly_plot.png"))

        if not anomalies.empty:
            logging.info(f"Detected {len(anomalies)} anomalies")
            anomalies.to_csv(os.path.join("static", "anomalies.csv"), index=False)
            return anomalies.iloc[0]
        logging.info("No anomalies detected")
        return None
    except Exception as e:
        logging.error(f"Error processing AIS data: {e}")
        return None

def generate_map(lat, lon, spill_area, pred_lat, pred_lon):
    m = folium.Map(location=[lat, lon], zoom_start=8, tiles="CartoDB dark_matter")
    folium.Circle(
        location=[lat, lon],
        radius=(float(spill_area.split()[0]) ** 0.5) * 1000,
        color="red",
        fill=True,
        fill_opacity=0.4,
        popup="Oil Spill Location"
    ).add_to(m)
    folium.Marker(
        location=[pred_lat, pred_lon],
        popup=f"Predicted Spread: Lat {pred_lat:.4f}, Lon {pred_lon:.4f}",
        icon=folium.Icon(color="blue")
    ).add_to(m)
    map_file = os.path.join("static", "spill_map.html")
    m.save(map_file)
    logging.info(f"Map saved as {map_file}")
    return map_file

def run_pipeline():
    """Execute the oil spill detection pipeline for the Indian Ocean region."""
    logging.info("Starting pipeline run")

    image_file = fetch_sentinel_data()
    anomaly = process_ais_data()

    # Default spill location (center of the satellite image bounding box)
    default_lat, default_lon = 7.0, 82.0  # Center of [81.5, 6.5, 82.5, 7.5]

    if anomaly is not None or (image_file and os.path.exists(image_file)):
        # Check for oil spill in the image
        spill_detected, spill_analysis = analyze_spill_with_deep_learning(image_file) if image_file else (False, "No image available")
        logging.info(f"Spill detection result: {spill_detected}, Analysis: {spill_analysis}")

        # Use detected spill coordinates if available, otherwise use default
        if spill_detected and "Lat" in spill_analysis:
            try:
                # Extract lat/lon from spill_analysis (e.g., "Oil spill detected at Lat 7.1, Lon 82.1")
                lat_str = spill_analysis.split("Lat ")[1].split(",")[0]
                lon_str = spill_analysis.split("Lon ")[1].split(" ")[0]  # Adjusted for "(simulated for presentation)"
                lat, lon = float(lat_str), float(lon_str)
                logging.info(f"Using detected spill coordinates: Lat {lat}, Lon {lon}")
            except (IndexError, ValueError) as e:
                logging.warning(f"Could not parse spill coordinates from analysis: {spill_analysis}. Using default coordinates.")
                lat, lon = default_lat, default_lon
        else:
            lat, lon = default_lat, default_lon  # Use default if no spill detected
            logging.info(f"No spill detected or coordinates unavailable. Using default coordinates: Lat {lat}, Lon {lon}")

        # If AIS anomaly is detected, override with anomaly coordinates
        if anomaly is not None:
            lat, lon = anomaly['LAT'], anomaly['LON']
            logging.info(f"Using AIS anomaly coordinates: Lat {lat}, Lon {lon}")

        vessel_info, spill_area = "Vessel 73", "234 sqm"
        timestamp = datetime.utcnow().isoformat() + "Z"

        wind_speed, wind_dir = fetch_weather_data(lat, lon)
        pred_lat, pred_lon, pred_area = predict_spill_spread(lat, lon, float(spill_area.split()[0]), wind_speed, wind_dir)
        logging.info(f"Predicted spread: Lat {pred_lat:.4f}, Lon {pred_lon:.4f}, Area {pred_area:.0f} sqm")

        map_file = generate_map(lat, lon, spill_area, pred_lat, pred_lon)
        if map_file:
            logging.info(f"Map generation successful: {map_file}")
        else:
            logging.error("Map generation failed")

        llm_response = analyze_spill_report(lat, lon, vessel_info, spill_area, timestamp, image_file)

        if spill_detected:
            email_body = f"Oil spill detected at Lat {lat}, Lon {lon}, Vessel: {vessel_info}, Area: {spill_area}, Time: {timestamp}\nLLM: {llm_response}\nSatellite Analysis: {spill_analysis}"
            logging.info("Sending email alert")
            send_email_alert("Urgent: Oil Spill Detected", email_body, image_file)
            logging.info("Sending SMS alert")
            send_sms_alert(f"Oil Spill Alert: Lat {lat}, Lon {lon}")
        else:
            logging.info(f"No oil spill detected. Analysis: {spill_analysis}")

        pdf_file = generate_pdf_report(lat, lon, vessel_info, spill_area, timestamp, image_file)
        if pdf_file:
            logging.info(f"Pipeline run completed successfully. PDF saved as {pdf_file}")
        else:
            logging.error("Failed to generate PDF report")
    else:
        logging.info("No oil spill detected or image unavailable")

def automate_pipeline():
    """Schedule the pipeline to run every 2 minutes."""
    schedule.every(2).minutes.do(run_pipeline)
    logging.info("Pipeline scheduled to run every 2 minutes")
    while True:
        logging.info("Checking for scheduled pipeline runs")
        schedule.run_pending()
        time.sleep(10)

if __name__ == "__main__":
    if not os.path.exists("static"):
        os.makedirs("static")
    automate_pipeline()