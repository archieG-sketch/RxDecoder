import React, { useState } from 'react';
import {
  Pill,
  ChevronDown,
  ChevronUp,
  Volume2,
  AlertTriangle,
  AlertOctagon,
  Info,
  Clock,
  Utensils,
  ShieldAlert,
  Sparkles,
  HelpCircle
} from 'lucide-react';
import { MedicationItem } from '../types';
import { ttsController } from '../utils/tts';

interface MedicationCardProps {
  medication: MedicationItem;
  mode: 'simple' | 'detailed';
  onReadAloud: (text: string) => void;
}

export const MedicationCard: React.FC<MedicationCardProps> = ({
  medication,
  mode,
  onReadAloud
}) => {
  const [isExpanded, setIsExpanded] = useState<boolean>(true);

  const getConfidenceBadge = () => {
    switch (medication.confidence) {
      case 'high':
        return <span className="badge badge-high">High Confidence (Verified)</span>;
      case 'medium':
        return <span className="badge badge-medium">Moderate Confidence</span>;
      case 'low':
      case 'unclear':
        return <span className="badge badge-unclear">⚠️ Needs Verification</span>;
      default:
        return null;
    }
  };

  const isLowConfidence = medication.confidence === 'low' || medication.confidence === 'unclear';

  const handleSpeakMedication = (e: React.MouseEvent) => {
    e.stopPropagation();
    const script = `
      ${medication.name} ${medication.strength}. 
      Dosage: ${medication.dosage}, ${medication.frequency.toLowerCase()}. 
      ${medication.food_instructions}. 
      Duration: ${medication.duration}. 
      ${medication.analysis ? medication.analysis.how_to_take_plain : ''}
    `;
    onReadAloud(script);
  };

  return (
    <div
      className="rx-card"
      style={{
        border: isLowConfidence
          ? '2px solid var(--accent-danger)'
          : '1px solid var(--border-subtle)',
        boxShadow: isLowConfidence ? '0 0 15px rgba(239, 68, 68, 0.15)' : 'var(--shadow-sm)',
        backgroundColor: 'var(--bg-surface)',
        marginBottom: '1.25rem',
        overflow: 'hidden'
      }}
    >
      {/* Card Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          flexWrap: 'wrap',
          gap: '1rem',
          cursor: 'pointer'
        }}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.85rem' }}>
          <div
            style={{
              width: '46px',
              height: '46px',
              borderRadius: '12px',
              backgroundColor: isLowConfidence ? 'var(--accent-danger-subtle)' : 'var(--accent-primary-subtle)',
              color: isLowConfidence ? 'var(--accent-danger)' : 'var(--accent-primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}
          >
            <Pill size={24} />
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flexWrap: 'wrap' }}>
              <h3 style={{ fontSize: 'var(--text-lg)', fontWeight: 800, color: 'var(--text-primary)' }}>
                {medication.name}
              </h3>
              <span
                style={{
                  fontSize: 'var(--text-sm)',
                  fontWeight: 700,
                  color: 'var(--accent-primary)',
                  backgroundColor: 'var(--bg-surface-subtle)',
                  padding: '0.2rem 0.6rem',
                  borderRadius: '6px'
                }}
              >
                {medication.strength}
              </span>
              {getConfidenceBadge()}
            </div>

            {medication.generic_name && medication.generic_name !== medication.name && (
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                Generic: <strong>{medication.generic_name}</strong> {medication.brand_name ? `• Brand: ${medication.brand_name}` : ''}
              </p>
            )}
          </div>
        </div>

        {/* Read Aloud & Expand Toggles */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <button
            type="button"
            onClick={handleSpeakMedication}
            className="btn-secondary"
            style={{ padding: '0.45rem 0.8rem', fontSize: 'var(--text-xs)', borderRadius: '8px' }}
            title="Read Aloud this medication's instructions"
            aria-label={`Read Aloud ${medication.name} instructions`}
          >
            <Volume2 size={16} />
            <span>Read Aloud</span>
          </button>

          <button
            type="button"
            style={{
              background: 'transparent',
              color: 'var(--text-muted)',
              padding: '0.45rem',
              display: 'flex',
              alignItems: 'center'
            }}
            aria-label={isExpanded ? 'Collapse card' : 'Expand card'}
          >
            {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </button>
        </div>
      </div>

      {/* Low Confidence / Uncertain Handwriting Banner */}
      {isLowConfidence && (
        <div
          style={{
            marginTop: '1rem',
            padding: '0.85rem 1rem',
            borderRadius: '10px',
            backgroundColor: 'var(--accent-danger-subtle)',
            border: '1px solid var(--accent-danger)',
            color: 'var(--text-primary)',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '0.75rem'
          }}
        >
          <AlertTriangle size={20} style={{ color: 'var(--accent-danger)', flexShrink: 0, marginTop: '2px' }} />
          <div>
            <strong style={{ color: 'var(--accent-danger)', display: 'block', fontSize: 'var(--text-sm)', marginBottom: '0.2rem' }}>
              Pharmacist Verification Recommended:
            </strong>
            <span style={{ fontSize: 'var(--text-xs)' }}>
              {medication.confidence_reason ||
                'Medication name could not be identified with sufficient confidence due to handwriting. Please verify this with your pharmacist or doctor before taking it.'}
            </span>
          </div>
        </div>
      )}

      {/* Core Dosage & Schedule Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '0.75rem',
          margin: '1.25rem 0',
          backgroundColor: 'var(--bg-surface-subtle)',
          padding: '1rem',
          borderRadius: '12px',
          border: '1px solid var(--border-subtle)'
        }}
      >
        <div>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <Clock size={14} /> How Often (Frequency):
          </span>
          <p style={{ fontSize: 'var(--text-sm)', fontWeight: 700, marginTop: '0.2rem', color: 'var(--text-primary)' }}>
            {medication.frequency}
          </p>
        </div>

        <div>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <Pill size={14} /> Amount per Dose:
          </span>
          <p style={{ fontSize: 'var(--text-sm)', fontWeight: 700, marginTop: '0.2rem', color: 'var(--text-primary)' }}>
            {medication.dosage} ({medication.route})
          </p>
        </div>

        <div>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <Utensils size={14} /> Food Directions:
          </span>
          <p style={{ fontSize: 'var(--text-sm)', fontWeight: 700, marginTop: '0.2rem', color: 'var(--text-primary)' }}>
            {medication.food_instructions}
          </p>
        </div>

        <div>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)' }}>
            ⏳ Duration:
          </span>
          <p style={{ fontSize: 'var(--text-sm)', fontWeight: 700, marginTop: '0.2rem', color: 'var(--text-primary)' }}>
            {medication.duration}
          </p>
        </div>
      </div>

      {/* Expandable Sections */}
      {isExpanded && medication.analysis && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', borderTop: '1px solid var(--border-subtle)', paddingTop: '1.25rem' }}>
          {/* 1. What it is used for */}
          <div>
            <h4 style={{ fontSize: 'var(--text-sm)', fontWeight: 700, color: 'var(--accent-primary)', marginBottom: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Info size={16} /> What this medicine is generally used for:
            </h4>
            <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              {medication.analysis.uses_summary}
            </p>
          </div>

          {/* 2. How to take it */}
          <div>
            <h4 style={{ fontSize: 'var(--text-sm)', fontWeight: 700, color: 'var(--accent-success)', marginBottom: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Sparkles size={16} /> How to take it:
            </h4>
            <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              {medication.analysis.how_to_take_plain}
            </p>
          </div>

          {/* 3. Common Side Effects */}
          {medication.analysis.common_side_effects.length > 0 && (
            <div>
              <h4 style={{ fontSize: 'var(--text-sm)', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.35rem' }}>
                Common Side Effects (usually mild):
              </h4>
              <ul style={{ paddingLeft: '1.25rem', fontSize: 'var(--text-sm)', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                {medication.analysis.common_side_effects.map((se, idx) => (
                  <li key={idx}>{se}</li>
                ))}
              </ul>
            </div>
          )}

          {/* 4. Important Warnings (Distinct from side effects) */}
          {medication.analysis.important_warnings.length > 0 && (
            <div
              style={{
                backgroundColor: 'var(--accent-warning-subtle)',
                border: '1px solid var(--accent-warning)',
                borderRadius: '10px',
                padding: '0.85rem 1rem'
              }}
            >
              <h4 style={{ fontSize: 'var(--text-sm)', fontWeight: 700, color: 'var(--accent-warning)', marginBottom: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <AlertTriangle size={16} /> Important Warnings & Precautions:
              </h4>
              <ul style={{ paddingLeft: '1.25rem', fontSize: 'var(--text-sm)', color: 'var(--text-primary)', lineHeight: 1.4 }}>
                {medication.analysis.important_warnings.map((w, idx) => (
                  <li key={idx}>{w}</li>
                ))}
              </ul>
            </div>
          )}

          {/* 5. Serious Symptoms (Requiring prompt medical attention) */}
          {medication.analysis.serious_symptoms.length > 0 && (
            <div
              style={{
                backgroundColor: 'var(--accent-danger-subtle)',
                border: '1px solid var(--accent-danger)',
                borderRadius: '10px',
                padding: '0.85rem 1rem'
              }}
            >
              <h4 style={{ fontSize: 'var(--text-sm)', fontWeight: 700, color: 'var(--accent-danger)', marginBottom: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <AlertOctagon size={16} /> Serious Symptoms (Seek prompt medical care):
              </h4>
              <ul style={{ paddingLeft: '1.25rem', fontSize: 'var(--text-sm)', color: 'var(--text-primary)', lineHeight: 1.4 }}>
                {medication.analysis.serious_symptoms.map((ss, idx) => (
                  <li key={idx}>{ss}</li>
                ))}
              </ul>
            </div>
          )}

          {/* 6. Allergen / Substance Warnings */}
          {medication.analysis.substance_allergy_warnings.length > 0 && (
            <div>
              <h4 style={{ fontSize: 'var(--text-xs)', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                Allergy & Substance Notes:
              </h4>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)' }}>
                {medication.analysis.substance_allergy_warnings.join(' ')}
              </p>
            </div>
          )}

          {/* 7. Detailed Medical Mode Extra Details */}
          {mode === 'detailed' && medication.analysis.mechanism_summary && (
            <div
              style={{
                borderTop: '1px dashed var(--border-subtle)',
                paddingTop: '0.75rem',
                fontSize: 'var(--text-xs)',
                color: 'var(--text-muted)'
              }}
            >
              <strong style={{ color: 'var(--text-secondary)' }}>Pharmacological Class & Mechanism: </strong>
              {medication.analysis.mechanism_summary}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
