import React from 'react';
import {
  Upload,
  Camera,
  ShieldCheck,
  CheckCircle2,
  Volume2,
  Sparkles,
  ArrowRight,
  AlertCircle
} from 'lucide-react';
import { SamplePreset } from '../types';

interface LandingHeroProps {
  onUploadClick: () => void;
  onCameraClick: () => void;
  samples: SamplePreset[];
  onSelectSample: (sampleId: string) => void;
  isLoading: boolean;
}

export const LandingHero: React.FC<LandingHeroProps> = ({
  onUploadClick,
  onCameraClick,
  samples,
  onSelectSample,
  isLoading
}) => {
  return (
    <section
      style={{
        padding: '3.5rem 1.5rem 2.5rem',
        maxWidth: '1200px',
        margin: '0 auto',
        textAlign: 'center'
      }}
    >
      {/* Privacy Badge */}
      <div
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.4rem 1rem',
          borderRadius: '9999px',
          background: 'var(--accent-primary-subtle)',
          border: '1px solid rgba(2, 132, 199, 0.3)',
          color: 'var(--accent-primary)',
          fontSize: 'var(--text-xs)',
          fontWeight: 700,
          marginBottom: '1.25rem',
          textTransform: 'uppercase',
          letterSpacing: '0.05em'
        }}
      >
        <ShieldCheck size={16} /> HIPAA Safe Harbor PHI Sanitization Enabled
      </div>

      {/* Main Title */}
      <h1
        style={{
          fontSize: 'clamp(2rem, 5vw, 3.25rem)',
          fontWeight: 800,
          color: 'var(--text-primary)',
          lineHeight: 1.15,
          letterSpacing: '-0.03em',
          maxWidth: '900px',
          margin: '0 auto 1.25rem'
        }}
      >
        Decode Doctor's Handwriting into <br />
        <span
          style={{
            background: 'linear-gradient(135deg, #0284c7, #10b981)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}
        >
          Clear, Simple Medication Guidance
        </span>
      </h1>

      {/* Subtitle */}
      <p
        style={{
          fontSize: 'var(--text-lg)',
          color: 'var(--text-secondary)',
          maxWidth: '750px',
          margin: '0 auto 2.25rem',
          lineHeight: 1.6
        }}
      >
        Designed for patients and caregivers who struggle with messy handwritten prescriptions and complex Latin abbreviations. We strip personal info, verify medication safety, and explain how to take it in plain English.
      </p>

      {/* Primary Action Buttons */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          gap: '1rem',
          flexWrap: 'wrap',
          marginBottom: '3rem'
        }}
      >
        <button
          onClick={onUploadClick}
          className="btn-primary"
          style={{ padding: '0.9rem 2rem', fontSize: 'var(--text-base)', borderRadius: '12px' }}
          disabled={isLoading}
        >
          <Upload size={20} />
          <span>Upload Prescription Image / PDF</span>
        </button>

        <button
          onClick={onCameraClick}
          className="btn-secondary"
          style={{ padding: '0.9rem 1.75rem', fontSize: 'var(--text-base)', borderRadius: '12px' }}
          disabled={isLoading}
        >
          <Camera size={20} />
          <span>Take Photo with Camera</span>
        </button>
      </div>

      {/* Quick Try With Preset Samples */}
      <div
        className="rx-card"
        style={{
          maxWidth: '960px',
          margin: '0 auto 3rem',
          textAlign: 'left',
          background: 'var(--bg-surface)',
          border: '1px solid var(--border-subtle)'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sparkles size={20} style={{ color: 'var(--accent-primary)' }} />
            <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 700 }}>
              Or Try Instantly with a Real-World Sample Prescription:
            </h3>
          </div>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>
            One-click interactive demonstration
          </span>
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
            gap: '1rem'
          }}
        >
          {samples.map((sample) => (
            <div
              key={sample.id}
              onClick={() => !isLoading && onSelectSample(sample.id)}
              className="rx-card-hover"
              style={{
                cursor: isLoading ? 'not-allowed' : 'pointer',
                border: '1px solid var(--border-subtle)',
                borderRadius: '12px',
                padding: '1rem',
                backgroundColor: 'var(--bg-surface-subtle)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'all 0.2s ease'
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.4rem' }}>
                  <span
                    style={{
                      fontSize: '0.65rem',
                      fontWeight: 700,
                      textTransform: 'uppercase',
                      padding: '0.15rem 0.45rem',
                      borderRadius: '4px',
                      background: sample.category.includes('Unclear') ? 'var(--accent-danger-subtle)' : 'var(--accent-primary-subtle)',
                      color: sample.category.includes('Unclear') ? 'var(--accent-danger)' : 'var(--accent-primary)'
                    }}
                  >
                    {sample.category}
                  </span>
                  <ArrowRight size={16} style={{ color: 'var(--accent-primary)' }} />
                </div>
                <h4 style={{ fontSize: 'var(--text-sm)', fontWeight: 700, marginBottom: '0.25rem', color: 'var(--text-primary)' }}>
                  {sample.title}
                </h4>
                <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                  {sample.description}
                </p>
              </div>
              <div style={{ marginTop: '0.75rem', fontSize: 'var(--text-xs)', color: 'var(--accent-primary)', fontWeight: 600 }}>
                {isLoading ? 'Processing...' : 'Load & Decode →'}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 3 Core Value Props */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '1.5rem',
          maxWidth: '1100px',
          margin: '0 auto',
          textAlign: 'left'
        }}
      >
        <div className="rx-card">
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '10px',
              background: 'var(--accent-primary-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent-primary)',
              marginBottom: '1rem'
            }}
          >
            <ShieldCheck size={22} />
          </div>
          <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 700, marginBottom: '0.5rem' }}>
            1. PHI Sanitization First
          </h3>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            Personal health information (names, birthdates, addresses, IDs) is detected and masked before clinical processing. Your privacy is protected by design.
          </p>
        </div>

        <div className="rx-card">
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '10px',
              background: 'var(--accent-success-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent-success)',
              marginBottom: '1rem'
            }}
          >
            <CheckCircle2 size={22} />
          </div>
          <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 700, marginBottom: '0.5rem' }}>
            2. Latin Sig Sig Translation
          </h3>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            Confusing abbreviations like "1 tab PO TID PC" are automatically converted into friendly, actionable instructions: "Take 1 tablet by mouth 3 times a day after meals."
          </p>
        </div>

        <div className="rx-card">
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '10px',
              background: 'rgba(99, 102, 241, 0.12)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--indigo-500, #6366f1)',
              marginBottom: '1rem'
            }}
          >
            <Volume2 size={22} />
          </div>
          <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 700, marginBottom: '0.5rem' }}>
            3. Audio TTS & Daily Checklist
          </h3>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            Listen aloud to any dosage instruction with Google Cloud Text-to-Speech, and track doses with an interactive Morning-to-Night daily schedule checklist.
          </p>
        </div>
      </div>
    </section>
  );
};
