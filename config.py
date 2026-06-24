import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    OPENROUTER_MODEL = 'google/gemma-4-31b-it:free'
    TEMPERATURE=0.7
    DRAFTS_DIR='data/drafts'
    PUBLISHED_DIR='data/published'
    IDEAS_FILE='data/ideas.json'

    @classmethod
    def init_dirs(cls):
        for path in [cls.DRAFTS_DIR, cls.PUBLISHED_DIR]:
            os.makedirs(path, exist_ok=True)
    
config=Config()
config.init_dirs()
