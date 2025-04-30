# app.py
from flask import Flask, render_template, request, url_for, send_from_directory
from pipeline import run_pipeline, automate_pipeline
import os
import threading
import logging
from deeplearning import fetch_sentinel_data, analyze_spill_with_deep_learning
from llm_integration import analyze_spill_report, interactive_query
from datetime import datetime

# Configure logging
logging.basicConfig(filename='oil_spill_pipeline.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Start the pipeline scheduler in a separate thread
def start_pipeline_scheduler():
    try:
        logging.info("Starting pipeline scheduler thread")
        automate_pipeline()
    except Exception as e:
        logging.error(f"Error in pipeline scheduler thread: {e}")

# Run the scheduler in a background thread when the app starts
scheduler_thread = threading.Thread(target=start_pipeline_scheduler, daemon=True)
scheduler_thread.start()

# Route for the opening page
@app.route("/")
def index():
    return render_template("opening.html")

# Route to serve the PDF file
@app.route("/download_pdf/<filename>")
def download_pdf(filename):
    try:
        return send_from_directory("static", filename, as_attachment=False)
    except Exception as e:
        logging.error(f"Error serving PDF file {filename}: {e}")
        return "PDF file not found", 404

# Route for the dashboard
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    # Ensure the static directory exists
    if not os.path.exists("static"):
        os.makedirs("static")
        logging.info("Created static directory")

    # Run the pipeline immediately to ensure PDF generation
    logging.info("Running pipeline for dashboard")
    try:
        run_pipeline()
    except Exception as e:
        logging.error(f"Error running pipeline for dashboard: {e}")

    # Default spill location (center of the satellite image bounding box)
    default_lat, default_lon = 7.0, 82.0  # Center of [81.5, 6.5, 82.5, 7.5]

    # Check for detected spill coordinates from the image
    image_file = os.path.join("static", "indian_ocean_specific.png")
    spill_detected, spill_analysis = analyze_spill_with_deep_learning(image_file) if os.path.exists(image_file) else (False, "No image available")
    if spill_detected and "Lat" in spill_analysis:
        try:
            lat_str = spill_analysis.split("Lat ")[1].split(",")[0]
            lon_str = spill_analysis.split("Lon ")[1].split(" ")[0]  # Adjusted for "(simulated for presentation)"
            lat, lon = float(lat_str), float(lon_str)
        except (IndexError, ValueError):
            lat, lon = default_lat, default_lon
    else:
        lat, lon = default_lat, default_lon

    # Spill data for the dashboard
    spill_data = {
        "lat": lat,
        "lon": lon,
        "vessel": "Vessel 73",
        "area": "234 sqm",
        "time": datetime.utcnow().isoformat() + "Z"
    }

    # File paths for static assets
    image_file = os.path.join("static", "indian_ocean_specific.png")
    anomaly_plot = os.path.join("static", "anomaly_plot.png")
    pdf_file = os.path.join("static", "Oil_Spill_Incident_Report.pdf")
    map_file = os.path.join("static", "spill_map.html")

    # Check if files exist
    image_exists = os.path.exists(image_file)
    anomaly_plot_exists = os.path.exists(anomaly_plot)
    pdf_exists = os.path.exists(pdf_file)
    map_exists = os.path.exists(map_file)
    latest_pdf = "Oil_Spill_Incident_Report.pdf" if pdf_exists else None

    # Log file existence
    if pdf_exists:
        logging.info(f"PDF file found: {pdf_file}")
    else:
        logging.warning(f"PDF file not found: {pdf_file}")

    # Run deep learning analysis if image exists (already done above, but keep for consistency)
    spill_detected, spill_analysis = analyze_spill_with_deep_learning(image_file) if image_exists else (False, "No image available")

    # Handle LLM response
    llm_response = None
    if request.method == "POST":
        query = request.form.get("query", "")
        llm_response = interactive_query(query) if query else "Please enter a query."
    else:
        llm_response = analyze_spill_report(
            spill_data["lat"],
            spill_data["lon"],
            spill_data["vessel"],
            spill_data["area"],
            spill_data["time"],
            image_file
        )

    return render_template(
        "index.html",
        spill_data=spill_data,
        image_exists=image_exists,
        anomaly_plot_exists=anomaly_plot_exists,
        latest_pdf=latest_pdf,
        pdf_exists=pdf_exists,
        map_exists=map_exists,
        llm_response=llm_response,
        spill_detected=spill_detected,
        spill_analysis=spill_analysis
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)