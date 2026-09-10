import { api } from '../services/api';

export class VoiceNarrationController {
  private currentAudio: HTMLAudioElement | null = null;
  private currentUtterance: SpeechSynthesisUtterance | null = null;
  private onStateChangeCallback: ((state: 'playing' | 'paused' | 'stopped') => void) | null = null;

  public state: 'playing' | 'paused' | 'stopped' = 'stopped';
  public currentSpeed: number = 1.0;

  constructor() {
    // Handle end events
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.onvoiceschanged = () => {
        // Voice list ready
      };
    }
  }

  public setCallback(cb: (state: 'playing' | 'paused' | 'stopped') => void) {
    this.onStateChangeCallback = cb;
  }

  private updateState(newState: 'playing' | 'paused' | 'stopped') {
    this.state = newState;
    if (this.onStateChangeCallback) {
      this.onStateChangeCallback(newState);
    }
  }

  public async speakText(text: string, speed: number = 1.0) {
    this.stop();
    this.currentSpeed = speed;

    if (!text || text.trim().length === 0) return;

    // Try Google Cloud TTS via Backend API first
    const audioBlob = await api.synthesizeTTS(text, speed);
    if (audioBlob) {
      const audioUrl = URL.createObjectURL(audioBlob);
      this.currentAudio = new Audio(audioUrl);
      this.currentAudio.playbackRate = speed;
      
      this.currentAudio.onplay = () => this.updateState('playing');
      this.currentAudio.onpause = () => {
        if (this.state !== 'stopped') this.updateState('paused');
      };
      this.currentAudio.onended = () => this.updateState('stopped');
      this.currentAudio.onerror = () => {
        this.fallbackClientSpeech(text, speed);
      };

      try {
        await this.currentAudio.play();
        return;
      } catch (e) {
        console.warn('Audio element play failed, falling back to Web Speech:', e);
      }
    }

    // Fallback to client-side Web Speech API
    this.fallbackClientSpeech(text, speed);
  }

  private fallbackClientSpeech(text: string, speed: number) {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      console.warn('Speech synthesis not supported in this browser.');
      this.updateState('stopped');
      return;
    }

    window.speechSynthesis.cancel();

    // Clean markdown asterisks and bullet symbols for natural pronunciation
    const cleanText = text
      .replace(/[*#_`]/g, '')
      .replace(/•/g, ' ')
      .replace(/\[.*?\]/g, '')
      .replace(/BID/gi, 'twice daily')
      .replace(/TID/gi, 'three times daily')
      .replace(/QID/gi, 'four times daily')
      .replace(/PO/gi, 'by mouth')
      .replace(/PRN/gi, 'as needed')
      .replace(/mg/gi, 'milligrams')
      .replace(/mcg/gi, 'micrograms')
      .replace(/mL/gi, 'milliliters');

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = speed;
    utterance.pitch = 1.0;
    utterance.lang = 'en-US';

    // Pick best English voice if available
    const voices = window.speechSynthesis.getVoices();
    const naturalVoice = voices.find(v => (v.name.includes('Google') || v.name.includes('Natural') || v.name.includes('Samantha') || v.name.includes('Daniel')) && v.lang.startsWith('en'));
    if (naturalVoice) {
      utterance.voice = naturalVoice;
    }

    utterance.onstart = () => this.updateState('playing');
    utterance.onpause = () => this.updateState('paused');
    utterance.onresume = () => this.updateState('playing');
    utterance.onend = () => this.updateState('stopped');
    utterance.onerror = () => this.updateState('stopped');

    this.currentUtterance = utterance;
    window.speechSynthesis.speak(utterance);
  }

  public pause() {
    if (this.currentAudio && !this.currentAudio.paused) {
      this.currentAudio.pause();
      this.updateState('paused');
    } else if (typeof window !== 'undefined' && 'speechSynthesis' in window && window.speechSynthesis.speaking) {
      window.speechSynthesis.pause();
      this.updateState('paused');
    }
  }

  public resume() {
    if (this.currentAudio && this.currentAudio.paused) {
      this.currentAudio.play();
      this.updateState('playing');
    } else if (typeof window !== 'undefined' && 'speechSynthesis' in window && window.speechSynthesis.paused) {
      window.speechSynthesis.resume();
      this.updateState('playing');
    }
  }

  public stop() {
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio.currentTime = 0;
      this.currentAudio = null;
    }
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      this.currentUtterance = null;
    }
    this.updateState('stopped');
  }

  public setSpeed(speed: number) {
    this.currentSpeed = speed;
    if (this.currentAudio) {
      this.currentAudio.playbackRate = speed;
    }
  }
}

export const ttsController = new VoiceNarrationController();
