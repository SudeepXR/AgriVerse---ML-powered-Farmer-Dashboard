import folium
import pandas as pd

def generate_farmer_map(
    farmer_district,
    target_district,
    shipments_csv,
    output_map_path
):
    df = pd.read_csv(shipments_csv)

    route = df[
        (df["Supplier_District"] == farmer_district) &
        (df["Receiver_District"] == target_district)
    ]

    if route.empty:
        raise ValueError("No route found")

    row = route.iloc[0]

    m = folium.Map(
        location=[row["Supplier_Lat"], row["Supplier_Lon"]],
        zoom_start=7
    )

    # Farmer location (blue)
    folium.Marker(
        [row["Supplier_Lat"], row["Supplier_Lon"]],
        popup=f"Farmer: {farmer_district}",
        icon=folium.Icon(color="blue")
    ).add_to(m)

    # Destination (red)
    folium.Marker(
        [row["Receiver_Lat"], row["Receiver_Lon"]],
        popup=f"Destination: {target_district}",
        icon=folium.Icon(color="red")
    ).add_to(m)

    # Route (green)
    folium.PolyLine(
        locations=[
            (row["Supplier_Lat"], row["Supplier_Lon"]),
            (row["Receiver_Lat"], row["Receiver_Lon"])
        ],
        color="green",
        weight=5
    ).add_to(m)

    m.save(output_map_path)
