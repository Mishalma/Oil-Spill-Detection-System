# 🌊 Oil Spill Detection and Response System – Indian Ocean Region

A Python-based system that leverages Sentinel-1 satellite imagery and AIS vessel data to automatically detect oil spills along the Mumbai coast, identify suspicious vessel activities, and alert relevant stakeholders via email and SMS with a detailed PDF report.

---

## 📌 Table of Contents
- [Overview](#-overview)
- [Objectives](#-objectives)
- [Features](#-features)
- [Architecture](#-architecture)
- [Technologies Used](#-technologies-used)
- [Installation](#-installation)
- [Usage](#-usage)
- [Environment Variables](#-environment-variables)
- [Sample Output](#-sample-output)
- [Deployment Plan](#-deployment-plan)
- [Future Enhancements](#-future-enhancements)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

---

## 📖 Overview

The **Oil Spill Detection and Response System** is an end-to-end solution for real-time oil spill surveillance in Mumbai's coastal waters. It uses Sentinel-1 Synthetic Aperture Radar (SAR) data to detect oil spills and correlates anomalies from AIS data to identify potentially responsible vessels. When a spill is detected, it triggers automated email/SMS alerts and generates a PDF report with actionable insights.

---

## 🎯 Objectives

- Detect oil spills using Sentinel-1 SAR (VV polarization) data.
- Monitor and analyze AIS (Automatic Identification System) data for vessel anomaly detection.
- Correlate vessel behavior with detected spill locations and times.
- Notify stakeholders with spill coordinates, affected area, and suspected vessels.
- Generate a PDF report with embedded images and analysis.
- Design a modular and scalable system for reuse across regions.

---

## ✨ Features

- ✅ **Oil Spill Detection** from Sentinel-1 imagery
- 🚢 **AIS Vessel Anomaly Detection** using Isolation Forest
- 📬 **Email and SMS Alerts** to notify stakeholders
- 📄 **PDF Report Generation** with spill and vessel data
- 🗺️ **Geospatial Visualizations** of spills and vessel tracks
- 🔐 **Secure Credential Handling** via environment variables
- ☁️ **Scalable & Modular Design** for cloud deployment

---

## 🧠 Architecture

```text
                    +-----------------------+
                    | Sentinel-1 SAR Data   | <---- Sentinel Hub API
                    +-----------------------+
                               |
                               v
             +--------------------------------------+
             | Oil Spill Detection (evalscript)     |
             | - Image Processing & Thresholding    |
             | - Area Calculation                   |
             +--------------------------------------+
                               |
                               v
         +-------------------------------------------+
         | AIS Data Processing (Ais_sample.csv)       |
         | - Speed/Course/Distance Features           |
         | - Isolation Forest for Anomaly Detection   |
         +-------------------------------------------+
                               |
                               v
            +--------------------------------------+
            | Alerting System                      |
            | - Email via Gmail SMTP (yagmail)     |
            | - SMS via Twilio API                 |
            +--------------------------------------+
                               |
                               v
            +--------------------------------------+
            | Report Generator (reportlab)         |
            | - Coordinates, Area, Vessel Data     |
            | - Embedded Plots & Maps              |
            +--------------------------------------+


🛠 Technologies Used
Python 3.11

Sentinel Hub API (Sentinel-1 SAR)

AIS CSV Data (Sample: Ais_sample.csv)

yagmail, twilio – for email/SMS alerts

reportlab – PDF report generation

pandas, numpy, scikit-learn, matplotlib, Pillow

dotenv – Secure configuration handling

📦 Installation
Clone the Repository
bash
Copy
Edit
git clone https://github.com/your-username/oil-spill-detection-mumbai.git
cd oil-spill-detection-mumbai
Create Conda Environment
bash
Copy
Edit
conda env create -f environment.yml
conda activate oil_spill_detection
Install Additional Dependencies (if needed)
bash
Copy
Edit
pip install -r requirements.txt
🚀 Usage
Run the main detection script:

bash
Copy
Edit
python oil_spill_detection.py
Output files generated:

oil_spill_detection_mumbai.png – Binary spill map

ais_anomalies.png – Highlighted anomalous vessel movements

oil_spill_report.pdf – Detailed PDF report

Email and SMS sent to configured recipients

🔐 Environment Variables
Create a .env file in the root directory with the following:

env
Copy
Edit
SENTINELHUB_CLIENT_ID=your_client_id
SENTINELHUB_CLIENT_SECRET=your_client_secret

EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
EMAIL_RECEIVER=receiver_email@example.com

TWILIO_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE=+1234567890
RECEIVER_PHONE=+0987654321
🧪 Sample Output
📷 Oil Spill Map (Sentinel-1)

📉 Anomalous Vessel Movements

📄 PDF Report
oil_spill_report.pdf – Contains spill location, area estimate, suspected vessels, and plots.

📅 Deployment Plan
Development: Validate thresholds and pipeline on local machine.

Configuration: Setup .env, credentials, and API keys.

Scheduler: Deploy on server with cron or use AWS Lambda with event triggers.

Logging: Add logs and error handling for production use.

Monitoring: Monitor API quota, alert delivery, and storage usage.

🚀 Future Enhancements
🔁 Real-time automation via cloud server

🛰️ Integration with Sentinel-2 or drone-based imagery

🧠 Deep Learning-based segmentation for better accuracy

🌐 Web Dashboard using Flask/Django

🗺️ GIS Analysis with GeoPandas and RasterIO

📈 Historical spill pattern analysis

🛟 Integration with Marine Safety Authorities

📜 License
This project is licensed under the MIT License.

🙌 Acknowledgments
ESA Copernicus Programme – Sentinel-1 Data

Sentinel Hub – API access and evalscript support

MarineTraffic – AIS sample datasets

Twilio – SMS communication API

ReportLab – PDF generation in Python

🧠 Maintainer
Your Name
📧 your.email@example.com
🌐 LinkedIn
