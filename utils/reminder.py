# utils/reminder.py
import datetime
import pytz
from telegram import Bot
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from . import json_helper

# Peta untuk konversi nama hari (Inggris ke Indonesia)
DAY_MAP = {
    'Monday': 'Senin',
    'Tuesday': 'Selasa',
    'Wednesday': 'Rabu',
    'Thursday': 'Kamis',
    'Friday': 'Jumat',
    'Saturday': 'Sabtu',
    'Sunday': 'Minggu'
}

async def check_reminders(context: ContextTypes.DEFAULT_TYPE):
    """Fungsi yang dijalankan oleh Job Queue setiap jam 21:00 WIB."""
    bot: Bot = context.bot
    all_data = json_helper.load_data()
    
    # Tentukan zona waktu dan waktu saat ini
    WIB = pytz.timezone('Asia/Jakarta')
    now = datetime.datetime.now(WIB)
    tomorrow = now + datetime.timedelta(days=1)
    tomorrow_day_name_en = tomorrow.strftime('%A')
    tomorrow_day_name_id = DAY_MAP.get(tomorrow_day_name_en, "").lower()
    
    print(f"[{now.isoformat()}] Menjalankan Pengecekan Pengingat Harian...")

    for user_id_str, user_data in all_data.items():
        message_parts = []
        
        # 1. Cek Jadwal Kuliah Besok
        jadwal_besok = [
            j for j in user_data.get('jadwal', []) 
            if j.get('hari', '').lower() == tomorrow_day_name_id
        ]
        
        if jadwal_besok:
            message_parts.append("📚 *Jadwal Kuliah Besok:*")
            for j in sorted(jadwal_besok, key=lambda x: x.get('jam', '')):
                message_parts.append(f"  • {j.get('mata_kuliah', 'N/A')} (Jam {j.get('jam', 'N/A')})")
        
        # 2. Cek Tugas Mendekati Deadline (H-3)
        tugas_deadline = []
        today_date = now.date()
        
        for t in user_data.get('tugas', []):
            try:
                deadline = datetime.date.fromisoformat(t.get('deadline', ''))
                days_left = (deadline - today_date).days
                
                # Kirim pengingat jika deadline 0 (hari ini), 1, 2, atau 3 hari lagi
                if 0 <= days_left <= 3:
                    tugas_deadline.append((t.get('nama', 'N/A'), days_left))
            except (ValueError, TypeError):
                continue # Skip jika format deadline salah
        
        if tugas_deadline:
            message_parts.append("\n📝 *Tugas Mendekati Deadline:*")
            for nama, sisa in sorted(tugas_deadline, key=lambda x: x[1]):
                if sisa == 0:
                    hari_str = "*HARI INI (DEADLINE!)*"
                elif sisa == 1:
                    hari_str = "*BESOK*"
                else:
                    hari_str = f"{sisa} hari lagi"
                message_parts.append(f"  • {nama} ({hari_str})")
        
        # 3. Kirim Pesan jika ada yang perlu diingatkan
        if message_parts:
            final_message = "🔔 *Pengingat Harian*\n\n" + "\n".join(message_parts)
            try:
                await bot.send_message(
                    chat_id=int(user_id_str), 
                    text=final_message,
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                print(f"Gagal mengirim pengingat ke {user_id_str}: {e}")