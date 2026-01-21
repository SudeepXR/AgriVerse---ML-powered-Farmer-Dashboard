# import numpy as np
# import pandas as pd
# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.metrics import mean_absolute_error

# # -----------------------------
# # STEP 1: Create Dataset
# # -----------------------------
# np.random.seed(42)
# n = 500

# data = {
#     "grain_type": np.random.randint(0, 3, n),      # 0-wheat,1-rice,2-maize
#     "temperature": np.random.uniform(15, 40, n),
#     "humidity": np.random.uniform(30, 90, n),
#     "moisture": np.random.uniform(10, 18, n),
#     "storage_type": np.random.randint(0, 3, n)     # 0-open,1-warehouse,2-silo
# }

# df = pd.DataFrame(data)

# df["shelf_life"] = (
#     140
#     - (df["temperature"] * 1.5)
#     - (df["humidity"] * 0.8)
#     - (df["moisture"] * 2)
#     + (df["storage_type"] * 15)
#     - (df["grain_type"] * 5)
# )

# df["shelf_life"] = df["shelf_life"].clip(15, 180)

# # -----------------------------
# # STEP 2: Train Model
# # -----------------------------
# X = df.drop("shelf_life", axis=1)
# y = df["shelf_life"]

# X_train, X_test, y_train, y_test = train_test_split(
#     X, y, test_size=0.2, random_state=42
# )

# model = RandomForestRegressor(n_estimators=200, random_state=42)
# model.fit(X_train, y_train)

# predictions = model.predict(X_test)
# mae = mean_absolute_error(y_test, predictions)

# print("Model trained successfully")
# print("Mean Absolute Error:", round(mae, 2), "days")

# # -----------------------------
# # STEP 3: Prediction Function
# # -----------------------------
# def predict_shelf_life(grain, temp, humidity, moisture, storage):
#     input_data = np.array([[grain, temp, humidity, moisture, storage]])
#     prediction = model.predict(input_data)[0]
    
#     confidence = max(0, 1 - (mae / prediction))
    
#     if prediction > 90:
#         risk = "Low"
#     elif prediction > 45:
#         risk = "Medium"
#     else:
#         risk = "High"
        
#     return round(prediction, 1), round(confidence * 100, 1), risk

# # -----------------------------
# # STEP 4: Example Run
# # -----------------------------
# if __name__ == "__main__":
#     shelf_life, confidence, risk = predict_shelf_life(
#         grain=1,        # Rice
#         temp=32,
#         humidity=78,
#         moisture=14,
#         storage=0       # Open storage
#     )

#     print("\nPrediction Output:")
#     print("Shelf Life:", shelf_life, "days")
#     print("Confidence:", confidence, "%")
#     print("Risk Level:", risk)
