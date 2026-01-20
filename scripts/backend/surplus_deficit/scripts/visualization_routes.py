# visualization_routes.py
import pandas as pd
import folium
import os
import uuid

def visualize_routes_with_farmer_highlight(
    farmer_city: str,
    output_dir: str
):
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "..", "data")
    shipments_path = os.path.join(data_dir, "optimized_shipments_with_latlon.csv")

    df = pd.read_csv(shipments_path)

    # Create unique map filename
    map_filename = f"shipment_map_{uuid.uuid4().hex}.html"
    map_output_path = os.path.join(output_dir, map_filename)

    # Create map centered on Karnataka
    m = folium.Map(location=[15.0, 76.0], zoom_start=7)

    for _, row in df.iterrows():
        supplier = row["Supplier_District"]
        consumer = row["Consumer_District"]

        supplier_coords = (row["Supplier_Lat"], row["Supplier_Lon"])
        consumer_coords = (row["Consumer_Lat"], row["Consumer_Lon"])

        if supplier == farmer_city or consumer == farmer_city:
            color, weight, opacity = "green", 5, 0.9
        else:
            color, weight, opacity = "gray", 2, 0.4

        folium.PolyLine(
            locations=[supplier_coords, consumer_coords],
            color=color,
            weight=weight,
            opacity=opacity,
            tooltip=f"{supplier} → {consumer} | {row['Shipment_Tons']:.0f} tons"
        ).add_to(m)

        folium.CircleMarker(
            location=supplier_coords,
            radius=4,
            color="blue",
            fill=True,
            fill_opacity=0.8,
            popup=f"Supplier: {supplier}"
        ).add_to(m)

        folium.CircleMarker(
            location=consumer_coords,
            radius=4,
            color="red",
            fill=True,
            fill_opacity=0.8,
            popup=f"Consumer: {consumer}"
        ).add_to(m)

    legend_html = """
    <div style="
        position: fixed;
        bottom: 40px;
        left: 40px;
        width: 240px;
        background-color: white;
        border:2px solid grey;
        z-index:9999;
        font-size:14px;
        padding:10px;
    ">
        <b>Route Legend</b><br>
        <span style="color:green;">━━</span> Routes connected to your farm<br>
        <span style="color:gray;">━━</span> Other routes<br>
        <span style="color:blue;">●</span> Supplier district<br>
        <span style="color:red;">●</span> Deficit district
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save(map_output_path)

    return map_filename
