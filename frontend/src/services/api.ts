import axios from 'axios';
import {
  PrescriptionDecodeResponse,
  PharmacySearchResponse,
  SamplePreset
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 45000,
});

export const api = {
  async checkHealth() {
    try {
      const resp = await apiClient.get('/api/health');
      return resp.data;
    } catch {
      return { status: 'offline' };
    }
  },

  async fetchSamples(): Promise<SamplePreset[]> {
    const resp = await apiClient.get<SamplePreset[]>('/api/samples');
    return resp.data;
  },

  async decodeSample(sampleId: string): Promise<PrescriptionDecodeResponse> {
    const resp = await apiClient.post<PrescriptionDecodeResponse>('/api/decode/sample', {
      sample_id: sampleId
    });
    return resp.data;
  },

  async decodePrescription(file: File): Promise<PrescriptionDecodeResponse> {
    const formData = new FormData();
    formData.append('file', file);
    const resp = await apiClient.post<PrescriptionDecodeResponse>('/api/decode', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return resp.data;
  },

  async synthesizeTTS(
    text: string,
    speed: number = 1.0,
    voiceGender: 'FEMALE' | 'MALE' | 'NEUTRAL' = 'NEUTRAL'
  ): Promise<Blob | null> {
    try {
      const resp = await apiClient.post(
        '/api/tts/synthesize',
        {
          text,
          speed,
          voice_gender: voiceGender,
          language_code: 'en-US'
        },
        {
          responseType: 'blob'
        }
      );
      if (resp.status === 200 && resp.data.size > 0) {
        return resp.data;
      }
      return null;
    } catch (e) {
      console.warn('Backend TTS call failed, client speech synthesis will be used:', e);
      return null;
    }
  },

  async fetchNearbyPharmacies(
    lat?: number,
    lon?: number,
    query?: string
  ): Promise<PharmacySearchResponse> {
    const params = new URLSearchParams();
    if (lat !== undefined) params.append('lat', lat.toString());
    if (lon !== undefined) params.append('lon', lon.toString());
    if (query) params.append('query', query);

    const resp = await apiClient.get<PharmacySearchResponse>(`/api/pharmacies?${params.toString()}`);
    return resp.data;
  }
};
