import React from 'react';
import {
  FileText,
  Sun,
  Moon,
  Laptop,
  Shield,
  Type,
  Eye,
  Volume2
} from 'lucide-react';
import { ThemeMode, FontSizeScale } from '../types';

interface NavbarProps {
  theme: ThemeMode;
  onThemeChange: (theme: ThemeMode) => void;
  fontScale: FontSizeScale;
  onFontScaleChange: (scale: FontSizeScale) => void;
  highContrast: boolean;
  onHighContrastToggle: () => void;
  onOpenPrivacy: () => void;
  onOpenPharmacy: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  theme,
  onThemeChange,
  fontScale,
  onFontScaleChange,
  highContrast,
  onHighContrastToggle,
  onOpenPrivacy,
  onOpenPharmacy
}) => {
  return (
    <header
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 50,
        backgroundColor: 'var(--bg-surface)',
        borderBottom: '1px solid var(--border-subtle)',
        backdropFilter: 'blur(10px)',
        padding: '0.75rem 1.5rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1rem'
      }}
    >
      {/* Brand Identity */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div
          style={{
            width: '42px',
            height: '42px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, #0284c7, #10b981)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#ffffff',
            boxShadow: '0 4px 12px rgba(2, 132, 199, 0.25)'
          }}
        >
          <FileText size={24} />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: 'var(--text-xl)', fontWeight: 800, fontFamily: 'var(--font-heading)', letterSpacing: '-0.02em' }}>
              Rx<span style={{ color: 'var(--accent-primary)' }}>Decoder</span>
            </span>
            <span
              style={{
                fontSize: '0.65rem',
                fontWeight: 700,
                padding: '0.15rem 0.4rem',
                borderRadius: '6px',
                background: 'var(--accent-primary-subtle)',
                color: 'var(--accent-primary)',
                textTransform: 'uppercase'
              }}
            >
              Safe AI
            </span>
          </div>
          <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', margin: 0 }}>
            Prescription Understanding & Patient Safety
          </p>
        </div>
      </div>

      {/* Action Controls: Accessibility, Pharmacy, Theme, Privacy */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
        {/* Find Pharmacy Link */}
        <button
          onClick={onOpenPharmacy}
          className="btn-secondary"
          style={{ padding: '0.45rem 0.85rem', fontSize: 'var(--text-sm)' }}
          title="Find nearby pharmacies to check medicine availability"
        >
          📍 Nearby Pharmacies
        </button>

        {/* Font Scale Buttons for Elderly / Low-vision */}
        <div
          role="group"
          aria-label="Text Size Controls"
          style={{
            display: 'flex',
            alignItems: 'center',
            background: 'var(--bg-surface-subtle)',
            borderRadius: '8px',
            border: '1px solid var(--border-subtle)',
            padding: '2px'
          }}
        >
          <button
            onClick={() => onFontScaleChange('normal')}
            style={{
              padding: '0.35rem 0.6rem',
              fontSize: '0.8rem',
              fontWeight: 600,
              background: fontScale === 'normal' ? 'var(--bg-surface)' : 'transparent',
              color: fontScale === 'normal' ? 'var(--accent-primary)' : 'var(--text-secondary)',
              boxShadow: fontScale === 'normal' ? 'var(--shadow-sm)' : 'none',
              borderRadius: '6px'
            }}
            title="Standard Font Size"
            aria-label="Standard Font Size"
          >
            A
          </button>
          <button
            onClick={() => onFontScaleChange('large')}
            style={{
              padding: '0.35rem 0.6rem',
              fontSize: '0.95rem',
              fontWeight: 700,
              background: fontScale === 'large' ? 'var(--bg-surface)' : 'transparent',
              color: fontScale === 'large' ? 'var(--accent-primary)' : 'var(--text-secondary)',
              boxShadow: fontScale === 'large' ? 'var(--shadow-sm)' : 'none',
              borderRadius: '6px'
            }}
            title="Large Font Size"
            aria-label="Large Font Size"
          >
            A+
          </button>
          <button
            onClick={() => onFontScaleChange('xlarge')}
            style={{
              padding: '0.35rem 0.6rem',
              fontSize: '1.1rem',
              fontWeight: 800,
              background: fontScale === 'xlarge' ? 'var(--bg-surface)' : 'transparent',
              color: fontScale === 'xlarge' ? 'var(--accent-primary)' : 'var(--text-secondary)',
              boxShadow: fontScale === 'xlarge' ? 'var(--shadow-sm)' : 'none',
              borderRadius: '6px'
            }}
            title="Extra Large Font Size"
            aria-label="Extra Large Font Size"
          >
            A++
          </button>
        </div>

        {/* High Contrast Toggle */}
        <button
          onClick={onHighContrastToggle}
          style={{
            padding: '0.45rem 0.75rem',
            borderRadius: '8px',
            background: highContrast ? 'var(--text-primary)' : 'var(--bg-surface-subtle)',
            color: highContrast ? 'var(--bg-surface)' : 'var(--text-secondary)',
            border: '1px solid var(--border-subtle)',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.35rem',
            fontSize: 'var(--text-xs)',
            fontWeight: 600
          }}
          title="Toggle High Contrast Mode"
          aria-label="Toggle High Contrast Mode"
        >
          <Eye size={15} />
          <span>{highContrast ? 'High Contrast ON' : 'Contrast'}</span>
        </button>

        {/* Theme Toggle */}
        <div
          role="group"
          aria-label="Theme Selector"
          style={{
            display: 'flex',
            alignItems: 'center',
            background: 'var(--bg-surface-subtle)',
            borderRadius: '8px',
            border: '1px solid var(--border-subtle)',
            padding: '2px'
          }}
        >
          <button
            onClick={() => onThemeChange('light')}
            style={{
              padding: '0.4rem',
              background: theme === 'light' ? 'var(--bg-surface)' : 'transparent',
              color: theme === 'light' ? 'var(--accent-warning)' : 'var(--text-muted)',
              borderRadius: '6px',
              display: 'flex',
              alignItems: 'center'
            }}
            title="Light Theme"
            aria-label="Light Theme"
          >
            <Sun size={16} />
          </button>
          <button
            onClick={() => onThemeChange('dark')}
            style={{
              padding: '0.4rem',
              background: theme === 'dark' ? 'var(--bg-surface)' : 'transparent',
              color: theme === 'dark' ? 'var(--accent-primary)' : 'var(--text-muted)',
              borderRadius: '6px',
              display: 'flex',
              alignItems: 'center'
            }}
            title="Dark Theme"
            aria-label="Dark Theme"
          >
            <Moon size={16} />
          </button>
        </div>

        {/* Privacy Info Modal Trigger */}
        <button
          onClick={onOpenPrivacy}
          className="btn-secondary"
          style={{ padding: '0.45rem 0.85rem', fontSize: 'var(--text-sm)' }}
          title="View HIPAA PHI Privacy & De-identification Details"
        >
          <Shield size={16} style={{ color: 'var(--accent-success)' }} />
          <span>PHI Privacy</span>
        </button>
      </div>
    </header>
  );
};
