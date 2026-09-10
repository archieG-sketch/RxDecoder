import React, { useRef, useState, useEffect } from 'react';
import { Camera, X, RefreshCw, Check, AlertCircle } from 'lucide-react';

interface CameraModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCapture: (file: File) => void;
}

export const CameraModal: React.FC<CameraModalProps> = ({
  isOpen,
  onClose,
  onCapture
}) => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isCaptured, setIsCaptured] = useState(false);
  const [capturedBlob, setCapturedBlob] = useState<Blob | null>(null);
  const [capturedPreview, setCapturedPreview] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      startCamera();
    } else {
      stopCamera();
      setIsCaptured(false);
      setCapturedBlob(null);
      setCapturedPreview(null);
      setError(null);
    }
    return () => {
      stopCamera();
    };
  }, [isOpen]);

  const startCamera = async () => {
    setError(null);
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'environment', // Prefer back camera on mobile
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        }
      });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err: any) {
      console.error('Camera access error:', err);
      setError(
        'Camera permission was denied or camera is not available. You can still upload prescription images using the file picker.'
      );
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      setStream(null);
    }
  };

  const handleCapture = () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth || 1280;
    canvas.height = video.videoHeight || 720;

    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      canvas.toBlob((blob) => {
        if (blob) {
          setCapturedBlob(blob);
          setCapturedPreview(URL.createObjectURL(blob));
          setIsCaptured(true);
        }
      }, 'image/jpeg', 0.95);
    }
  };

  const handleRetake = () => {
    setIsCaptured(false);
    setCapturedBlob(null);
    if (capturedPreview) {
      URL.revokeObjectURL(capturedPreview);
      setCapturedPreview(null);
    }
  };

  const handleConfirm = () => {
    if (capturedBlob) {
      const file = new File([capturedBlob], `prescription_camera_${Date.now()}.jpg`, {
        type: 'image/jpeg'
      });
      onCapture(file);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="camera-modal-title"
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.85)',
        backdropFilter: 'blur(8px)',
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1rem'
      }}
    >
      <div
        className="rx-card"
        style={{
          width: '100%',
          maxWidth: '640px',
          background: 'var(--bg-surface)',
          padding: '1.5rem',
          borderRadius: '20px',
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Camera size={22} style={{ color: 'var(--accent-primary)' }} />
            <h3 id="camera-modal-title" style={{ fontSize: 'var(--text-lg)', fontWeight: 700 }}>
              {isCaptured ? 'Review Prescription Photo' : 'Capture Prescription Document'}
            </h3>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'transparent', color: 'var(--text-muted)', padding: '0.4rem' }}
            aria-label="Close Camera Modal"
          >
            <X size={22} />
          </button>
        </div>

        {/* Viewfinder / Captured Frame */}
        <div
          style={{
            position: 'relative',
            width: '100%',
            height: '340px',
            backgroundColor: '#000000',
            borderRadius: '12px',
            overflow: 'hidden',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          {error ? (
            <div style={{ padding: '1.5rem', textAlign: 'center', color: '#f87171' }}>
              <AlertCircle size={36} style={{ margin: '0 auto 0.75rem' }} />
              <p style={{ fontSize: 'var(--text-sm)' }}>{error}</p>
            </div>
          ) : !isCaptured ? (
            <>
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              />
              {/* Document Alignment Overlay Box */}
              <div
                style={{
                  position: 'absolute',
                  inset: '20px',
                  border: '2px dashed rgba(255, 255, 255, 0.75)',
                  borderRadius: '12px',
                  pointerEvents: 'none',
                  boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.25)'
                }}
              />
              <div
                style={{
                  position: 'absolute',
                  bottom: '12px',
                  backgroundColor: 'rgba(0, 0, 0, 0.65)',
                  color: '#ffffff',
                  padding: '0.3rem 0.75rem',
                  borderRadius: '9999px',
                  fontSize: '0.75rem',
                  pointerEvents: 'none'
                }}
              >
                Position the prescription clearly inside the frame
              </div>
            </>
          ) : (
            <img
              src={capturedPreview || ''}
              alt="Captured prescription preview"
              style={{ width: '100%', height: '100%', objectFit: 'contain' }}
            />
          )}

          <canvas ref={canvasRef} style={{ display: 'none' }} />
        </div>

        {/* Control Buttons */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            gap: '1rem',
            marginTop: '1.25rem'
          }}
        >
          {error ? (
            <button onClick={onClose} className="btn-secondary">
              Close
            </button>
          ) : !isCaptured ? (
            <button
              onClick={handleCapture}
              className="btn-primary"
              style={{ padding: '0.8rem 2rem', borderRadius: '12px' }}
            >
              <Camera size={20} />
              <span>Take Photo</span>
            </button>
          ) : (
            <>
              <button
                onClick={handleRetake}
                className="btn-secondary"
                style={{ padding: '0.75rem 1.5rem', borderRadius: '12px' }}
              >
                <RefreshCw size={18} />
                <span>Retake</span>
              </button>
              <button
                onClick={handleConfirm}
                className="btn-primary"
                style={{ padding: '0.75rem 1.75rem', borderRadius: '12px' }}
              >
                <Check size={18} />
                <span>Use This Photo</span>
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
