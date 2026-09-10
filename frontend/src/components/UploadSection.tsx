import React, { useRef, useState } from 'react';
import {
  Upload,
  Camera,
  FileText,
  Image as ImageIcon,
  CheckCircle,
  AlertCircle,
  Sparkles
} from 'lucide-react';
import { SamplePreset } from '../types';

interface UploadSectionProps {
  onFileSelect: (file: File) => void;
  onCameraTrigger: () => void;
  samples: SamplePreset[];
  onSelectSample: (sampleId: string) => void;
  isLoading: boolean;
}

export const UploadSection: React.FC<UploadSectionProps> = ({
  onFileSelect,
  onCameraTrigger,
  samples,
  onSelectSample,
  isLoading
}) => {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [fileError, setFileError] = useState<string | null>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const validateAndUpload = (file: File) => {
    setFileError(null);
    const validTypes = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf'];
    if (!validTypes.includes(file.type) && !file.name.match(/\.(jpg|jpeg|png|webp|pdf)$/i)) {
      setFileError('Please upload an image (JPG, PNG, WEBP) or a PDF prescription document.');
      return;
    }
    if (file.size > 25 * 1024 * 1024) {
      setFileError('File size exceeds 25MB limit.');
      return;
    }
    onFileSelect(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndUpload(e.dataTransfer.files[0]);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndUpload(e.target.files[0]);
    }
  };

  return (
    <div
      style={{
        maxWidth: '960px',
        margin: '0 auto 2.5rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.25rem'
      }}
    >
      {/* Drag & Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !isLoading && fileInputRef.current?.click()}
        style={{
          border: `2px dashed ${isDragOver ? 'var(--accent-primary)' : 'var(--border-strong)'}`,
          borderRadius: '20px',
          padding: '2.75rem 2rem',
          textAlign: 'center',
          backgroundColor: isDragOver ? 'var(--accent-primary-subtle)' : 'var(--bg-surface)',
          cursor: isLoading ? 'not-allowed' : 'pointer',
          transition: 'all var(--transition-normal)',
          boxShadow: isDragOver ? 'var(--shadow-glow)' : 'var(--shadow-sm)'
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/png, image/jpeg, image/webp, application/pdf"
          style={{ display: 'none' }}
          onChange={handleInputChange}
          disabled={isLoading}
        />

        <div
          style={{
            width: '64px',
            height: '64px',
            borderRadius: '16px',
            background: 'var(--accent-primary-subtle)',
            color: 'var(--accent-primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 1.25rem'
          }}
        >
          <Upload size={32} />
        </div>

        <h3 style={{ fontSize: 'var(--text-xl)', fontWeight: 700, marginBottom: '0.5rem' }}>
          {isDragOver ? 'Drop your prescription file here' : 'Drag & drop prescription or click to browse'}
        </h3>

        <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)', maxWidth: '500px', margin: '0 auto 1.5rem' }}>
          Supports handwritten & printed doctor notes, clinic discharge papers, and digital Rx (JPG, PNG, WEBP, PDF up to 25MB).
        </p>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <button
            type="button"
            className="btn-primary"
            onClick={(e) => {
              e.stopPropagation();
              fileInputRef.current?.click();
            }}
            disabled={isLoading}
            style={{ borderRadius: '10px' }}
          >
            <ImageIcon size={18} />
            <span>Select File</span>
          </button>

          <button
            type="button"
            className="btn-secondary"
            onClick={(e) => {
              e.stopPropagation();
              onCameraTrigger();
            }}
            disabled={isLoading}
            style={{ borderRadius: '10px' }}
          >
            <Camera size={18} />
            <span>Open Camera</span>
          </button>
        </div>

        {fileError && (
          <div
            style={{
              marginTop: '1.25rem',
              color: 'var(--accent-danger)',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              fontSize: 'var(--text-sm)',
              fontWeight: 600
            }}
          >
            <AlertCircle size={18} />
            <span>{fileError}</span>
          </div>
        )}
      </div>

      {/* Preset Prescription Samples Strip */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          overflowX: 'auto',
          paddingBottom: '0.5rem'
        }}
      >
        <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
          ⚡ Test Samples:
        </span>
        {samples.map((s) => (
          <button
            key={s.id}
            onClick={() => onSelectSample(s.id)}
            disabled={isLoading}
            className="btn-secondary"
            style={{
              padding: '0.4rem 0.85rem',
              fontSize: 'var(--text-xs)',
              borderRadius: '20px',
              whiteSpace: 'nowrap',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.35rem'
            }}
          >
            <Sparkles size={13} style={{ color: 'var(--accent-primary)' }} />
            <span>{s.title}</span>
          </button>
        ))}
      </div>
    </div>
  );
};
