import React, { useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useSelectedFarmer } from "../contexts/FarmerSelectionContext";

const KARNATAKA_DISTRICTS = [
  "Bagalkot", "Ballari", "Belagavi", "Bengaluru Rural", "Bengaluru Urban",
  "Bidar", "Chamarajanagar", "Chikkaballapur", "Chikkamagaluru", "Chitradurga",
  "Dakshina Kannada", "Davanagere", "Dharwad", "Gadag", "Hassan", "Haveri",
  "Kalaburagi", "Kodagu", "Kolar", "Koppal", "Mandya", "Mysuru", "Raichur",
  "Ramanagara", "Shivamogga", "Tumakuru", "Udupi", "Uttara Kannada",
  "Vijayanagara", "Vijayapura", "Yadgir",
];

const LogisticsMap: React.FC = () => {
  const { user, role } = useAuth();
  const { selectedFarmer } = useSelectedFarmer();
  const farmerId = role === "farmer" ? user?.id : selectedFarmer?.id;

  // Map State
  const [district, setDistrict] = useState("");
  const [mapUrl, setMapUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Shelf Life State
  const [harvestDate, setHarvestDate] = useState("");
  const [transportHours, setTransportHours] = useState("");
  const [shelfLifeResult, setShelfLifeResult] = useState<any>(null);
  const [shelfLifeLoading, setShelfLifeLoading] = useState(false);

  // Fetch Logistics Map
  const fetchMap = async (selectedDistrict: string) => {
    setLoading(true);
    setError(null);
    setMapUrl(null);

    try {
      const response = await fetch(
        `http://localhost:5000/api/logistics/map?district=${encodeURIComponent(selectedDistrict)}`
      );
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to fetch map");
      }
      setMapUrl(data.map_url);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Predict Shelf Life
  const predictShelfLife = async () => {
    if (!farmerId || !harvestDate || !transportHours || !district) {
      alert("Please fill all shelf life prediction fields");
      return;
    }

    setShelfLifeLoading(true);
    setShelfLifeResult(null);

    try {
      const response = await fetch(
        "http://localhost:5000/api/shelf-life/predict",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            farmer_id: farmerId,
            harvest_date: harvestDate,
            transport_hours: Number(transportHours),
            storage_district: district,
          }),
        }
      );

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Prediction failed");

      setShelfLifeResult(data);
    } catch (e: any) {
      console.error(e);
      alert(e.message || "Failed to predict shelf life");
    } finally {
      setShelfLifeLoading(false);
    }
  };

  const handleDistrictChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setDistrict(value);
    if (value) fetchMap(value);
  };

  return (
    <div className="p-6 space-y-6 animate-fade-in grid grid-cols-1 md:grid-cols-2 gap-6">

      {/* LEFT COLUMN */}
      <div className="space-y-6">

        {/* District Selection */}
        <div className="agri-card">
          <h2 className="text-xl font-semibold mb-4">
            Logistics & Yield Planning
          </h2>

          <label className="block text-sm font-medium mb-2">
            Select District (Karnataka)
          </label>

          <select
            value={district}
            onChange={handleDistrictChange}
            className="agri-input w-full"
          >
            <option value="">-- Select District --</option>
            {KARNATAKA_DISTRICTS.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>

          {loading && (
            <p className="text-sm text-muted-foreground mt-2 italic">
              Generating logistics map…
            </p>
          )}

          {error && (
            <p className="text-sm text-destructive mt-2">{error}</p>
          )}
        </div>

        {/* Shelf Life Prediction */}
        <div className="agri-card">
          <h2 className="text-xl font-semibold mb-4">
            Shelf Life Prediction
          </h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                Harvest Date
              </label>
              <input
                type="date"
                className="agri-input w-full"
                value={harvestDate}
                onChange={(e) => setHarvestDate(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                Transport Duration (Hours)
              </label>
              <input
                type="number"
                className="agri-input w-full"
                placeholder="e.g. 12"
                value={transportHours}
                onChange={(e) => setTransportHours(e.target.value)}
              />
            </div>

            <button
              onClick={predictShelfLife}
              disabled={shelfLifeLoading || !farmerId}
              className="w-full bg-primary text-primary-foreground py-2 rounded-md hover:bg-primary/90 disabled:opacity-50"
            >
              {shelfLifeLoading ? "Predicting..." : "Predict Shelf Life"}
            </button>

            {shelfLifeResult && (
              <div className="mt-4 p-4 bg-muted/50 rounded-lg border space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Risk Level</span>
                  <span className="px-2 py-1 rounded text-xs font-bold">
                    {shelfLifeResult.prediction?.risk_level}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Base Shelf Life</p>
                    <p className="font-semibold">
                      {shelfLifeResult.prediction?.base_shelf_life_days} days
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Final Shelf Life</p>
                    <p className="font-semibold text-primary">
                      {shelfLifeResult.prediction?.final_shelf_life_days} days
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Transport Impact</p>
                    <p className="text-red-500 font-medium">
                      {Math.floor(shelfLifeResult.prediction?.base_shelf_life_days - shelfLifeResult.prediction?.final_shelf_life_days)} days
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* RIGHT COLUMN */}
      <div className="agri-card min-h-[500px] flex flex-col">
        <h2 className="text-lg font-semibold mb-4">
          Surplus-Deficit Route Map {district && `- ${district}`}
        </h2>

        {mapUrl ? (
          <iframe
            src={mapUrl}
            title={`Logistics map for ${district}`}
            className="w-full h-full min-h-[500px] rounded-xl border"
            loading="lazy"
          />
        ) : (
          <div className="flex-grow flex items-center justify-center text-muted-foreground bg-muted/20 rounded-xl border border-dashed">
            {loading ? "Loading Map..." : "Select a district to view routes"}
          </div>
        )}
      </div>
    </div>
  );
};

export default LogisticsMap;
