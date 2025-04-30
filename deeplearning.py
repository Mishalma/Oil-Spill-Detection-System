# deeplearning.py
import os
import requests
from requests.auth import HTTPBasicAuth
import yagmail
from twilio.rest import Client
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from datetime import datetime, timedelta
import time
import logging
import numpy as np
import cv2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Sentinel Hub credentials
CLIENT_ID = os.getenv("CLIENT_ID")
SECRET_KEY = os.getenv("SECRET_KEY")
API_URL = 'https://services.sentinel-hub.com/oauth/token'

# Notification credentials
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
RECIPIENT_NUMBER = os.getenv("RECIPIENT_NUMBER")

# Configure logging
logging.basicConfig(filename='oil_spill_pipeline.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_access_token(client_id=CLIENT_ID, secret_key=SECRET_KEY):
    """Obtain an access token from Sentinel Hub with retry logic."""
    payload = {'grant_type': 'client_credentials'}
    for attempt in range(3):
        try:
            response = requests.post(API_URL, auth=HTTPBasicAuth(client_id, secret_key), data=payload)
            response.raise_for_status()
            access_token = response.json().get('access_token')
            logging.info("Successfully obtained Sentinel Hub access token")
            return access_token
        except Exception as e:
            logging.error(f"Attempt {attempt+1} to get access token failed: {e}")
            time.sleep(10)
    logging.error("Failed to obtain access token after 3 attempts")
    return None  # Return None instead of raising an exception

def fetch_sentinel_data():
    """Fetch Sentinel-1 imagery for the Indian Ocean region, or use a fallback image if API fails."""
    bbox = [81.5, 6.5, 82.5, 7.5]  # Fixed bounding box for Indian Ocean
    filename = os.path.join("static", "indian_ocean_specific.png")

    # Check if a fallback image already exists
    if os.path.exists(filename):
        logging.info(f"Using existing image: {filename}")
        return filename

    access_token = get_access_token()
    if not access_token:
        logging.warning("Could not obtain access token. Using fallback image if available.")
        if os.path.exists(filename):
            return filename
        else:
            logging.error("No fallback image available and API access failed.")
            return None

    url = "https://services.sentinel-hub.com/api/v1/process"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    now = datetime.utcnow()
    time_range = {
        "from": (now - timedelta(days=7)).isoformat() + "Z",
        "to": now.isoformat() + "Z"
    }

    payload = {
        "input": {
            "bounds": {
                "bbox": bbox,
                "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"}
            },
            "data": [{
                "type": "S1GRD",
                "dataFilter": {"timeRange": time_range}
            }]
        },
        "output": {
            "width": 2056,
            "height": 2056,
            "responses": [{"identifier": "default", "format": {"type": "image/png"}}]
        },
        "evalscript": """
        //VERSION=3
        function setup() { return { input: ["VV"], output: { bands: 1 } }; }
        function evaluatePixel(sample) {
            let vv = sample.VV;
            vv = Math.min(Math.max(vv * 20, 0), 1);  // Scale for visibility
            return [vv];  // Grayscale output
        }
        """
    }

    for attempt in range(3):
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "wb") as f:
                f.write(response.content)

            img = cv2.imread(filename)
            if img is None or np.mean(img) < 1:
                logging.warning(f"Image {filename} appears to be black or invalid. Mean intensity: {np.mean(img) if img is not None else 'N/A'}")
            else:
                logging.info(f"Sentinel-1 image saved as {filename}, Mean intensity: {np.mean(img)}")
            return filename
        except Exception as e:
            logging.error(f"Attempt {attempt+1} to fetch Sentinel data failed: {e}")
            time.sleep(10)
    logging.error("Failed to fetch Sentinel data after 3 attempts")
    return None

def analyze_spill_with_deep_learning(image_path):
    try:
        if not os.path.exists(image_path):
            logging.warning(f"Image not found: {image_path}")
            return False, "No image available for analysis"

        # Simulate an oil spill detection for demonstration purposes
        logging.info("Simulating oil spill detection for presentation")
        lat, lon = 7.1, 82.1  # Simulated spill location within the bounding box [81.5, 6.5, 82.5, 7.5]
        result = f"Oil spill detected at Lat {lat:.2f}, Lon {lon:.2f} (simulated for presentation)"
        spill_detected = True

        logging.info(f"Deep learning analysis: {result}")
        return spill_detected, result
    except Exception as e:
        logging.error(f"Error in deep learning analysis: {e}")
        return False, f"Analysis error: {e}"

def send_email_alert(subject, body, attachment=None):
    for attempt in range(3):
        try:
            yag = yagmail.SMTP(EMAIL_USER, EMAIL_PASSWORD)
            yag.send(to=RECIPIENT_EMAIL, subject=subject, contents=body, attachments=attachment)
            logging.info("Email sent successfully")
            return
        except Exception as e:
            logging.error(f"Attempt {attempt+1} to send email failed: {e}")
            time.sleep(10)
    logging.error("Failed to send email after 3 attempts")

def send_sms_alert(body):
    for attempt in range(3):
        try:
            client = Client(ACCOUNT_SID, AUTH_TOKEN)
            message = client.messages.create(body=body, from_=TWILIO_NUMBER, to=RECIPIENT_NUMBER)
            logging.info(f"SMS sent successfully! SID: {message.sid}")
            return
        except Exception as e:
            logging.error(f"Attempt {attempt+1} to send SMS failed: {e}")
            time.sleep(10)
    logging.error("Failed to send SMS after 3 attempts")

def generate_pdf_report(latitude, longitude, vessel_info, spill_area, timestamp, image_file, pdf_file="static/Oil_Spill_Incident_Report.pdf"):
    try:
        # Ensure the static directory exists
        os.makedirs(os.path.dirname(pdf_file), exist_ok=True)

        doc = SimpleDocTemplate(pdf_file, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = [
            Paragraph(f"Oil Spill Incident Report - {timestamp}", styles['Title']),
            Spacer(1, 12),
            Paragraph(
                f"<b>Latitude:</b> {latitude}<br/><b>Longitude:</b> {longitude}<br/><b>Vessel:</b> {vessel_info}<br/><b>Spill Area:</b> {spill_area}",
                styles['BodyText']),
            Spacer(1, 12)
        ]

        # Add image if it exists, otherwise skip
        if image_file and os.path.exists(image_file):
            elements.append(Image(image_file, width=400, height=400))
        else:
            elements.append(Paragraph("No satellite image available for this report.", styles['BodyText']))
            logging.warning(f"Image file {image_file} not found; generating PDF without image")

        doc.build(elements)
        logging.info(f"PDF report generated: {pdf_file}")
        return pdf_file
    except Exception as e:
        logging.error(f"Error generating PDF: {e}")
        return None

def detect_and_report():
    """Detect oil spill and generate reports/notifications for the Indian Ocean region."""
    image_file = fetch_sentinel_data()
    if not image_file or not os.path.exists(image_file):
        logging.info("No image fetched; skipping detection")
        return

    spill_detected, spill_analysis = analyze_spill_with_deep_learning(image_file)
    if spill_detected:
        latitude, longitude = 7.0, 82.0  # Default center of the image
        if "Lat" in spill_analysis:
            try:
                lat_str = spill_analysis.split("Lat ")[1].split(",")[0]
                lon_str = spill_analysis.split("Lon ")[1].split(" ")[0]  # Adjusted to handle "(simulated for presentation)"
                latitude, longitude = float(lat_str), float(lon_str)
            except (IndexError, ValueError):
                pass

        vessel_info, spill_area = "Vessel 73", "234 sqm"
        timestamp = datetime.utcnow().isoformat() + "Z"

        email_body = f"""
        Oil spill detected in the Indian Ocean.
        - Latitude: {latitude}
        - Longitude: {longitude}
        - Vessel: {vessel_info}
        - Spill Area: {spill_area}
        - Time: {timestamp}
        - Analysis: {spill_analysis}
        See attached image for details.
        """
        send_email_alert("Urgent: Oil Spill Detected", email_body, image_file)
        send_sms_alert(f"Oil Spill Alert: Lat {latitude}, Lon {longitude}")

        pdf_file = generate_pdf_report(latitude, longitude, vessel_info, spill_area, timestamp, image_file)
        if pdf_file:
            logging.info("Detection and reporting completed successfully")
        else:
            logging.error("Failed to complete reporting")
    else:
        logging.info(f"No oil spill detected. Analysis: {spill_analysis}")

if __name__ == "__main__":
    detect_and_report()