import React from 'react';
import { AlertCircle, ShieldAlert, CheckCircle, Info } from 'lucide-react';
import { InteractionCheck } from '../types';

interface InteractionAlertProps {
  interactionCheck: InteractionCheck;
}

export const InteractionAlert: React.FC<InteractionAlertProps> = ({
  interactionCheck
}) => {
  const hasInteractions = interactionCheck.has_potential_interactions && interactionCheck.interactions.length > 0;

  return (
    <div
      className="rx-card"
      style={{
        marginBottom: '1.75rem',
        border: hasInteractions
          ? '1px solid var(--accent-warning)'
          : '1px solid var(--accent-success)',
        backgroundColor: hasInteractions
          ? 'var(--accent-warning-subtle)'
          : 'var(--accent-success-subtle)',
        padding: '1.25rem'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.85rem' }}>
        {hasInteractions ? (
          <ShieldAlert size={26} style={{ color: 'var(--accent-warning)', flexShrink: 0, marginTop: '2px' }} />
        ) : (
          <CheckCircle size={26} style={{ color: 'var(--accent-success)', flexShrink: 0, marginTop: '2px' }} />
        )}

        <div style={{ flex: 1 }}>
          <h3
            style={{
              fontSize: 'var(--text-base)',
              fontWeight: 800,
              color: hasInteractions ? 'var(--accent-warning)' : 'var(--accent-success)',
              marginBottom: '0.35rem'
            }}
          >
            {hasInteractions
              ? 'Potential Medication Interaction Awareness'
              : 'Multi-Medication Safety Check: No Severe Conflicts'}
          </h3>

          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-primary)', lineHeight: 1.5, marginBottom: '0.75rem' }}>
            {interactionCheck.summary}
          </p>

          {/* Interaction Details List */}
          {hasInteractions && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '0.75rem' }}>
              {interactionCheck.interactions.map((item, idx) => (
                <div
                  key={idx}
                  style={{
                    backgroundColor: 'var(--bg-surface)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '8px',
                    padding: '0.75rem 1rem'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.2rem' }}>
                    <strong style={{ fontSize: 'var(--text-xs)', textTransform: 'uppercase', color: 'var(--accent-warning)' }}>
                      Between: {item.medications_involved.join(' + ')}
                    </strong>
                  </div>
                  <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
                    {item.description}
                  </p>
                  <p style={{ fontSize: 'var(--text-xs)', color: 'var(--accent-primary)', fontWeight: 600 }}>
                    💡 Guidance: {item.recommendation}
                  </p>
                </div>
              ))}
            </div>
          )}

          <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', fontStyle: 'italic' }}>
            {interactionCheck.verification_advice}
          </p>
        </div>
      </div>
    </div>
  );
};
