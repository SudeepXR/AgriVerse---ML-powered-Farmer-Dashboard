import React, { useState } from "react";

const KARNATAKA_DISTRICTS = [
  "Bagalkot",
  "Ballari",
  "Belagavi",
  "Bengaluru Rural",
  "Bengaluru Urban",
  "Bidar",
  "Chamarajanagar",
  "Chikkaballapur",
  "Chikkamagaluru",
  "Chitradurga",
  "Dakshina Kannada",
  "Davanagere",
  "Dharwad",
  "Gadag",
  "Hassan",
  "Haveri",
  "Kalaburagi",
  "Kodagu",
  "Kolar",
  "Koppal",
  "Mandya",
  "Mysuru",
  "Raichur",
  "Ramanagara",
  "Shivamogga",
  "Tumakuru",
  "Udupi",
  "Uttara Kannada",
  "Vijayanagara",
  "Vijayapura",
  "Yadgir",
];

const LogisticsMap: React.FC = () => {
  const [district, setDistrict] = useState("");
  const [mapUrl, setMapUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Shelf Life State
  const [harvestDate, setHarvestDate] = useState("");
  const [transportHours, setTransportHours] = useState("");
  const [shelfLifeResult, setShelfLifeResult] = useState<any>(null);
  const [shelfLifeLoading, setShelfLifeLoading] = useState(false);

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

  const predictShelfLife = async () => {
    if (!district || !harvestDate || !transportHours) {
      // You might want to show a toast or error here
      return;
    }
    setShelfLifeLoading(true);
    setShelfLifeResult(null);
    try {
      const response = await fetch("http://localhost:5000/api/shelf-life/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          district,
          harvest_date: harvestDate,
          transport_hours: transportHours
        })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Failed to predict");
      setShelfLifeResult(data);
    } catch (e: any) {
      console.error(e);
      // handle error
    } finally {
      setShelfLifeLoading(false);
    }
  };

  const handleDistrictChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setDistrict(value);

    if (value) {
      fetchMap(value);
    }
  };

  return (
    <div className="p-6 space-y-6 animate-fade-in grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="space-y-6">
        <div className="agri-card">
          <h2 className="text-xl font-semibold mb-4">Logistics & Yield Planning</h2>
          {/* Input */}
          <div className="">
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
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>

          {/* Loading */}
          {loading && (
            <p className="text-sm text-muted-foreground mt-2">
              Generating logistics map…
            </p>
          )}

          {/* Error */}
          {error && (
            <p className="text-sm text-destructive mt-2">
              {error}
            </p>
          )}
        </div>

        <div className="agri-card">
          <h2 className="text-xl font-semibold mb-4">Shelf Life Prediction</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Harvest Date</label>
              <input
                type="date"
                className="agri-input w-full"
                value={harvestDate}
                onChange={(e) => setHarvestDate(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Transport Duration (Hours)</label>
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
              disabled={shelfLifeLoading || !district}
              className="w-full bg-primary text-primary-foreground py-2 rounded-md hover:bg-primary/90 disabled:opacity-50 transition-colors"
            >
              {shelfLifeLoading ? "Predicting..." : "Predict Shelf Life"}
            </button>

            {!district && <p className="text-xs text-muted-foreground">Select a district above first.</p>}

            {shelfLifeResult && (
              <div className="mt-4 p-4 bg-muted/50 rounded-lg space-y-2 border">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Risk Level</span>
                  <span className={`px-2 py-1 rounded text-xs font-bold ${shelfLifeResult.prediction.risk_level === 'Low' ? 'bg-green-100 text-green-700' :
                      shelfLifeResult.prediction.risk_level === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-red-100 text-red-700'
                    }`}>
                    {shelfLifeResult.prediction.risk_level}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <p className="text-muted-foreground">Base Shelf Life</p>
                    <p className="font-semibold">{shelfLifeResult.prediction.base_shelf_life_days} days</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Final Shelf Life</p>
                    <p className="font-semibold">{shelfLifeResult.prediction.final_shelf_life_days} days</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Weather</p>
                    <p>{shelfLifeResult.weather_used.temperature}°C, {shelfLifeResult.weather_used.humidity}% RH</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Transport Impact</p>
                    <p className="text-red-500">-{shelfLifeResult.prediction.transport_impact_days} days</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Map */}
      <div className="agri-card min-h-[500px] flex flex-col">
        <h2 className="text-lg font-semibold mb-4">
          Logistics Route Map {district && `- ${district}`}
        </h2>
        {mapUrl ? (
          <iframe
            src={mapUrl}
            title={`Logistics map for ${district}`}
            className="w-full h-full min-h-[500px] rounded-xl border flex-grow"
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
