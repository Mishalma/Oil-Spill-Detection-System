# 🌊 Oil Spill Detection and Response System – Indian Ocean Region

A Python-based system that leverages Sentinel-1 satellite imagery and AIS vessel data to automatically detect oil spills along the Indian Ocean coast, identify suspicious vessel activities, and alert relevant stakeholders via email and SMS with a detailed PDF report.

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

📌 Workflow Architecture

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

Sentinel Hub API – for accessing Sentinel-1 SAR data

AIS CSV Data – Sample dataset: Ais_sample.csv

yagmail – Email notification service

twilio – SMS alert system

reportlab – PDF report generation

pandas, numpy, scikit-learn – Data analysis and ML

matplotlib, Pillow – Data visualization and image handling

dotenv – Secure environment variable management

📦 Installation
Clone the Repository
bash
Copy
Edit
git clone https://github.com/your-username/oil-spill-detection-mumbai.git
cd oil-spill-detection-mumbai
Set Up Environment Variables
Create a .env file and add the following:

env
Copy
Edit
# Sentinel Hub Credentials
SENTINELHUB_CLIENT_ID=your_client_id
SENTINELHUB_CLIENT_SECRET=your_client_secret

# Email Alert Configuration
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
EMAIL_RECEIVER=receiver_email@example.com

# SMS Alert Configuration
TWILIO_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE=+1234567890
RECEIVER_PHONE=+0987654321
🚀 Future Enhancements
🔁 Real-time automation on cloud (AWS/GCP/Azure)

🛰️ Use Sentinel-2 optical or drone data for cross-validation

🧠 Add deep learning-based segmentation (e.g., U-Net)

🌐 Interactive dashboard using Flask or Django

🗺️ Spatial analytics with GeoPandas and RasterIO

📈 Analyze historical spill patterns and trends

🛟 API integration with Indian Coast Guard/MoES

📜 License
This project is licensed under the MIT License. See the LICENSE file for details.

🙌 Acknowledgments
ESA Copernicus Programme – Sentinel-1 SAR Data

Sentinel Hub – Evalscript and API support

MarineTraffic – AIS datasets

Twilio – SMS delivery platform

ReportLab – PDF generation in Python

🧠 Maintainer
Mohammed Mishal
📧 mohammedmishal430@gmail.com
🌐 LinkedIn

