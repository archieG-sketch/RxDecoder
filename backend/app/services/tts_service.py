import io
from typing import Optional
from google.cloud import texttospeech
from app.utils.logger import logger

class TTSService:
    def __init__(self):
        self.client: Optional[texttospeech.TextToSpeechClient] = None
        try:
            # Authenticates automatically via Application Default Credentials (ADC)
            self.client = texttospeech.TextToSpeechClient()
            logger.info("TTSService: Google Cloud Text-to-Speech client initialized via ADC.")
        except Exception as e:
            logger.warning(f"TTSService: Cloud TTS client could not be initialized ({e}). Client-side Web Speech will handle voice narration.")

    async def synthesize_speech(
        self,
        text: str,
        voice_gender: str = "NEUTRAL",
        language_code: str = "en-US",
        speaking_rate: float = 1.0
    ) -> Optional[bytes]:
        """
        Synthesizes spoken audio from text using Google Cloud Text-to-Speech.
        Returns MP3 audio bytes or None if unavailable.
        """
        if not self.client or not text:
            return None

        try:
            # Set synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)

            # Map voice gender
            gender_enum = texttospeech.SsmlVoiceGender.NEUTRAL
            if voice_gender.upper() == "FEMALE":
                gender_enum = texttospeech.SsmlVoiceGender.FEMALE
            elif voice_gender.upper() == "MALE":
                gender_enum = texttospeech.SsmlVoiceGender.MALE

            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                ssml_gender=gender_enum
            )

            # Select MP3 audio format with custom speaking rate
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=max(0.7, min(speaking_rate, 1.5))
            )

            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )

            logger.info(f"TTSService: Successfully synthesized {len(response.audio_content)} bytes of MP3 audio.")
            return response.audio_content
        except Exception as e:
            logger.error(f"TTSService synthesis error: {e}")
            return None

tts_service = TTSService()
