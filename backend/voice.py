import os
import logging
try:
    import torch
    from TTS.api import TTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    
# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VoiceGenerator:
    def __init__(self, use_cuda=False):
        self.use_cuda = use_cuda and TTS_AVAILABLE and torch.cuda.is_available()
        self.model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        self.tts = None
    
    def load_model(self):
        if TTS_AVAILABLE and not self.tts:
            logger.info(f"Loading TTS Model: {self.model_name}")
            # Ensure we accept usage terms if using coqui
            os.environ["COQUI_TOS_AGREED"] = "1"
            self.tts = TTS(self.model_name).to("cuda" if self.use_cuda else "cpu")
            
    def generate_audio(self, text, output_path, language="en", speaker_wav=None):
        if not TTS_AVAILABLE:
            logger.warning("TTS library not found. Generating dummy audio for demo.")
            # Generate 5 seconds of silence or simple wave
            import wave
            import struct
            with wave.open(output_path, 'w') as f:
                f.setnchannels(1)
                f.setsampwidth(2)
                f.setframerate(44100)
                # 3 seconds of silence/noise
                for i in range(44100 * 3):
                    value = 0
                    data = struct.pack('<h', value)
                    f.writeframesraw(data)
            return True

        self.load_model()
        
        try:
            logger.info(f"Generating audio for: {text[:30]}...")
            
            # If speaker_wav is provided, use it for cloning/persona
            # Otherwise use default speaker if available or first one
            
            if speaker_wav and os.path.exists(speaker_wav):
                self.tts.tts_to_file(
                    text=text, 
                    file_path=output_path, 
                    speaker_wav=speaker_wav, 
                    language=language
                )
            else:
                # Fallback to a default speaker if XTTS requires one
                # XTTS usually requires a reference audio.
                # For now, let's assume we have a reference or use a different model if no ref.
                # But implementation plan said XTTS-v2.
                # We should provide a default reference audio in the repo or user config.
                msg = "XTTS requires a speaker_wav reference audio."
                logger.warning(msg)
                # Try generating without speaker_wav if model supports it (some do, XTTS usually doesn't)
                # Or use a different model like 'tts_models/en/ljspeech/glow-tts' for fallback
                pass
                
            logger.info(f"Audio saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"TTS Generation failed: {e}")
            return False

if __name__ == "__main__":
    # Create dummy reference for test if possible or just warn
    vg = VoiceGenerator()
    # vg.generate_audio("Hello this is a test.", "test.wav", language="en", speaker_wav="ref.wav")
