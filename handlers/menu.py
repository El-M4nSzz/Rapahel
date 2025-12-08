import textwrap
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from utils.json_helper import get_user_data

# Fungsi untuk membuat keyboard menu utama
def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📚 Jadwal Kuliah", callback_data="menu:jadwal")],
        [InlineKeyboardButton("📝 Daftar Tugas", callback_data="menu:tugas")],
        [InlineKeyboardButton("⏰ Info Pengingat", callback_data="menu:pengingat")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk perintah /start."""
    user = update.effective_user
    
    # Inisialisasi data user di data.json jika belum ada
    get_user_data(user.id)
    
    # Fungsi ini sudah benar menggunakan HTML
    await update.message.reply_html(
        f"👋 Halo, {user.mention_html()}!\n\n"
        "Selamat datang di Bot Asisten <b>Raphael!</b> "
        "Saya di sini untuk membantumu mencatat jadwal kuliah dan tugas.\n\n"
        "Gunakan tombol di bawah ini untuk memulai, atau ketik "
        "<b>/help</b> untuk melihat panduan lengkap penggunaan.",
        reply_markup=get_main_menu_keyboard()
    )

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk callback query 'menu:main' (kembali ke menu utama)."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "Kamu kembali ke Menu Utama. Apa yang ingin kamu lakukan?",
        reply_markup=get_main_menu_keyboard()
    )

# --- FUNGSI /help (DIUBAH KE HTML) ---
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menampilkan pesan panduan (manual user)."""
    user = update.effective_user
    
    # Teks ini sekarang menggunakan format HTML (<b>, <code>, <i>)
    # Jauh lebih aman dan tidak akan crash
    text = f"""
    ❓ <b>Panduan Penggunaan Bot</b> ❓

    Halo, {user.first_name}! Ini adalah panduan lengkap untuk menggunakan bot ini.

    <b>Dasar-dasar Navigasi:</b>
    Kamu bisa berinteraksi dengan bot ini melalui dua cara:
    1.  <b>Tombol Inline:</b> Tombol yang muncul di bawah pesan (seperti di menu utama).
    2.  <b>Perintah:</b> Perintah yang diawali / (seperti /start atau /help).

    ---
    <b>Menu Utama (/start):</b>
    Saat kamu mengirim /start, kamu akan melihat 3 tombol utama:

    1.  📚 <b>Jadwal Kuliah</b>
        -   Melihat semua jadwal kuliah yang sudah kamu simpan.
        -   <b>➕ Tambah Jadwal:</b> Memulai proses input jadwal baru. Bot akan menanyakan (1) Hari, (2) Nama Mata Kuliah, dan (3) Jam.
        -   <b>🗑️ Hapus Jadwal:</b> Menampilkan daftar jadwal untuk kamu hapus satu per satu.

    2.  📝 <b>Daftar Tugas</b>
        -   Melihat semua tugas yang tersisa.
        -   <b>➕ Tambah Tugas:</b> Memulai proses input tugas baru. Bot akan menanyakan (1) Nama Tugas dan (2) Deadline (format: <code>YYYY-MM-DD</code>).
        -   <b>🗑️ Hapus Tugas:</b> Menampilkan daftar tugas untuk kamu hapus.

    3.  ⏰ <b>Info Pengingat</b>
        -   Memberi info tentang fitur pengingat otomatis.

    ---
    <b>Membatalkan Aksi:</b>
    Jika kamu sedang dalam proses menambah jadwal atau tugas dan ingin membatalkannya, cukup kirim perintah <b>/batal</b> kapan saja.

    <b>Pengingat Otomatis:</b>
    Setiap hari pada jam <b>21:00 WIB</b> (jam 9 malam), bot akan otomatis mengecek data kamu. Jika kamu punya jadwal kuliah <i>besok</i> atau tugas yang <i>mendekati deadline</i> (H-3), kamu akan mendapat pesan rangkuman.

    <b>Perintah Lain:</b>
    -   <b>/help</b>: Menampilkan pesan panduan ini.
    -   <b>/contact</b>: Menampilkan info kontak jika kamu menemukan bug atau punya saran.
    """
    
    # Kita gunakan textwrap.dedent untuk merapikan teks
    await update.message.reply_text(
        textwrap.dedent(text), 
        parse_mode=ParseMode.HTML  # <-- INI PERUBAHAN UTAMANYA
    )

# --- FUNGSI /contact (DIUBAH KE HTML) ---
async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menampilkan info kontak/feedback."""
    text = (
        "🐞 <b>Punya Kritik, Saran, atau Laporan Bug?</b>\n\n"
        "Bot ini masih dalam tahap pengembangan. Jika kamu menemukan masalah "
        "atau punya ide fitur keren, jangan ragu untuk menghubungi developernya!\n\n"
        "Silakan kirim pesan langsung ke: <b>@Refasttt</b>"
    )
    # Kita juga ubah ini ke HTML agar konsisten
    await update.message.reply_text(
        text, 
        parse_mode=ParseMode.HTML  # <-- INI PERUBAHAN UTAMANYA
    )