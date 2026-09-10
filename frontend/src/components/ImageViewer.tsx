import React, { useState, useRef, useEffect } from 'react';
import {
  ZoomIn,
  ZoomOut,
  RotateCw,
  RotateCcw,
  Maximize2,
  Sparkles,
  RefreshCw,
  Move
} from 'lucide-react';

interface ImageViewerProps {
  imageSrc: string;
  altText?: string;
  isPDF?: boolean;
}

export const ImageViewer: React.FC<ImageViewerProps> = ({
  imageSrc,
  altText = 'Prescription document preview',
  isPDF = false
}) => {
  const [scale, setScale] = useState<number>(1);
  const [rotation, setRotation] = useState<number>(0);
  const [enhanceHandwriting, setEnhanceHandwriting] = useState<boolean>(false);
  const [position, setPosition] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  const containerRef = useRef<HTMLDivElement | null>(null);

  const handleZoomIn = () => {
    setScale((prev) => Math.min(prev + 0.25, 3.5));
  };

  const handleZoomOut = () => {
    setScale((prev) => Math.max(prev - 0.25, 0.5));
  };

  const handleReset = () => {
    setScale(1);
    setRotation(0);
    setPosition({ x: 0, y: 0 });
    setEnhanceHandwriting(false);
  };

  const handleRotateCw = () => {
    setRotation((prev) => (prev + 90) % 360);
  };

  const handleRotateCcw = () => {
    setRotation((prev) => (prev - 90 + 360) % 360);
  };

  // Drag / Pan handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    if (scale <= 1) return;
    setIsDragging(true);
    setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    setPosition({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  return (
    <div
      className="rx-card"
      style={{
        padding: '1rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.75rem',
        backgroundColor: 'var(--bg-surface)'
      }}
    >
      {/* Control Bar */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '0.5rem',
          borderBottom: '1px solid var(--border-subtle)',
          paddingBottom: '0.75rem'
        }}
      >
        <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
          Prescription Viewer Controls
        </span>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', flexWrap: 'wrap' }}>
          {/* Zoom In */}
          <button
            onClick={handleZoomIn}
            className="btn-secondary"
            style={{ padding: '0.4rem 0.6rem', fontSize: 'var(--text-xs)' }}
            title="Zoom In"
            aria-label="Zoom In"
          >
            <ZoomIn size={16} />
            <span>In</span>
          </button>

          {/* Zoom Out */}
          <button
            onClick={handleZoomOut}
            className="btn-secondary"
            style={{ padding: '0.4rem 0.6rem', fontSize: 'var(--text-xs)' }}
            title="Zoom Out"
            aria-label="Zoom Out"
          >
            <ZoomOut size={16} />
            <span>Out</span>
          </button>

          {/* Rotate Left */}
          <button
            onClick={handleRotateCcw}
            className="btn-secondary"
            style={{ padding: '0.4rem 0.6rem', fontSize: 'var(--text-xs)' }}
            title="Rotate 90° Counter-Clockwise"
            aria-label="Rotate Counter-Clockwise"
          >
            <RotateCcw size={16} />
          </button>

          {/* Rotate Right */}
          <button
            onClick={handleRotateCw}
            className="btn-secondary"
            style={{ padding: '0.4rem 0.6rem', fontSize: 'var(--text-xs)' }}
            title="Rotate 90° Clockwise"
            aria-label="Rotate Clockwise"
          >
            <RotateCw size={16} />
          </button>

          {/* Enhance Handwriting Filter */}
          <button
            onClick={() => setEnhanceHandwriting(!enhanceHandwriting)}
            style={{
              padding: '0.4rem 0.75rem',
              borderRadius: '8px',
              border: '1px solid var(--border-subtle)',
              fontSize: 'var(--text-xs)',
              fontWeight: 600,
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.35rem',
              background: enhanceHandwriting ? 'var(--accent-primary)' : 'var(--bg-surface-subtle)',
              color: enhanceHandwriting ? '#ffffff' : 'var(--text-primary)'
            }}
            title="Toggle High-Contrast Handwriting Enhancement Filter"
          >
            <Sparkles size={15} />
            <span>{enhanceHandwriting ? 'Enhanced ON' : 'Enhance Ink'}</span>
          </button>

          {/* Reset Zoom & Rotation */}
          <button
            onClick={handleReset}
            className="btn-secondary"
            style={{ padding: '0.4rem 0.6rem', fontSize: 'var(--text-xs)' }}
            title="Reset Zoom and Rotation"
            aria-label="Reset View"
          >
            <RefreshCw size={15} />
            <span>Reset</span>
          </button>
        </div>
      </div>

      {/* Interactive Image Viewport */}
      <div
        ref={containerRef}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{
          width: '100%',
          height: '420px',
          backgroundColor: 'var(--bg-surface-subtle)',
          borderRadius: '12px',
          overflow: 'hidden',
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: scale > 1 ? (isDragging ? 'grabbing' : 'grab') : 'default',
          userSelect: 'none'
        }}
      >
        {isPDF ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)' }}>
            <p style={{ fontWeight: 600, marginBottom: '0.5rem' }}>📄 PDF Document Uploaded</p>
            <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>
              Processed directly via multimodal PDF vision engine.
            </p>
          </div>
        ) : (
          <img
            src={imageSrc}
            alt={altText}
            className={enhanceHandwriting ? 'high-contrast-canvas' : ''}
            style={{
              maxWidth: '100%',
              maxHeight: '100%',
              objectFit: 'contain',
              transform: `translate(${position.x}px, ${position.y}px) scale(${scale}) rotate(${rotation}deg)`,
              transition: isDragging ? 'none' : 'transform 0.2s ease',
              borderRadius: '8px',
              boxShadow: 'var(--shadow-md)'
            }}
            draggable={false}
          />
        )}

        {/* Zoom & Rotation Level Indicator */}
        <div
          style={{
            position: 'absolute',
            bottom: '10px',
            right: '10px',
            background: 'rgba(0, 0, 0, 0.7)',
            color: '#ffffff',
            padding: '0.25rem 0.6rem',
            borderRadius: '6px',
            fontSize: '0.7rem',
            fontWeight: 600,
            pointerEvents: 'none'
          }}
        >
          {Math.round(scale * 100)}% • {rotation}°
        </div>
      </div>
    </div>
  );
};
