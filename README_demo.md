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