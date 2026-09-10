import React from 'react';
import { Shield, AlertCircle, Heart, PhoneCall } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer
      style={{
        marginTop: '4rem',
        borderTop: '1px solid var(--border-subtle)',
        backgroundColor: 'var(--bg-surface)',
        padding: '2.5rem 1.5rem',
        color: 'var(--text-secondary)',
        fontSize: 'var(--text-sm)'
      }}
    >
      <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {/* Medical Safety Disclaimer Callout */}
        <div
          style={{
            background: 'var(--bg-surface-subtle)',
            borderLeft: '4px solid var(--accent-warning)',
            padding: '1.25rem',
            borderRadius: '0 12px 12px 0',
            display: 'flex',
            gap: '1rem',
            alignItems: 'flex-start'
          }}
        >
          <AlertCircle size={24} style={{ color: 'var(--accent-warning)', flexShrink: 0, marginTop: '2px' }} />
          <div>
            <h4 style={{ fontSize: 'var(--text-base)', marginBottom: '0.35rem', color: 'var(--text-primary)' }}>
              Important Healthcare & Safety Disclaimer
            </h4>
            <p style={{ lineHeight: 1.5, margin: 0 }}>
              RxDecoder is strictly an informational assistant designed to help patients and caregivers decipher handwriting and understand prescription abbreviations in simple language. It <strong>never diagnoses diseases</strong>, <strong>never prescribes treatments</strong>, and <strong>never recommends changing medication doses</strong>. If handwriting or dosage is ambiguous, always confirm with your doctor or licensed pharmacist. If experiencing a medical emergency, call 911 or your local emergency service immediately.
            </p>
          </div>
        </div>

        {/* Privacy & Trust Highlights */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '1.5rem',
            paddingTop: '1rem'
          }}
        >
          <div>
            <h5 style={{ color: 'var(--text-primary)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Shield size={18} style={{ color: 'var(--accent-primary)' }} /> Privacy & HIPAA Principles
            </h5>
            <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>
              Patient identifiers (names, dates of birth, addresses, phones, IDs) are masked during processing before reaching clinical AI agents. Original files are ephemeral and never retained.
            </p>
          </div>

          <div>
            <h5 style={{ color: 'var(--text-primary)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Heart size={18} style={{ color: 'var(--accent-success)' }} /> Patient-Centered Accessibility
            </h5>
            <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>
              Designed for elderly users and caregivers with high-contrast themes, scalable text, and Google Cloud natural voice text-to-speech audio guidance.
            </p>
          </div>

          <div>
            <h5 style={{ color: 'var(--text-primary)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <PhoneCall size={18} style={{ color: 'var(--indigo-500, #6366f1)' }} /> Pharmacist Verification
            </h5>
            <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>
              When handwriting confidence is low, RxDecoder immediately prompts user verification with their local dispensing pharmacy.
            </p>
          </div>
        </div>

        {/* Copyright */}
        <div
          style={{
            borderTop: '1px solid var(--border-subtle)',
            paddingTop: '1.25rem',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '1rem',
            fontSize: 'var(--text-xs)',
            color: 'var(--text-muted)'
          }}
        >
          <span>© {new Date().getFullYear()} RxDecoder. All rights reserved. Built with Google Cloud & Gemini AI.</span>
          <span>Version 1.0.0 • Production Quality Healthcare Assistant</span>
        </div>
      </div>
    </footer>
  );
};
