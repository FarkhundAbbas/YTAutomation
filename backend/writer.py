import requests
import yaml
import os
import json
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIWriter:
    def __init__(self, ollama_url="http://localhost:11434"):
        self.ollama_url = ollama_url
        self.config = self.load_config()
        self.prompts = self.config['prompts']
        self.personas = self.config['personas']

    def load_config(self):
        config_path = os.path.join(os.getcwd(), 'config', 'prompts.yaml')
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def generate(self, model, prompt, system=None):
        payload = {
            "model": model, 
            "prompt": prompt, 
            "stream": False,
            "options": {
                "num_ctx": 4096,
                "temperature": 0.7
            }
        }
        if system:
            payload["system"] = system
            
        try:
            resp = requests.post(f"{self.ollama_url}/api/generate", json=payload)
            resp.raise_for_status()
            return resp.json()['response']
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            logger.warning("Returning MOCK content for demonstration.")
            return (
                f"[MOCK SCRIPT by {model}]\n"
                "Hook: Did you hear the latest shocking news?\n"
                f"Body: {prompt[:100]}...\n"
                "This is a simulated AI response because Ollama is not running.\n"
                "CTA: Subscribe for more tea!"
            )

    def rewrite_article(self, article_text, persona_key="gossip_queen", model="mistral"):
        persona = self.personas.get(persona_key)
        if not persona:
            logger.warning(f"Persona {persona_key} not found, using Gossip Queen default.")
            persona = self.personas.get('gossip_queen')

        # Construct System Prompt
        system_prompt = (
            f"You are {persona['name']}. "
            f"Your tone is {persona['tone']}, pace is {persona['pace']}, and emotion level is {persona['emotion']}. "
            f"Your catchphrase is '{persona['catchphrase']}'. "
            f"{persona.get('prompt_modifier', '')} "
            "Structured Output Required:\n"
            "1. Hook (3-5s)\n"
            "2. Story Body\n"
            "3. CTA Outro\n"
        )
        
        # Base User Prompt
        user_prompt = self.prompts['base_rewrite'].format(article_text=article_text)
        
        # Generate
        logger.info(f"Generating script with persona: {persona['name']}")
        script = self.generate(model, user_prompt, system=system_prompt)
        
        return script

if __name__ == "__main__":
    writer = AIWriter()
    sample_text = "Brad Pitt was seen eating a burger in New York yesterday. He looked happy."
    print(writer.rewrite_article(sample_text))
