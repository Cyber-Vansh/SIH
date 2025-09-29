
Rockfall Prediction MVP - Generated Artifacts
============================================

Files generated (in this folder):
- probability_map.csv : CSV grid with coordinates, elevation, slope, crack metric, and predicted probability.
- elevation_map.png : PNG visualization of synthetic DEM elevation.
- crack_map.png : PNG visualization of synthetic drone crack score.
- probability_map.png : PNG visualization of predicted rockfall probability (heatmap).
- sensor_sample.png : Sample sensor timeseries plot.
- this README.md

How this prototype works (high-level)
------------------------------------
1. Synthetic Data:
   - A synthetic Digital Elevation Model (DEM) is generated over a 100x100 grid.
   - A synthetic 'drone image' is simulated and line-like structures are added to mimic cracks.
   - Geotechnical sensors (strain/displacement) are simulated at several grid locations with time-series containing trends and spikes.
   - Recent rainfall is simulated as a single scalar (you can change it).

2. Feature engineering:
   - Slope is derived from elevation gradients.
   - Crack score is derived from gradient magnitude of the synthetic drone image.
   - Sensor features (last value, variance, slope) are aggregated per grid cell using distance-weighted averaging.
   - Rainfall is included as a feature.

3. Model training:
   - A Random Forest Classifier is trained on the synthetic dataset to predict the probability of rockfall-like events.
   - The trained model predicts per-grid-cell probability, saved in probability_map.csv.

4. Visualizations:
   - Elevation map, crack map, and probability heatmap are created as PNGs for easy demo.

How to run this prototype locally (recommended)
-----------------------------------------------
1. Requirements:
   - Python 3.8+
   - Install packages: numpy, pandas, scikit-learn, matplotlib
     Example: pip install numpy pandas scikit-learn matplotlib

2. Steps:
   - Run the Python script (or notebook) that produces the artifacts (the script that generated these files).
   - Open the PNGs to show the DEM, crack map, and predicted probability map.
   - Open probability_map.csv in a spreadsheet or GIS tool (QGIS) to inspect coordinates and probabilities.

How to demo to judges (short script)
------------------------------------
1. Start by explaining the problem briefly: safety risks from unexpected rockfalls and limitations of current approaches.
2. Show the elevation map (open elevation_map.png).
3. Show the drone-derived crack map (open crack_map.png).
4. Show the predicted probability heatmap (open probability_map.png).
   - Explain how the model uses slope, crack evidence, sensor trends, and rainfall to score each grid cell.
5. Show a sample sensor timeseries (sensor_sample.png) and explain how spikes/trends increase risk score.
6. Explain how this prototype maps to a production architecture:
   - Replace synthetic DEM/drone with real DEM and drone orthophotos (store imagery in S3, DEM in PostGIS raster)
   - Ingest real sensors via MQTT to a time-series DB (InfluxDB or PostgreSQL + Timescale)
   - Serve model via FastAPI and create a dashboard with React/Mapbox or Leaflet to overlay heatmaps on real coordinates
   - Use Twilio or AWS SNS for alerts (SMS/email) from the server when probability exceeds thresholds
7. Optional: show the CSV loaded into QGIS to display heatmap over real coordinates and link to photo thumbnails.

Extending the prototype
-----------------------
- Replace RandomForest with spatiotemporal models (LSTM/Temporal CNN) for better temporal prediction.
- Use computer vision (YOLO or U-Net) on real drone images to extract crack masks and rock fragments.
- Add an ingestion pipeline with MQTT -> ingestion service -> timeseries DB.
- Integrate PostGIS for real spatial joins and store DEM rasters.
- Add a production dashboard (React + Mapbox) and a backend (FastAPI) to serve model endpoints.
- Add an alerting microservice that calls Twilio/AWS SNS when thresholds are crossed.

Notes
-----
- This is a **minimal** proof-of-concept built on synthetic data to demonstrate the full stack flow: data -> features -> model -> visualization.
- For a judged demo, the visuals (PNGs) plus the architecture explanation are usually sufficient to show feasibility and next steps.

