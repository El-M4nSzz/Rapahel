import os
from dotenv import load_dotenv

# Load environment variables dari file .env (untuk di laptop)
load_dotenv()

# Ambil token dari environment variable
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("Token tidak ditemukan! Pastikan file .env ada atau Environment Variable di set.")
