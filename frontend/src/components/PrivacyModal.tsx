import React from 'react';
import { ShieldCheck, Lock, EyeOff, Server, X, CheckCircle2 } from 'lucide-react';

interface PrivacyModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const PrivacyModal: React.FC<PrivacyModalProps> = ({
  isOpen,
  onClose
}) => {
  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="privacy-modal-title"
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
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
          maxWidth: '680px',
          maxHeight: '90vh',
          backgroundColor: 'var(--bg-surface)',
          padding: '1.75rem',
          borderRadius: '20px',
          overflowY: 'auto'
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <div
              style={{
                width: '38px',
                height: '38px',
                borderRadius: '10px',
                backgroundColor: 'rgba(99, 102, 241, 0.15)',
                color: 'var(--indigo-500, #6366f1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <ShieldCheck size={22} />
            </div>
            <div>
              <h3 id="privacy-modal-title" style={{ fontSize: 'var(--text-lg)', fontWeight: 800 }}>
                Protected Health Information (PHI) Guarantee
              </h3>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>
                How RxDecoder protects your sensitive personal medical data
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            style={{ background: 'transparent', color: 'var(--text-muted)', padding: '0.4rem' }}
            aria-label="Close Privacy Modal"
          >
            <X size={22} />
          </button>
        </div>

        {/* Core Principles Grid */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>
          <div
            style={{
              padding: '1rem',
              borderRadius: '12px',
              backgroundColor: 'var(--bg-surface-subtle)',
              border: '1px solid var(--border-subtle)',
              display: 'flex',
              gap: '0.75rem',
              alignItems: 'flex-start'
            }}
          >
            <EyeOff size={20} style={{ color: 'var(--accent-primary)', flexShrink: 0, marginTop: '2px' }} />
            <div>
              <h4 style={{ fontSize: 'var(--text-sm)', fontWeight: 700, marginBottom: '0.25rem' }}>
                1. Dedicated Stage-2 PHI Masking
              </h4>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                Before any prescription data is sent to clinical reasoning agents or translation models, our PHI Sanitization Agent scans and replaces personal identifiers:
              </p>
              <ul style={{ paddingLeft: '1.25rem', marginTop: '0.4rem', fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>
                <li>Patient Full Name & Initials → <code>[PATIENT_NAME_MASKED]</code></li>
                <li>Date of Birth & Age → <code>[DOB_MASKED]</code></li>
                <li>Home Address & Zip Code → <code>[ADDRESS_MASKED]</code></li>
                <li>Phone Numbers & Emails → <code>[PHONE_MASKED]</code></li>
                <li>Medical Record Number (MRN) & Rx ID → <code>[MRN_MASKED]</code></li>
              </ul>
            </div>
          </div>

          <div
            style={{
              padding: '1rem',
              borderRadius: '12px',
              backgroundColor: 'var(--bg-surface-subtle)',
              border: '1px solid var(--border-subtle)',
              display: 'flex',
              gap: '0.75rem',
              alignItems: 'flex-start'
            }}
          >
            <Lock size={20} style={{ color: 'var(--accent-success)', flexShrink: 0, marginTop: '2px' }} />
            <div>
              <h4 style={{ fontSize: 'var(--text-sm)', fontWeight: 700, marginBottom: '0.25rem' }}>
                2. Ephemeral Processing & Zero Long-Term Storage
              </h4>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                Uploaded images and PDFs are processed purely in ephemeral memory for the duration of your session. We do not permanently store or retain your prescription images or share them with third parties.
              </p>
            </div>
          </div>

          <div
            style={{
              padding: '1rem',
              borderRadius: '12px',
              backgroundColor: 'var(--bg-surface-subtle)',
              border: '1px solid var(--border-subtle)',
              display: 'flex',
              gap: '0.75rem',
              alignItems: 'flex-start'
            }}
          >
            <Server size={20} style={{ color: 'var(--indigo-500, #6366f1)', flexShrink: 0, marginTop: '2px' }} />
            <div>
              <h4 style={{ fontSize: 'var(--text-sm)', fontWeight: 700, marginBottom: '0.25rem' }}>
                3. Masked Server Logs
              </h4>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                All backend system logging applies real-time regex sanitization, ensuring that zero patient names, dates, or contact details are ever written to console output or application log files.
              </p>
            </div>
          </div>
        </div>

        <button
          onClick={onClose}
          className="btn-primary"
          style={{ width: '100%', justifyContent: 'center', borderRadius: '12px' }}
        >
          <span>I Understand — Continue to RxDecoder</span>
        </button>
      </div>
    </div>
  );
};
