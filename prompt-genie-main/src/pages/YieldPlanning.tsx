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

  const handleDistrictChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setDistrict(value);

    if (value) {
      fetchMap(value);
    }
  };

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Input */}
      <div className="max-w-md">
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
        <p className="text-sm text-muted-foreground">
          Generating logistics map…
        </p>
      )}

      {/* Error */}
      {error && (
        <p className="text-sm text-destructive">
          {error}
        </p>
      )}

      {/* Map */}
      {mapUrl && (
        <div className="agri-card">
          <h2 className="text-lg font-semibold mb-4">
            Logistics Route Map - {district}
          </h2>
              <iframe
                src={mapUrl}
                title={`Logistics map for ${district}`}
                className="w-full h-[600px] rounded-xl border"
                loading="lazy"
              />



        </div>
      )}
    </div>
  );
};

export default LogisticsMap;
