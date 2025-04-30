# main.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(filename='oil_spill_pipeline.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def haversine(lon1, lat1, lon2, lat2):
    """Calculate the great circle distance between two points on Earth."""
    R = 6371  # Earth's radius in kilometers
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    distance = R * c * 1000  # Convert to meters
    return distance

def predict_spill_spread(lat, lon, area, wind_speed, wind_dir):
    """Predict the spread of an oil spill based on wind and initial area."""
    spread_factor = wind_speed * 0.1  # Simplified spread factor based on wind
    distance = spread_factor * 1000  # meters
    pred_lat = lat + (distance / 111320) * np.sin(np.radians(wind_dir))  # 111320m per degree latitude
    pred_lon = lon + (distance / (111320 * np.cos(np.radians(lat)))) * np.cos(np.radians(wind_dir))  # Adjust for longitude
    pred_area = area * 1.5  # Estimated area growth
    return pred_lat, pred_lon, pred_area

def generate_anomaly_plot(data, anomalies, output_path):
    """Generate and save an anomaly plot from AIS data."""
    # Set the Agg backend to avoid GUI issues
    plt.switch_backend('Agg')  # Use Agg backend for headless rendering

    plt.figure(figsize=(10, 6))
    plt.scatter(data['LON'], data['LAT'], c='blue', alpha=0.5, label='Normal')
    plt.scatter(anomalies['LON'], anomalies['LAT'], c='red', label='Anomalies')
    plt.title('AIS Data Anomalies')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.legend(loc="upper right")  # Specify legend location to avoid loc="best" warning
    plt.grid(True)

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)  # Save the plot to file
    logging.info(f"Anomaly plot saved to {output_path}")
    plt.close()  # Close the figure to free memory

if __name__ == "__main__":
    # Example usage (for testing)
    sample_data = pd.DataFrame({
        'LON': np.random.uniform(81.5, 82.5, 100),
        'LAT': np.random.uniform(6.5, 7.5, 100),
        'SOG': np.random.uniform(0, 20, 100),
        'COG': np.random.uniform(0, 360, 100)
    })
    anomalies = sample_data.sample(n=5)  # Simulate some anomalies
    generate_anomaly_plot(sample_data, anomalies, "static/anomaly_plot.png")