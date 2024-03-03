import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv("DEBUG")
DEBUG = True if DEBUG.lower() == "true" else False

SECRET_KEY = os.getenv("SECRET_KEY", "")
