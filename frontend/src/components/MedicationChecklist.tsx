import React, { useState } from 'react';
import {
  CheckSquare,
  Square,
  Printer,
  Sun,
  Sunset,
  Moon,
  Clock,
  AlertTriangle,
  Sparkles
} from 'lucide-react';
import { MedicationChecklistItem, TimeOfDay } from '../types';

interface MedicationChecklistProps {
  initialChecklist: MedicationChecklistItem[];
  onReadAloudChecklist: () => void;
}

export const MedicationChecklist: React.FC<MedicationChecklistProps> = ({
  initialChecklist,
  onReadAloudChecklist
}) => {
  const [items, setItems] = useState<MedicationChecklistItem[]>(initialChecklist);

  const toggleItem = (id: string) => {
    setItems((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, completed: !item.completed } : item
      )
    );
  };

  const handlePrint = () => {
    window.print();
  };

  // Group items by time of day
  const timeSlots: TimeOfDay[] = ['Morning', 'Afternoon', 'Evening', 'Bedtime', 'As Needed'];
  const grouped: Record<TimeOfDay, MedicationChecklistItem[]> = {
    Morning: [],
    Afternoon: [],
    Evening: [],
    Bedtime: [],
    'As Needed': []
  };

  items.forEach((item) => {
    if (grouped[item.time_of_day]) {
      grouped[item.time_of_day].push(item);
    } else {
      grouped['Morning'].push(item);
    }
  });

  const getTimeIcon = (slot: TimeOfDay) => {
    switch (slot) {
      case 'Morning':
        return <Sun size={18} style={{ color: 'var(--accent-warning)' }} />;
      case 'Afternoon':
        return <Sun size={18} style={{ color: 'var(--accent-primary)' }} />;
      case 'Evening':
        return <Sunset size={18} style={{ color: '#f97316' }} />;
      case 'Bedtime':
        return <Moon size={18} style={{ color: 'var(--indigo-500, #6366f1)' }} />;
      case 'As Needed':
        return <Clock size={18} style={{ color: 'var(--accent-success)' }} />;
    }
  };

  const completedCount = items.filter((i) => i.completed).length;

  return (
    <div
      className="rx-card"
      style={{
        backgroundColor: 'var(--bg-surface)',
        border: '1px solid var(--border-subtle)',
        padding: '1.75rem',
        marginBottom: '2rem'
      }}
    >
      {/* Checklist Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '1rem',
          marginBottom: '1.5rem',
          borderBottom: '1px solid var(--border-subtle)',
          paddingBottom: '1rem'
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <CheckSquare size={22} style={{ color: 'var(--accent-primary)' }} />
            <h3 style={{ fontSize: 'var(--text-lg)', fontWeight: 800, color: 'var(--text-primary)' }}>
              Interactive Daily Medication Checklist
            </h3>
          </div>
          <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            {completedCount} of {items.length} daily actions checked off
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <button
            type="button"
            onClick={onReadAloudChecklist}
            className="btn-secondary"
            style={{ padding: '0.45rem 0.85rem', fontSize: 'var(--text-xs)' }}
            title="Read aloud daily checklist schedule"
          >
            🔊 Listen to Schedule
          </button>

          <button
            type="button"
            onClick={handlePrint}
            className="btn-secondary"
            style={{ padding: '0.45rem 0.85rem', fontSize: 'var(--text-xs)' }}
            title="Print this medication checklist for your fridge or medicine cabinet"
          >
            <Printer size={15} />
            <span>Print Checklist</span>
          </button>
        </div>
      </div>

      {/* Grouped Time Slots */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {timeSlots.map((slot) => {
          const slotItems = grouped[slot];
          if (slotItems.length === 0) return null;

          return (
            <div key={slot}>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  marginBottom: '0.75rem',
                  fontSize: 'var(--text-sm)',
                  fontWeight: 700,
                  color: 'var(--text-primary)'
                }}
              >
                {getTimeIcon(slot)}
                <span>{slot} Schedule</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                {slotItems.map((item) => (
                  <div
                    key={item.id}
                    onClick={() => toggleItem(item.id)}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '0.85rem',
                      padding: '0.85rem 1rem',
                      borderRadius: '10px',
                      backgroundColor: item.completed
                        ? 'var(--bg-surface-subtle)'
                        : 'var(--bg-surface)',
                      border: `1px solid ${
                        item.completed
                          ? 'var(--border-subtle)'
                          : item.requires_verification
                          ? 'var(--accent-danger)'
                          : 'var(--border-strong)'
                      }`,
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                      opacity: item.completed ? 0.65 : 1
                    }}
                  >
                    <div style={{ marginTop: '2px', color: item.completed ? 'var(--accent-success)' : 'var(--text-muted)' }}>
                      {item.completed ? <CheckSquare size={20} /> : <Square size={20} />}
                    </div>

                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                        <span
                          style={{
                            fontSize: 'var(--text-sm)',
                            fontWeight: 700,
                            color: 'var(--text-primary)',
                            textDecoration: item.completed ? 'line-through' : 'none'
                          }}
                        >
                          {item.medication_name}
                        </span>
                        <span
                          style={{
                            fontSize: 'var(--text-xs)',
                            fontWeight: 600,
                            padding: '0.1rem 0.4rem',
                            borderRadius: '4px',
                            backgroundColor: 'var(--bg-surface-subtle)',
                            color: 'var(--accent-primary)'
                          }}
                        >
                          {item.dosage}
                        </span>
                        {item.requires_verification && (
                          <span className="badge badge-unclear">
                            <AlertTriangle size={12} /> Verify with Pharmacist
                          </span>
                        )}
                      </div>

                      <p
                        style={{
                          fontSize: 'var(--text-xs)',
                          color: 'var(--text-secondary)',
                          marginTop: '0.25rem'
                        }}
                      >
                        {item.instructions} • <strong>Food:</strong> {item.food_relation}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
