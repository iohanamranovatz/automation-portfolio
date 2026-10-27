import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv() #reads from an .env file and injects those key/value pairs 

@dataclass(frozen=True) #makes the class immutable
class Settings:
    web_url: str = os.getenv("WEB_URL", "https://www.saucedemo.com")
    web_user: str = os.getenv("WEB_USER", "standard_user")
    web_password: str = os.getenv("WEB_PASSWORD", "")
    api_url: str = os.getenv("API_URL", "http://localhost:3001")
    api_user: str = os.getenv("API_USER", "")
    api_password: str = os.getenv("API_PASSWORD", "")
    headless: bool = os.getenv("HEADLESS", "true").lower() == "true" #headless browser in CI

settings = Settings()