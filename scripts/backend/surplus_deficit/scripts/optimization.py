import pandas as pd
import numpy as np
from scipy.optimize import linprog
from geopy.distance import geodesic

# -------------------------------------------------
# MAIN OPTIMIZATION FUNCTION
# -------------------------------------------------

def optimize_food_distribution(input_path, output_path):
    """
    Takes processed district-wise surplus/deficit data
    and computes optimal shipment quantities from surplus
    districts to deficit districts using Linear Programming.
    """

    df = pd.read_csv(input_path)

    # -------------------------------
    # Separate surplus and deficit
    # -------------------------------
    suppliers = df[df["Surplus_tons"] > 0].copy()
    consumers = df[df["Deficit_tons"] > 0].copy()

    if suppliers.empty or consumers.empty:
        print("⚠️ No surplus or no deficit districts found.")
        return pd.DataFrame()

    suppliers.reset_index(drop=True, inplace=True)
    consumers.reset_index(drop=True, inplace=True)

    num_suppliers = len(suppliers)
    num_consumers = len(consumers)

    # -------------------------------------------------
    # Create cost vector (distance-based cost)
    # -------------------------------------------------
    costs = []

    for i in range(num_suppliers):
        for j in range(num_consumers):
            sup_coords = (suppliers.loc[i, "lat"], suppliers.loc[i, "lon"])
            con_coords = (consumers.loc[j, "lat"], consumers.loc[j, "lon"])
            dist = geodesic(sup_coords, con_coords).km
            costs.append(dist)

    # 🔴 IMPORTANT FIX: c must be 1D
    c = np.array(costs).flatten()

    # -------------------------------------------------
    # Build constraints
    # -------------------------------------------------

    # Supplier constraints (cannot send more than surplus)
    A_ub = []
    b_ub = []

    for i in range(num_suppliers):
        row = [0] * (num_suppliers * num_consumers)
        for j in range(num_consumers):
            row[i * num_consumers + j] = 1
        A_ub.append(row)
        b_ub.append(suppliers.loc[i, "Surplus_tons"])

    # Consumer constraints (must receive deficit)
    A_eq = []
    b_eq = []

    for j in range(num_consumers):
        row = [0] * (num_suppliers * num_consumers)
        for i in range(num_suppliers):
            row[i * num_consumers + j] = 1
        A_eq.append(row)
        b_eq.append(consumers.loc[j, "Deficit_tons"])

    A_ub = np.array(A_ub)
    b_ub = np.array(b_ub)
    A_eq = np.array(A_eq)
    b_eq = np.array(b_eq)

    # Shipment bounds (>= 0)
    bounds = [(0, None)] * (num_suppliers * num_consumers)

    # -------------------------------------------------
    # Solve Linear Program
    # -------------------------------------------------
    result = linprog(
        c=c,
        A_ub=A_ub,
        b_ub=b_ub,
        A_eq=A_eq,
        b_eq=b_eq,
        bounds=bounds,
        method="highs"
    )

    if not result.success:
        print("❌ Optimization failed:", result.message)
        return pd.DataFrame()

    # -------------------------------------------------
    # Build shipment output
    # -------------------------------------------------
    shipments = []
    x = result.x  # optimized shipment quantities

    for i in range(num_suppliers):
        for j in range(num_consumers):
            qty = x[i * num_consumers + j]
            if qty > 0:
                shipments.append({
                    "Supplier_District": suppliers.loc[i, "District_Name"],
                    "Consumer_District": consumers.loc[j, "District_Name"],
                    "Shipment_Tons": round(qty, 2),
                    "Supplier_Lat": suppliers.loc[i, "lat"],
                    "Supplier_Lon": suppliers.loc[i, "lon"],
                    "Consumer_Lat": consumers.loc[j, "lat"],
                    "Consumer_Lon": consumers.loc[j, "lon"]
                })

    shipments_df = pd.DataFrame(shipments)
    shipments_df.to_csv(output_path, index=False)

    print(f"✅ Optimization complete. Shipments saved to:\n{output_path}")

    return shipments_df


# -------------------------------------------------
# SCRIPT ENTRY POINT
# -------------------------------------------------

if __name__ == "__main__":
    input_path = r"C:\Users\SUDEEP XAVIER ROCHE\VS CODE\EL_3\surplus_deficit-main\surplus_deficit-main\data\clustered_data.csv"
    output_path = r"C:\Users\SUDEEP XAVIER ROCHE\VS CODE\EL_3\surplus_deficit-main\surplus_deficit-main\data\optimized_shipments_with_latlon.csv"

    optimize_food_distribution(input_path, output_path)