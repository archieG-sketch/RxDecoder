import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { DisclaimerBanner } from './components/DisclaimerBanner';
import { LandingHero } from './components/LandingHero';
import { UploadSection } from './components/UploadSection';
import { CameraModal } from './components/CameraModal';
import { ImageViewer } from './components/ImageViewer';
import { ProcessingPipeline } from './components/ProcessingPipeline';
import { ResultsDashboard } from './components/ResultsDashboard';
import { PharmacyFinder } from './components/PharmacyFinder';
import { PrivacyModal } from './components/PrivacyModal';
import { Footer } from './components/Footer';
import { api } from './services/api';
import {
  PrescriptionDecodeResponse,
  SamplePreset,
  ThemeMode,
  FontSizeScale
} from './types';

export const App: React.FC = () => {
  // Theme & Accessibility States
  const [theme, setTheme] = useState<ThemeMode>(() => {
    return (localStorage.getItem('rxdecoder_theme') as ThemeMode) || 'light';
  });

  const [fontScale, setFontScale] = useState<FontSizeScale>(() => {
    return (localStorage.getItem('rxdecoder_font_scale') as FontSizeScale) || 'normal';
  });

  const [highContrast, setHighContrast] = useState<boolean>(() => {
    return localStorage.getItem('rxdecoder_contrast') === 'true';
  });

  // App Flow & Data States
  const [viewState, setViewState] = useState<'landing' | 'preview' | 'processing' | 'results'>('landing');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [filePreviewUrl, setFilePreviewUrl] = useState<string | null>(null);
  const [isPDF, setIsPDF] = useState<boolean>(false);
  const [samples, setSamples] = useState<SamplePreset[]>([]);
  const [currentProcessingStage, setCurrentProcessingStage] = useState<number>(1);
  const [decodedData, setDecodedData] = useState<PrescriptionDecodeResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  // Modals
  const [isCameraOpen, setIsCameraOpen] = useState<boolean>(false);
  const [isPharmacyOpen, setIsPharmacyOpen] = useState<boolean>(false);
  const [isPrivacyOpen, setIsPrivacyOpen] = useState<boolean>(false);

  // Apply Theme & Font Scales to Root HTML Element
  useEffect(() => {
    const root = document.documentElement;
    root.setAttribute('data-theme', theme);
    localStorage.setItem('rxdecoder_theme', theme);

    if (fontScale === 'large') {
      root.style.setProperty('--font-scale', '1.15');
    } else if (fontScale === 'xlarge') {
      root.style.setProperty('--font-scale', '1.3');
    } else {
      root.style.setProperty('--font-scale', '1.0');
    }
    localStorage.setItem('rxdecoder_font_scale', fontScale);

    root.setAttribute('data-high-contrast', highContrast ? 'true' : 'false');
    localStorage.setItem('rxdecoder_contrast', highContrast ? 'true' : 'false');
  }, [theme, fontScale, highContrast]);

  // Load Samples on Startup
  useEffect(() => {
    const loadSamples = async () => {
      try {
        const sampleList = await api.fetchSamples();
        setSamples(sampleList);
      } catch (e) {
        console.warn('Unable to load samples:', e);
      }
    };
    loadSamples();
  }, []);

  // Handle File Selection
  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    const isPdfFile = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
    setIsPDF(isPdfFile);

    const url = URL.createObjectURL(file);
    setFilePreviewUrl(url);
    setViewState('preview');
  };

  // Handle Camera Capture
  const handleCameraCapture = (file: File) => {
    handleFileSelect(file);
  };

  // Start Processing Pipeline
  const handleStartProcessing = async () => {
    if (!selectedFile) return;

    setViewState('processing');
    setLoading(true);
    setCurrentProcessingStage(1);

    // Stage visual progression timer
    const stageTimer = setInterval(() => {
      setCurrentProcessingStage((prev) => {
        if (prev < 5) return prev + 1;
        return prev;
      });
    }, 650);

    try {
      const response = await api.decodePrescription(selectedFile);
      clearInterval(stageTimer);
      setCurrentProcessingStage(5);
      setDecodedData(response);
      setTimeout(() => {
        setViewState('results');
        setLoading(false);
      }, 400);
    } catch (e: any) {
      clearInterval(stageTimer);
      console.error('Decoding failed:', e);
      alert('Error processing prescription. Falling back to structured demo view.');
      // Graceful fallback to sample response if backend encounters unhandled file error
      const fallbackSample = await api.decodeSample('sample_handwritten_amoxicillin');
      setDecodedData(fallbackSample);
      setViewState('results');
      setLoading(false);
    }
  };

  // Handle One-Click Sample Presets
  const handleSelectSample = async (sampleId: string) => {
    setViewState('processing');
    setLoading(true);
    setCurrentProcessingStage(1);

    // Simulate standard pipeline progression
    const interval = setInterval(() => {
      setCurrentProcessingStage((prev) => (prev < 5 ? prev + 1 : prev));
    }, 450);

    try {
      const resp = await api.decodeSample(sampleId);
      clearInterval(interval);
      setCurrentProcessingStage(5);
      setDecodedData(resp);

      // Set sample placeholder preview
      setFilePreviewUrl(
        sampleId === 'sample_handwritten_amoxicillin'
          ? 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400"><rect width="600" height="400" fill="%23fff8e7"/><text x="40" y="60" font-family="sans-serif" font-size="18" font-weight="bold" fill="%23333">Metro Family Clinic - Dr. Marcus Vance MD</text><text x="40" y="100" font-family="sans-serif" font-size="14" fill="%23666">Pt: Robert Miller, Age 42 | Date: 10/14/2026</text><line x1="40" y1="120" x2="560" y2="120" stroke="%23ccc" stroke-width="2"/><text x="40" y="160" font-family="cursive, sans-serif" font-size="22" fill="%231a365d">Rx: Amoxicillin 500mg - 1 cap PO TID PC x 10d</text><text x="40" y="220" font-family="cursive, sans-serif" font-size="22" fill="%231a365d">2. Ibuprofen 400mg - 1 tab PO Q6H PRN pain</text><text x="40" y="320" font-family="sans-serif" font-size="14" fill="%23888">Refills: 0 | Sig: Dr. M. Vance</text></svg>'
          : 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400"><rect width="600" height="400" fill="%23f8fafc"/><text x="40" y="60" font-family="sans-serif" font-size="18" font-weight="bold" fill="%230f172a">Valley Internal Medicine - Dr. Elena Rostova MD</text><text x="40" y="100" font-family="sans-serif" font-size="14" fill="%23475569">Pt: Eleanor Davies, DOB: 03/22/1954</text><line x1="40" y1="120" x2="560" y2="120" stroke="%23cbd5e1" stroke-width="2"/><text x="40" y="160" font-family="monospace" font-size="18" fill="%230284c7">1. Metformin 850mg tab - 1 tab PO BID WF (%2360)</text><text x="40" y="210" font-family="monospace" font-size="18" fill="%230284c7">2. Lisinopril 20mg tab - 1 tab PO QAM (%2330)</text><text x="40" y="260" font-family="monospace" font-size="18" fill="%230284c7">3. Atorvastatin 40mg tab - 1 tab PO QHS (%2330)</text></svg>'
      );
      setIsPDF(false);

      setTimeout(() => {
        setViewState('results');
        setLoading(false);
      }, 400);
    } catch (e) {
      clearInterval(interval);
      console.error(e);
      setLoading(false);
      setViewState('landing');
    }
  };

  const handleReset = () => {
    setViewState('landing');
    setSelectedFile(null);
    if (filePreviewUrl) {
      URL.revokeObjectURL(filePreviewUrl);
      setFilePreviewUrl(null);
    }
    setDecodedData(null);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: 'var(--bg-app)' }}>
      {/* Top Safety Disclaimer */}
      <DisclaimerBanner />

      {/* Main Navbar */}
      <Navbar
        theme={theme}
        onThemeChange={setTheme}
        fontScale={fontScale}
        onFontScaleChange={setFontScale}
        highContrast={highContrast}
        onHighContrastToggle={() => setHighContrast(!highContrast)}
        onOpenPrivacy={() => setIsPrivacyOpen(true)}
        onOpenPharmacy={() => setIsPharmacyOpen(true)}
      />

      {/* Main Content Area */}
      <main style={{ flex: 1 }}>
        {/* VIEW 1: LANDING & UPLOAD */}
        {viewState === 'landing' && (
          <>
            <LandingHero
              onUploadClick={() => {
                const input = document.createElement('input');
                input.type = 'file';
                input.accept = 'image/*,application/pdf';
                input.onchange = (e: any) => {
                  if (e.target.files && e.target.files[0]) {
                    handleFileSelect(e.target.files[0]);
                  }
                };
                input.click();
              }}
              onCameraClick={() => setIsCameraOpen(true)}
              samples={samples}
              onSelectSample={handleSelectSample}
              isLoading={loading}
            />

            <UploadSection
              onFileSelect={handleFileSelect}
              onCameraTrigger={() => setIsCameraOpen(true)}
              samples={samples}
              onSelectSample={handleSelectSample}
              isLoading={loading}
            />
          </>
        )}

        {/* VIEW 2: PREVIEW & INTERACTIVE CONTROLS */}
        {viewState === 'preview' && filePreviewUrl && (
          <div style={{ maxWidth: '960px', margin: '2rem auto', padding: '0 1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
              <div>
                <h2 style={{ fontSize: 'var(--text-xl)', fontWeight: 800 }}>
                  Review Uploaded Prescription
                </h2>
                <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>
                  Use the controls to zoom in, rotate, or enhance ink readability before AI decoding.
                </p>
              </div>

              <div style={{ display: 'flex', gap: '0.6rem' }}>
                <button onClick={handleReset} className="btn-secondary" style={{ padding: '0.6rem 1rem' }}>
                  Cancel
                </button>
                <button
                  onClick={handleStartProcessing}
                  className="btn-primary"
                  style={{ padding: '0.6rem 1.5rem', borderRadius: '10px' }}
                >
                  <span>Decode Prescription →</span>
                </button>
              </div>
            </div>

            <ImageViewer imageSrc={filePreviewUrl} isPDF={isPDF} />

            <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
              <button
                onClick={handleStartProcessing}
                className="btn-primary"
                style={{ padding: '0.9rem 2.5rem', fontSize: 'var(--text-base)', borderRadius: '12px' }}
              >
                <span>Process with Safe AI Pipeline →</span>
              </button>
            </div>
          </div>
        )}

        {/* VIEW 3: MULTI-AGENT PIPELINE PROCESSING */}
        {viewState === 'processing' && (
          <div style={{ padding: '3rem 1rem' }}>
            <ProcessingPipeline
              currentStage={currentProcessingStage}
              phiReport={decodedData?.phi_report}
            />
          </div>
        )}

        {/* VIEW 4: RESULTS DASHBOARD */}
        {viewState === 'results' && decodedData && (
          <ResultsDashboard
            data={decodedData}
            originalImageSrc={filePreviewUrl || undefined}
            isPDF={isPDF}
            onReset={handleReset}
            onOpenPharmacy={() => setIsPharmacyOpen(true)}
          />
        )}
      </main>

      {/* Modals */}
      <CameraModal
        isOpen={isCameraOpen}
        onClose={() => setIsCameraOpen(false)}
        onCapture={handleCameraCapture}
      />

      <PharmacyFinder
        isOpen={isPharmacyOpen}
        onClose={() => setIsPharmacyOpen(false)}
      />

      <PrivacyModal
        isOpen={isPrivacyOpen}
        onClose={() => setIsPrivacyOpen(false)}
      />

      {/* Global Footer */}
      <Footer />
    </div>
  );
};
