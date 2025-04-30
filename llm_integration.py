# llm_integration.py
import os
import logging
import time
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure logging
logging.basicConfig(filename='oil_spill_pipeline.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Validate API key
if not GEMINI_API_KEY:
    logging.error("GEMINI_API_KEY not found in environment variables")
    raise ValueError("GEMINI_API_KEY is required in .env file")
genai.configure(api_key=GEMINI_API_KEY)

def query_gemini(prompt, max_retries=3):
    """Query the Gemini 1.5 Flash model with retry logic."""
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt, generation_config={"max_output_tokens": 150, "temperature": 0.7})
            if hasattr(response, 'text'):
                result = response.text
            elif response.candidates and response.candidates[0].content.parts:
                result = response.candidates[0].content.parts[0].text
            else:
                raise ValueError("No valid text found in Gemini response")
            logging.info(f"Gemini 1.5 Flash response: {result}")
            return result
        except Exception as e:
            logging.error(f"Attempt {attempt + 1} failed querying Gemini 1.5 Flash: {e}")
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
            else:
                return f"Error: Could not generate response from Gemini after {max_retries} attempts - {str(e)}"

def analyze_spill_report(lat, lon, vessel_info, spill_area, timestamp, image_file):
    """Analyze an oil spill report with India’s NOS-DCP compliance."""
    prompt = (
        f"Analyze this oil spill report for an Indian government authority:\n"
        f"- Latitude: {lat}\n"
        f"- Longitude: {lon}\n"
        f"- Vessel: {vessel_info}\n"
        f"- Spill Area: {spill_area}\n"
        f"- Timestamp: {timestamp}\n"
        f"The image is located at {image_file} (assume it shows an oil spill in the Indian Ocean).\n"
        f"Provide a short summary (1-2 sentences) and recommendations (3-5 brief bullet points, each under 10 words) that comply with India's National Oil Spill Disaster Contingency Plan (NOS-DCP). "
        f"Recommendations must include: 1) Notify Indian Coast Guard and DG Shipping, 2) Deploy containment equipment per ICG approval, 3) Coordinate with NOSRT, 4) Monitor spill via satellite, 5) Protect marine ecosystems like coral reefs."
    )
    return query_gemini(prompt)

def interactive_query(query):
    """Handle interactive queries with India’s NOS-DCP compliance."""
    prompt = (
        f"User query about an oil spill for an Indian government authority: '{query}'.\n"
        f"Provide a concise response (1-2 sentences, under 20 words) that complies with India's National Oil Spill Disaster Contingency Plan (NOS-DCP), focusing on ICG-led protocols."
    )
    return query_gemini(prompt)

if __name__ == "__main__":
    print(analyze_spill_report(19.0, 72.8, "Vessel 73", "234 sqm", "2025-03-17 10:30 UTC", "static/oil_spill_detection_gulf.png"))