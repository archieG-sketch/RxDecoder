import React, { useEffect, useState } from 'react';
import {
  Scan,
  ShieldCheck,
  FileCode,
  HeartPulse,
  Sparkles,
  CheckCircle2,
  Loader2
} from 'lucide-react';
import { PHISanitizationReport } from '../types';

interface ProcessingPipelineProps {
  currentStage: number; // 1 to 5
  phiReport?: PHISanitizationReport;
}

const STAGES = [
  {
    id: 1,
    title: 'Reading Prescription',
    description: 'Multimodal vision transcription & handwriting legibility assessment',
    icon: Scan
  },
  {
    id: 2,
    title: 'Protecting Personal Information',
    description: 'HIPAA-compliant de-identification of names, DOB, addresses, and patient IDs',
    icon: ShieldCheck
  },
  {
    id: 3,
    title: 'Extracting Medication Information',
    description: 'Translating Latin sig codes, dosages, frequencies, and administration routes',
    icon: FileCode
  },
  {
    id: 4,
    title: 'Checking Medication Information',
    description: 'Verifying drug uses, side effects, precautions, and multi-drug interaction safety',
    icon: HeartPulse
  },
  {
    id: 5,
    title: 'Preparing Your Explanation',
    description: 'Generating friendly 5th-grade explanation, daily schedule checklist, and TTS narration',
    icon: Sparkles
  }
];

export const ProcessingPipeline: React.FC<ProcessingPipelineProps> = ({
  currentStage,
  phiReport
}) => {
  return (
    <div
      className="rx-card"
      style={{
        maxWidth: '850px',
        margin: '0 auto 2.5rem',
        padding: '2rem',
        backgroundColor: 'var(--bg-surface)',
        border: '1px solid var(--border-subtle)',
        boxShadow: 'var(--shadow-md)'
      }}
    >
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h3 style={{ fontSize: 'var(--text-xl)', fontWeight: 800, marginBottom: '0.5rem' }}>
          Decoding Your Prescription
        </h3>
        <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)' }}>
          Processing with privacy-first multi-agent AI pipeline
        </p>
      </div>

      {/* 5-Step Process Timeline */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {STAGES.map((stage) => {
          const Icon = stage.icon;
          const isCompleted = currentStage > stage.id;
          const isCurrent = currentStage === stage.id;
          const isPending = currentStage < stage.id;

          return (
            <div
              key={stage.id}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '1rem',
                padding: '1rem',
                borderRadius: '12px',
                backgroundColor: isCurrent
                  ? 'var(--accent-primary-subtle)'
                  : isCompleted
                  ? 'var(--bg-surface-subtle)'
                  : 'transparent',
                border: `1px solid ${
                  isCurrent
                    ? 'var(--accent-primary)'
                    : isCompleted
                    ? 'var(--border-subtle)'
                    : 'transparent'
                }`,
                transition: 'all 0.3s ease'
              }}
            >
              {/* Status Icon */}
              <div
                style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: '10px',
                  backgroundColor: isCompleted
                    ? 'var(--accent-success-subtle)'
                    : isCurrent
                    ? 'var(--accent-primary)'
                    : 'var(--bg-surface-subtle)',
                  color: isCompleted
                    ? 'var(--accent-success)'
                    : isCurrent
                    ? '#ffffff'
                    : 'var(--text-muted)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}
              >
                {isCompleted ? (
                  <CheckCircle2 size={20} />
                ) : isCurrent ? (
                  <Loader2 size={20} style={{ animation: 'spin 1s linear infinite' }} />
                ) : (
                  <Icon size={18} />
                )}
              </div>

              {/* Text */}
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap' }}>
                  <h4
                    style={{
                      fontSize: 'var(--text-base)',
                      fontWeight: 700,
                      color: isPending ? 'var(--text-muted)' : 'var(--text-primary)'
                    }}
                  >
                    Stage {stage.id}: {stage.title}
                  </h4>
                  <span
                    style={{
                      fontSize: 'var(--text-xs)',
                      fontWeight: 600,
                      color: isCompleted
                        ? 'var(--accent-success)'
                        : isCurrent
                        ? 'var(--accent-primary)'
                        : 'var(--text-muted)'
                    }}
                  >
                    {isCompleted ? 'Complete' : isCurrent ? 'In Progress...' : 'Waiting'}
                  </span>
                </div>
                <p
                  style={{
                    fontSize: 'var(--text-xs)',
                    color: isPending ? 'var(--text-muted)' : 'var(--text-secondary)',
                    marginTop: '0.25rem'
                  }}
                >
                  {stage.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* PHI Sanitization Live Transparency Badge */}
      {phiReport && (
        <div
          style={{
            marginTop: '1.75rem',
            padding: '1rem',
            borderRadius: '12px',
            backgroundColor: 'rgba(99, 102, 241, 0.08)',
            border: '1px solid rgba(99, 102, 241, 0.25)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem'
          }}
        >
          <ShieldCheck size={24} style={{ color: 'var(--indigo-500, #6366f1)', flexShrink: 0 }} />
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
              <span style={{ fontSize: 'var(--text-sm)', fontWeight: 700, color: 'var(--text-primary)' }}>
                PHI Privacy Protection Active:
              </span>
              <span className="badge badge-phi">
                {phiReport.masked_items_count} Identifiers Masked
              </span>
            </div>
            <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', margin: '0.25rem 0 0' }}>
              Masked types: {phiReport.masked_types.join(', ')}. Downstream AI only processes sanitized medication directives.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
