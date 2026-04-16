import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

    @staticmethod
    def validate():
        missing = []
        if not Config.GROQ_API_KEY:
            missing.append("GROQ_API_KEY")
        if not Config.UNSPLASH_ACCESS_KEY:
            missing.append("UNSPLASH_ACCESS_KEY")

        if missing:
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")