import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from PIL import Image

st.set_page_config(layout="wide", page_title="Rockfall MVP — Interactive Heatmap")
st.title("Rockfall Prediction — Interactive Heatmap")

st.sidebar.header("Data & Input")
uploaded = st.sidebar.file_uploader("Upload probability_map.csv (or leave empty to use path)", type=["csv"])
csv_path_input = st.sidebar.text_input("Or give path to CSV", "probability_map.csv")
use_uploaded = uploaded is not None

st.sidebar.markdown("---")
st.sidebar.header("Visualization Controls")
threshold = st.sidebar.slider("Alert threshold (probability)", 0.0, 1.0, 0.6, 0.01)
top_n = st.sidebar.slider("Top N risky cells to overlay", 1, 200, 20)

st.sidebar.markdown("---")
st.sidebar.markdown("Notes:")
st.sidebar.markdown("- If CSV has `lat`/`lon` (or `latitude`/`longitude`), the app will use geographic coordinates.")
st.sidebar.markdown("- If CSV has `thumbnail` or `image` column, click a top cell to view it.")

@st.cache_data
def load_df_from_bytes(bytes_io):
    return pd.read_csv(bytes_io)

@st.cache_data
def load_df_from_path(path):
    return pd.read_csv(path)

if use_uploaded:
    try:
        df = load_df_from_bytes(uploaded)
        st.sidebar.success("CSV uploaded")
    except Exception as e:
        st.sidebar.error(f"Failed to read uploaded CSV: {e}")
        st.stop()
else:
    try:
        df = load_df_from_path(csv_path_input)
    except Exception as e:
        st.sidebar.error(f"Failed to read CSV from path '{csv_path_input}': {e}")
        st.stop()

if 'probability' not in df.columns:
    st.error("CSV must contain a 'probability' column.")
    st.stop()

lat_cols = [c for c in df.columns if c.lower() in ("lat", "latitude")]
lon_cols = [c for c in df.columns if c.lower() in ("lon", "longitude")]
has_georef = len(lat_cols) > 0 and len(lon_cols) > 0
if has_georef:
    lat_col = lat_cols[0]
    lon_col = lon_cols[0]
else:
    lat_col = lon_col = None

st.sidebar.write(f"Detected georef: {'Yes' if has_georef else 'No (using grid indices)'}")

@st.cache_data
def make_grid_from_table(df, georef):
    probs = df['probability'].values.astype(float)
    if georef:
        lats = df[lat_col].values.astype(float)
        lons = df[lon_col].values.astype(float)
        xi = np.linspace(lons.min(), lons.max(), 200)
        yi = np.linspace(lats.min(), lats.max(), 200)
        Xg, Yg = np.meshgrid(xi, yi)
        from scipy.interpolate import griddata
        Zg = griddata((lons, lats), probs, (Xg, Yg), method='linear')
        Zg = np.nan_to_num(Zg, nan=0.0)
        return Xg, Yg, Zg
    else:
        n = len(probs)
        side = int(np.round(np.sqrt(n)))
        if side * side == n:
            Zg = probs.reshape(side, side)
            Xg, Yg = np.meshgrid(np.arange(side), np.arange(side))
            return Xg, Yg, Zg
        else:
            xi = np.linspace(0, 1, 200)
            yi = np.linspace(0, 1, 200)
            Xg, Yg = np.meshgrid(xi, yi)
            Zg = np.random.rand(200, 200) * 0.1
            return Xg, Yg, Zg

Xg, Yg, Zg = make_grid_from_table(df, has_georef)

mask = (Zg >= threshold).astype(float)

top_df = df.sort_values('probability', ascending=False).head(top_n).reset_index(drop=True)

fig = go.Figure()

fig.add_trace(go.Heatmap(
    x=np.unique(Xg[0, :]),
    y=np.unique(Yg[:, 0]),
    z=Zg,
    colorscale="Cividis",
    zmin=0, zmax=1,
    colorbar=dict(title="Probability"),
    hovertemplate="x:%{x:.5f}<br>y:%{y:.5f}<br>prob:%{z:.3f}<extra></extra>"
))

fig.add_trace(go.Heatmap(
    x=np.unique(Xg[0, :]),
    y=np.unique(Yg[:, 0]),
    z=mask,
    colorscale=[[0,'rgba(0,0,0,0)'], [1,'rgba(255,0,0,0.35)']],
    showscale=False,
    hoverinfo='skip'
))

if has_georef:
    tx = top_df[lon_col].values
    ty = top_df[lat_col].values
else:
    if 'x' in top_df.columns and 'y' in top_df.columns:
        tx = top_df['x'].values
        ty = top_df['y'].values
    else:
        tx = np.arange(len(top_df))
        ty = np.arange(len(top_df))

fig.add_trace(go.Scatter(
    x=tx,
    y=ty,
    mode='markers+text',
    marker=dict(size=9, color='white', line=dict(width=1, color='black')),
    text=[f"{p:.2f}" for p in top_df['probability'].values],
    textposition="top center",
    hovertemplate=("prob:%{text}<br>x:%{x}<br>y:%{y}<extra></extra>")
))

fig.update_layout(
    title="Rockfall Probability (interactive)",
    xaxis=dict(showgrid=False, zeroline=False),
    yaxis=dict(showgrid=False, zeroline=False, scaleanchor="x"),
    height=720,
    margin=dict(l=10, r=10, t=40, b=10)
)
fig.update_yaxes(autorange="reversed")

col1, col2 = st.columns([3,1])
with col1:
    st.plotly_chart(fig, use_container_width=True)
with col2:
    st.subheader("Top risky cells (raw probabilities)")
    st.dataframe(top_df[['probability'] + [c for c in ('lat','lon','latitude','longitude','x','y') if c in top_df.columns]].head(30))
    csv_bytes = top_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download top points CSV", data=csv_bytes, file_name="top_risky_cells.csv", mime="text/csv")

    st.markdown("---")
    st.subheader("Inspect selected top cell")
    sel_idx = st.number_input("Select top-cell index (1 = highest probability)", min_value=1, max_value=max(1, len(top_df)), value=1)
    sel = top_df.iloc[sel_idx-1]
    st.write(f"**Probability:** {sel['probability']:.4f}")
    if has_georef:
        st.write(f"**Lat / Lon:** {sel[lat_col]:.6f} / {sel[lon_col]:.6f}")
    elif 'x' in sel.index and 'y' in sel.index:
        st.write(f"**Grid x / y:** {sel['x']} / {sel['y']}")

    thumb_col = None
    for c in ('thumbnail','image','thumb','photo','url'):
        if c in sel.index:
            thumb_col = c
            break
    if thumb_col:
        st.markdown("**Thumbnail / photo:**")
        val = sel[thumb_col]
        try:
            if isinstance(val, str) and val.startswith("http"):
                st.image(val, use_column_width=True)
            else:
                img = Image.open(str(val))
                st.image(img, use_column_width=True)
        except Exception as e:
            st.write("Failed to load thumbnail:", e)
