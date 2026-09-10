import React, { useState } from 'react';
import {
  FileText,
  Sparkles,
  Stethoscope,
  AlertTriangle,
  CheckCircle2,
  Share2,
  Download,
  RotateCcw,
  Pill,
  ShieldCheck,
  Eye,
  Home,
  ArrowUp,
  List
} from 'lucide-react';
import { PrescriptionDecodeResponse } from '../types';
import { MedicationCard } from './MedicationCard';
import { InteractionAlert } from './InteractionAlert';
import { MedicationChecklist } from './MedicationChecklist';
import { ImageViewer } from './ImageViewer';
import { AudioPlayer } from './AudioPlayer';

interface ResultsDashboardProps {
  data: PrescriptionDecodeResponse;
  originalImageSrc?: string;
  isPDF?: boolean;
  onReset: () => void;
  onOpenPharmacy: () => void;
}

export const ResultsDashboard: React.FC<ResultsDashboardProps> = ({
  data,
  originalImageSrc,
  isPDF,
  onReset,
  onOpenPharmacy
}) => {
  const [explanationMode, setExplanationMode] = useState<'simple' | 'detailed'>('simple');
  const [activeTab, setActiveTab] = useState<'overview' | 'checklist' | 'document'>('overview');
  const [activeTTSNarration, setActiveTTSNarration] = useState<string>(data.tts_narration_script || data.simple_explanation);

  const displayMedications = data.medications.filter((medication, index, medications) => {
    const identity = `${(medication.generic_name || medication.name).trim().toLowerCase()}|${medication.strength.trim().toLowerCase()}`;
    return medications.findIndex((candidate) => {
      const candidateIdentity = `${(candidate.generic_name || candidate.name).trim().toLowerCase()}|${candidate.strength.trim().toLowerCase()}`;
      return candidateIdentity === identity;
    }) === index;
  });

  const scrollToTop = () => window.scrollTo({ top: 0, behavior: 'smooth' });
  const jumpToMedications = () => {
    setActiveTab('overview');
    window.requestAnimationFrame(() => {
      document.getElementById('medications-section')?.scrollIntoView({ behavior: 'smooth' });
    });
  };

  const handleReadAloudCustom = (text: string) => {
    setActiveTTSNarration(text);
  };

  const handleReadChecklist = () => {
    const checklistText = `
      Here is your daily medication schedule. 
      ${data.checklist.map((c) => `In the ${c.time_of_day}, take ${c.medication_name}, ${c.dosage}, ${c.instructions}, ${c.food_relation}.`).join('. ')}
    `;
    setActiveTTSNarration(checklistText);
  };

  return (
    <div
      id="results-top"
      style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '1.5rem 1rem 4rem'
      }}
    >
      {/* Top Banner & Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
          marginBottom: '1.5rem',
          borderBottom: '1px solid var(--border-subtle)',
          paddingBottom: '1rem'
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flexWrap: 'wrap' }}>
            <h2 style={{ fontSize: 'var(--text-2xl)', fontWeight: 800, color: 'var(--text-primary)' }}>
              Prescription Understanding Summary
            </h2>
            <span className="badge badge-high">Decoded Successfully</span>
            {data.phi_report?.sanitized && (
              <span className="badge badge-phi">
                <ShieldCheck size={12} /> {data.phi_report.masked_items_count} PHI Masked
              </span>
            )}
          </div>
          <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            Processed in {data.processing_time_ms}ms • Document: {data.original_file_name || 'Prescription'}
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.6rem', flexWrap: 'wrap' }}>
          <button
            onClick={onReset}
            className="btn-secondary"
            style={{ padding: '0.55rem 1rem', fontSize: 'var(--text-xs)', borderRadius: '10px' }}
            title="Return home and upload another prescription"
          >
            <Home size={15} />
            <span>Back to Home</span>
          </button>

          <button
            onClick={onReset}
            className="btn-secondary"
            style={{ padding: '0.55rem 1rem', fontSize: 'var(--text-xs)', borderRadius: '10px' }}
            title="Upload another prescription"
          >
            <RotateCcw size={15} />
            <span>New Prescription</span>
          </button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1rem' }} aria-label="Results shortcuts">
        <button type="button" className="btn-secondary" onClick={jumpToMedications} style={{ padding: '0.45rem 0.75rem', fontSize: 'var(--text-xs)' }}>
          <List size={15} />
          <span>Jump to Medications</span>
        </button>
      </div>

      {/* Prominent Safety Warning for Uncertain Handwriting */}
      {data.has_uncertain_handwriting && (
        <div
          role="alert"
          style={{
            backgroundColor: 'var(--accent-danger-subtle)',
            border: '2px solid var(--accent-danger)',
            borderRadius: '16px',
            padding: '1.25rem 1.5rem',
            marginBottom: '1.75rem',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '1rem',
            boxShadow: '0 4px 14px rgba(239, 68, 68, 0.15)'
          }}
        >
          <AlertTriangle size={28} style={{ color: 'var(--accent-danger)', flexShrink: 0, marginTop: '2px' }} />
          <div>
            <h3 style={{ fontSize: 'var(--text-base)', fontWeight: 800, color: 'var(--accent-danger)', marginBottom: '0.35rem' }}>
              ⚠️ Verification Required: Ambiguous Doctor Handwriting Detected
            </h3>
            <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-primary)', lineHeight: 1.5, margin: 0 }}>
              {data.uncertainty_warning ||
                'Some information in this prescription could not be read with sufficient confidence. Please confirm the medication and dosage with your doctor or pharmacist before taking it.'}
            </p>
            <button
              onClick={onOpenPharmacy}
              className="btn-primary"
              style={{
                marginTop: '0.75rem',
                padding: '0.4rem 0.85rem',
                fontSize: 'var(--text-xs)',
                backgroundColor: 'var(--accent-danger)',
                borderColor: 'var(--accent-danger)'
              }}
            >
              Locate Nearby Pharmacy to Verify →
            </button>
          </div>
        </div>
      )}

      {/* Main Tabs Navigation */}
      <div
        role="tablist"
        style={{
          display: 'flex',
          gap: '0.5rem',
          borderBottom: '1px solid var(--border-subtle)',
          marginBottom: '1.75rem',
          flexWrap: 'wrap'
        }}
      >
        <button
          role="tab"
          aria-selected={activeTab === 'overview'}
          onClick={() => setActiveTab('overview')}
          style={{
            padding: '0.75rem 1.25rem',
            fontWeight: 700,
            fontSize: 'var(--text-sm)',
            borderBottom: activeTab === 'overview' ? '3px solid var(--accent-primary)' : '3px solid transparent',
            color: activeTab === 'overview' ? 'var(--accent-primary)' : 'var(--text-secondary)',
            background: 'transparent',
            borderRadius: '0',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.4rem'
          }}
        >
          <Pill size={18} />
          <span>Medications ({displayMedications.length})</span>
        </button>

        <button
          role="tab"
          aria-selected={activeTab === 'checklist'}
          onClick={() => setActiveTab('checklist')}
          style={{
            padding: '0.75rem 1.25rem',
            fontWeight: 700,
            fontSize: 'var(--text-sm)',
            borderBottom: activeTab === 'checklist' ? '3px solid var(--accent-primary)' : '3px solid transparent',
            color: activeTab === 'checklist' ? 'var(--accent-primary)' : 'var(--text-secondary)',
            background: 'transparent',
            borderRadius: '0',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.4rem'
          }}
        >
          <CheckCircle2 size={18} />
          <span>Daily Schedule Checklist ({data.checklist.length})</span>
        </button>

        {originalImageSrc && (
          <button
            role="tab"
            aria-selected={activeTab === 'document'}
            onClick={() => setActiveTab('document')}
            style={{
              padding: '0.75rem 1.25rem',
              fontWeight: 700,
              fontSize: 'var(--text-sm)',
              borderBottom: activeTab === 'document' ? '3px solid var(--accent-primary)' : '3px solid transparent',
              color: activeTab === 'document' ? 'var(--accent-primary)' : 'var(--text-secondary)',
              background: 'transparent',
              borderRadius: '0',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem'
            }}
          >
            <Eye size={18} />
            <span>View Original Document</span>
          </button>
        )}
      </div>

      {/* Tab 1: Overview & Medications */}
      {activeTab === 'overview' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1.75rem' }}>
          {/* Explanation Header Box with Dual Mode Toggle */}
          <div
            className="rx-card"
            style={{
              background: 'var(--bg-surface)',
              border: '1px solid var(--border-subtle)',
              padding: '1.75rem'
            }}
          >
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: '1rem',
                marginBottom: '1.25rem'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Sparkles size={22} style={{ color: 'var(--accent-primary)' }} />
                <h3 style={{ fontSize: 'var(--text-lg)', fontWeight: 800 }}>
                  {explanationMode === 'simple' ? 'Patient-Friendly Explanation' : 'Detailed Clinical Summary'}
                </h3>
              </div>

              {/* Dual Mode Switch */}
              <div
                role="group"
                aria-label="Explanation Level"
                style={{
                  display: 'flex',
                  backgroundColor: 'var(--bg-surface-subtle)',
                  borderRadius: '10px',
                  border: '1px solid var(--border-subtle)',
                  padding: '3px'
                }}
              >
                <button
                  type="button"
                  onClick={() => setExplanationMode('simple')}
                  style={{
                    padding: '0.45rem 0.95rem',
                    fontSize: 'var(--text-xs)',
                    fontWeight: 700,
                    borderRadius: '8px',
                    backgroundColor: explanationMode === 'simple' ? 'var(--bg-surface)' : 'transparent',
                    color: explanationMode === 'simple' ? 'var(--accent-primary)' : 'var(--text-muted)',
                    boxShadow: explanationMode === 'simple' ? 'var(--shadow-sm)' : 'none',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.35rem'
                  }}
                >
                  <Sparkles size={14} />
                  <span>Simple Explanation (Default)</span>
                </button>

                <button
                  type="button"
                  onClick={() => setExplanationMode('detailed')}
                  style={{
                    padding: '0.45rem 0.95rem',
                    fontSize: 'var(--text-xs)',
                    fontWeight: 700,
                    borderRadius: '8px',
                    backgroundColor: explanationMode === 'detailed' ? 'var(--bg-surface)' : 'transparent',
                    color: explanationMode === 'detailed' ? 'var(--accent-primary)' : 'var(--text-muted)',
                    boxShadow: explanationMode === 'detailed' ? 'var(--shadow-sm)' : 'none',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.35rem'
                  }}
                >
                  <Stethoscope size={14} />
                  <span>Detailed Medical</span>
                </button>
              </div>
            </div>

            {/* Formatted Explanation Text */}
            <div
              style={{
                fontSize: 'var(--text-base)',
                color: 'var(--text-secondary)',
                lineHeight: 1.65,
                whiteSpace: 'pre-line'
              }}
            >
              {explanationMode === 'simple' ? data.simple_explanation : data.detailed_explanation}
            </div>
          </div>

          {/* Multi-Drug Interactions Alert */}
          {data.interactions && <InteractionAlert interactionCheck={data.interactions} />}

          {/* List of Medications */}
          <div id="medications-section" style={{ scrollMarginTop: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <h3 style={{ fontSize: 'var(--text-lg)', fontWeight: 800, color: 'var(--text-primary)' }}>
                Prescribed Medications ({displayMedications.length})
              </h3>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>
                Click any medication card to expand full guidance
              </span>
            </div>

            {displayMedications.map((med) => (
              <MedicationCard
                key={med.id}
                medication={med}
                mode={explanationMode}
                onReadAloud={handleReadAloudCustom}
              />
            ))}
          </div>
        </div>
      )}

      {/* Tab 2: Interactive Checklist */}
      {activeTab === 'checklist' && (
        <div>
          <MedicationChecklist
            initialChecklist={data.checklist}
            onReadAloudChecklist={handleReadChecklist}
          />
        </div>
      )}

      {/* Tab 3: Original Document Viewer */}
      {activeTab === 'document' && originalImageSrc && (
        <div>
          <ImageViewer imageSrc={originalImageSrc} isPDF={isPDF} />
        </div>
      )}

      {/* Audio Controller Bar */}
      <AudioPlayer currentText={activeTTSNarration} autoPlay={false} />

      <div style={{ display: 'flex', justifyContent: 'center', marginTop: '1.5rem' }}>
        <button type="button" className="btn-secondary" onClick={scrollToTop} title="Return to the top of the results">
          <ArrowUp size={16} />
          <span>Back to Top</span>
        </button>
      </div>
    </div>
  );
};
