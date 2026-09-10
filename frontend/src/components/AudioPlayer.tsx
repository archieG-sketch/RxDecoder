import React, { useState, useEffect } from 'react';
import {
  Play,
  Pause,
  Square,
  Volume2
} from 'lucide-react';
import { ttsController } from '../utils/tts';

interface AudioPlayerProps {
  currentText: string;
  autoPlay?: boolean;
}

export const AudioPlayer: React.FC<AudioPlayerProps> = ({
  currentText,
  autoPlay = false
}) => {
  const [playState, setPlayState] = useState<'playing' | 'paused' | 'stopped'>('stopped');
  const [speed, setSpeed] = useState<number>(1.0);

  useEffect(() => {
    ttsController.setCallback((newState) => {
      setPlayState(newState);
    });
    if (autoPlay && currentText) {
      ttsController.speakText(currentText, speed);
    }
    return () => {
      ttsController.stop();
    };
  }, []);

  const handlePlay = () => {
    if (playState === 'paused') {
      ttsController.resume();
    } else {
      ttsController.speakText(currentText, speed);
    }
  };

  const handlePause = () => {
    ttsController.pause();
  };

  const handleStop = () => {
    ttsController.stop();
  };

  const handleSpeedChange = (newSpeed: number) => {
    setSpeed(newSpeed);
    ttsController.setSpeed(newSpeed);
  };

  if (!currentText || currentText.trim().length === 0) return null;

  return (
    <div
      role="region"
      aria-label="Text to Speech Controller"
      className="glass-panel"
      style={{
        position: 'sticky',
        bottom: '20px',
        maxWidth: '720px',
        margin: '1.5rem auto 0',
        padding: '0.85rem 1.25rem',
        borderRadius: '16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '0.75rem',
        boxShadow: 'var(--shadow-lg)',
        border: '1px solid var(--border-strong)',
        zIndex: 40
      }}
    >
      {/* Audio Icon & Status */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
        <div
          style={{
            width: '36px',
            height: '36px',
            borderRadius: '10px',
            backgroundColor: playState === 'playing' ? 'var(--accent-success)' : 'var(--accent-primary)',
            color: '#ffffff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          <Volume2 size={18} />
        </div>
        <div>
          <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
            Google Cloud Voice Reader
          </span>
          <p style={{ fontSize: 'var(--text-sm)', fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>
            {playState === 'playing'
              ? 'Reading Prescription Aloud...'
              : playState === 'paused'
              ? 'Narration Paused'
              : 'Listen to Medication Summary'}
          </p>
        </div>
      </div>

      {/* Playback Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        {playState === 'playing' ? (
          <button
            onClick={handlePause}
            className="btn-primary"
            style={{ padding: '0.5rem 1rem', borderRadius: '8px', fontSize: 'var(--text-xs)' }}
            title="Pause narration"
            aria-label="Pause narration"
          >
            <Pause size={16} />
            <span>Pause</span>
          </button>
        ) : (
          <button
            onClick={handlePlay}
            className="btn-primary"
            style={{ padding: '0.5rem 1.25rem', borderRadius: '8px', fontSize: 'var(--text-xs)' }}
            title="Play narration"
            aria-label="Play narration"
          >
            <Play size={16} />
            <span>{playState === 'paused' ? 'Resume' : 'Play Narration'}</span>
          </button>
        )}

        <button
          onClick={handleStop}
          className="btn-secondary"
          style={{ padding: '0.5rem 0.75rem', borderRadius: '8px', fontSize: 'var(--text-xs)' }}
          disabled={playState === 'stopped'}
          title="Stop narration"
          aria-label="Stop narration"
        >
          <Square size={15} />
          <span>Stop</span>
        </button>

        {/* Speaking Speed Controls */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            backgroundColor: 'var(--bg-surface-subtle)',
            borderRadius: '8px',
            border: '1px solid var(--border-subtle)',
            padding: '2px'
          }}
        >
          {[0.8, 1.0, 1.2].map((s) => (
            <button
              key={s}
              onClick={() => handleSpeedChange(s)}
              style={{
                padding: '0.35rem 0.5rem',
                fontSize: '0.75rem',
                fontWeight: 600,
                background: speed === s ? 'var(--bg-surface)' : 'transparent',
                color: speed === s ? 'var(--accent-primary)' : 'var(--text-muted)',
                borderRadius: '6px'
              }}
              title={`${s}x speaking speed`}
            >
              {s}x
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
