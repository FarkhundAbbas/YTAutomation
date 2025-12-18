try:
    from easynmt import EasyNMT
except ImportError:
    class EasyNMT:
        def __init__(self, *args): pass
        def translate(self, text, **kwargs): return text + " [Translated]"

import logging
import os

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TranslatorService:
    def __init__(self, model_input="opus-mt", load_on_init=False):
        # opus-mt is lightweight (Helsinki-NLP)
        self.model_name = model_input
        self.model = None
        if load_on_init:
            self.load_model()
            
    def load_model(self):
        logger.info(f"Loading Translation Model: {self.model_name}...")
        try:
            self.model = EasyNMT(self.model_name)
        except:
            # Fallback
            self.model = EasyNMT('mock')

    def translate(self, text, target_lang="en", source_lang="en"):
        if target_lang == source_lang:
            return text
            
        if not self.model:
            self.load_model()
            
        try:
            # EasyNMT handles language codes automatically
            translation = self.model.translate(text, target_lang=target_lang, source_lang=source_lang)
            return translation
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text

if __name__ == "__main__":
    ts = TranslatorService()
    print(ts.translate("Hello world", target_lang="es"))
