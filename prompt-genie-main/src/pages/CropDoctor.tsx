import React, { useState, useRef } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { Upload, Camera, AlertCircle, CheckCircle, Loader2, RefreshCw } from 'lucide-react';

const CropDoctor: React.FC = () => {
  const { t } = useLanguage();
  
  // --- State Management ---
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // --- Handlers ---
  const handleFile = (selectedFile: File) => {
    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
    setResult(null); // Reset previous results
    uploadAndDiagnose(selectedFile);
  };

  const uploadAndDiagnose = async (targetFile: File) => {
    setLoading(true);
    const formData = new FormData();
    formData.append('file', targetFile);

    try {
      const response = await fetch('http://localhost:5000/api/diagnose', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Diagnosis failed:", error);
      alert("Failed to connect to backend server.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      <div>
        <h1 className="text-2xl font-display font-bold text-foreground">
          {t('nav.cropDoctor')}
        </h1>
        <p className="text-muted-foreground mt-1">
          Detect diseases and get localized treatment advice for Karnataka crops
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Area */}
        <div className="agri-card">
          <h2 className="text-lg font-display font-semibold text-foreground mb-4 flex items-center gap-2">
            <Camera className="w-5 h-5 text-primary" />
            Upload Crop Image
          </h2>

          <input 
            type="file" 
            className="hidden" 
            ref={fileInputRef} 
            accept="image/*"
            onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
          />

          <div
            className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 cursor-pointer overflow-hidden relative ${
              isDragging ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50 hover:bg-secondary/50'
            }`}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={(e) => { e.preventDefault(); setIsDragging(false); e.dataTransfer.files[0] && handleFile(e.dataTransfer.files[0]); }}
            onClick={() => fileInputRef.current?.click()}
          >
            {preview ? (
              <div className="absolute inset-0">
                <img src={preview} alt="Preview" className="w-full h-full object-cover opacity-40" />
                <div className="absolute inset-0 flex flex-col items-center justify-center bg-background/20 backdrop-blur-[2px]">
                    <RefreshCw className="w-8 h-8 text-primary mb-2" />
                    <p className="text-sm font-semibold">Click to change image</p>
                </div>
              </div>
            ) : (
              <>
                <div className="w-16 h-16 rounded-2xl bg-secondary mx-auto mb-4 flex items-center justify-center">
                  <Upload className="w-8 h-8 text-muted-foreground" />
                </div>
                <p className="text-foreground font-medium">Drag and drop your image here</p>
                <p className="text-sm text-muted-foreground mt-2">or click to browse device</p>
              </>
            )}
          </div>
          
          {loading && (
            <div className="mt-4 p-4 bg-primary/5 rounded-xl flex items-center justify-center gap-3 text-primary font-medium">
              <Loader2 className="w-5 h-5 animate-spin" />
              Analyzing with AI...
            </div>
          )}
        </div>

        {/* Results */}
        <div className="space-y-4">
          {result && result.status === "success" ? (
            <div className="animate-fade-in space-y-4">
              {/* Detection Summary */}
              <div className="agri-card border-l-4 border-warning">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl bg-warning/15 flex items-center justify-center flex-shrink-0">
                    <AlertCircle className="w-6 h-6 text-warning" />
                  </div>
                  <div className="flex-1">
                    <p className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Detected Condition</p>
                    <h3 className="text-xl font-display font-bold text-foreground">
                      {result.disease}
                    </h3>
                    <div className="flex items-center gap-3 mt-2">
                      <span className="px-3 py-1 bg-primary/10 text-primary text-sm font-medium rounded-full">
                        {result.plant !== "Unknown" ? result.plant : "Detected Plant"}
                      </span>
                      <span className="text-sm text-muted-foreground">
                        Confidence: {result.confidence}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Karnataka Regional Advice (The Gemini Output) */}
              <div className="agri-card bg-success/5 border-l-4 border-success">
                <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-success" />
                  Karnataka Regional Advice
                </h3>
                <div className="text-sm text-foreground leading-relaxed whitespace-pre-wrap">
                   {/* This displays the Gemini response including Kannada text */}
                    {result.karnataka_advice}
                </div>
              </div>

              <p className="text-xs text-muted-foreground text-center">
                ⚠️ This is an AI-based prediction. Consult a Krishi Vigyana Kendra (KVK) expert for confirmation.
              </p>
            </div>
          ) : !loading && (
            <div className="h-full flex flex-col items-center justify-center p-12 text-center text-muted-foreground border-2 border-dashed rounded-3xl">
              <Camera className="w-12 h-12 mb-4 opacity-20" />
              <p>Upload an image to see the diagnosis here</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CropDoctor;