# utils/json_helper.py
import json
import threading
import os

DATA_FILE = 'data.json'
# Lock untuk mencegah race condition (data rusak) saat banyak user akses bersamaan
_lock = threading.Lock()

def load_data() -> dict:
    """Membaca data dari file JSON dengan aman."""
    with _lock:
        if not os.path.exists(DATA_FILE):
            return {}
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

def save_data(data: dict) -> None:
    """Menyimpan data ke file JSON dengan aman."""
    with _lock:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def get_user_data(user_id: int) -> dict:
    """Mendapatkan data spesifik user, atau membuat entri baru jika belum ada."""
    all_data = load_data()
    user_id_str = str(user_id)
    
    if user_id_str not in all_data:
        # Template data untuk user baru
        all_data[user_id_str] = {
            "jadwal": [],
            "tugas": []
        }
        save_data(all_data)
        
    return all_data[user_id_str]

def update_user_data(user_id: int, user_data: dict) -> None:
    """Mengupdate data untuk user spesifik."""
    all_data = load_data()
    all_data[str(user_id)] = user_data
    save_data(all_data)