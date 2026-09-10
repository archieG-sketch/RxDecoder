export type ConfidenceLevel = 'high' | 'medium' | 'low' | 'unclear';
export type TimeOfDay = 'Morning' | 'Afternoon' | 'Evening' | 'Bedtime' | 'As Needed';

export interface MedicationAnalysis {
  uses_summary: string;
  how_to_take_plain: string;
  common_side_effects: string[];
  important_warnings: string[];
  serious_symptoms: string[];
  substance_allergy_warnings: string[];
  mechanism_summary?: string;
}

export interface MedicationItem {
  id: string;
  name: string;
  generic_name?: string;
  brand_name?: string;
  strength: string;
  dosage: string;
  frequency: string;
  route: string;
  duration: string;
  timing_instructions: string;
  food_instructions: string;
  additional_notes?: string;
  confidence: ConfidenceLevel;
  confidence_reason?: string;
  analysis?: MedicationAnalysis;
}

export interface InteractionItem {
  severity: 'low' | 'moderate' | 'high' | 'caution';
  medications_involved: string[];
  description: string;
  recommendation: string;
}

export interface InteractionCheck {
  has_potential_interactions: boolean;
  summary: string;
  interactions: InteractionItem[];
  verification_advice: string;
}

export interface MedicationChecklistItem {
  id: string;
  time_of_day: TimeOfDay;
  medication_name: string;
  dosage: string;
  instructions: string;
  food_relation: string;
  requires_verification: boolean;
  verification_reason?: string;
  completed: boolean;
}

export interface PHISanitizationReport {
  sanitized: boolean;
  masked_items_count: number;
  masked_types: string[];
  sanitized_text_preview: string;
  summary: string;
}

export interface PrescriptionDecodeResponse {
  success: boolean;
  session_id: string;
  original_file_name?: string;
  file_type: string;
  phi_report: PHISanitizationReport;
  raw_ocr_summary?: string;
  medications: MedicationItem[];
  interactions: InteractionCheck;
  checklist: MedicationChecklistItem[];
  simple_explanation: string;
  detailed_explanation: string;
  has_uncertain_handwriting: boolean;
  uncertainty_warning?: string;
  safety_disclaimer: string;
  tts_narration_script: string;
  processing_time_ms: number;
}

export interface PharmacyItem {
  id: string;
  name: string;
  distance_km: number;
  distance_miles: number;
  address: string;
  phone?: string;
  open_status: string;
  hours_summary: string;
  google_maps_url: string;
  inventory_disclaimer: string;
}

export interface PharmacySearchResponse {
  latitude?: number;
  longitude?: number;
  query_location?: string;
  pharmacies: PharmacyItem[];
  note: string;
}

export interface SamplePreset {
  id: string;
  title: string;
  category: string;
  description: string;
  image_url: string;
}

export type ThemeMode = 'light' | 'dark' | 'system';
export type FontSizeScale = 'normal' | 'large' | 'xlarge';
