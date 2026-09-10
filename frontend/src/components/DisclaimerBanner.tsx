import React from 'react';
import { AlertTriangle, ShieldCheck } from 'lucide-react';

export const DisclaimerBanner: React.FC = () => {
  return (
    <div
      role="region"
      aria-label="Medical Disclaimer"
      style={{
        background: 'linear-gradient(90deg, rgba(2, 132, 199, 0.12), rgba(16, 185, 129, 0.12))',
        borderBottom: '1px solid var(--border-subtle)',
        padding: '0.6rem 1rem',
        fontSize: 'var(--text-xs)',
        color: 'var(--text-secondary)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '0.6rem',
        textAlign: 'center',
        flexWrap: 'wrap'
      }}
    >
      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', fontWeight: 600, color: 'var(--accent-primary)' }}>
        <ShieldCheck size={16} /> Privacy-First Educational Assistant:
      </span>
      <span>
        RxDecoder helps patients & caregivers understand prescriptions in plain language. It does <strong>not</strong> diagnose, prescribe, change dosages, or replace your doctor or pharmacist.
      </span>
    </div>
  );
};
