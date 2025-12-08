import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, 
    ConversationHandler, 
    CallbackQueryHandler, 
    MessageHandler,
    filters
)
from utils import json_helper
from handlers.menu import get_main_menu_keyboard  # <--- TAMBAHKAN IMPORT INI

# Definisikan state untuk ConversationHandler
TUGAS_NAMA, TUGAS_DEADLINE = range(3, 5) # Lanjutkan range dari jadwal.py

# --- Tombol Kembali ---
def get_back_button(menu: str = "tugas") -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton("« Kembali", callback_data=f"menu:{menu}")]]
    return InlineKeyboardMarkup(keyboard)

# --- Logika Menampilkan Tugas ---
def format_tugas_message(user_data: dict) -> str:
    """Menyusun pesan daftar tugas dari data user."""
    tugas = user_data.get('tugas', [])
    if not tugas:
        return "Hore! Kamu tidak memiliki tugas yang tersimpan."
    
    # Sortir berdasarkan deadline
    tugas_sorted = sorted(tugas, key=lambda x: x.get('deadline', '9999-12-31'))
    
    message = "📝 *Daftar Tugas Kamu:*\n\n"
    today = datetime.date.today()
    
    for item in tugas_sorted:
        deadline_str = item.get('deadline', 'N/A')
        nama = item.get('nama', 'N/A')
        try:
            deadline_date = datetime.date.fromisoformat(deadline_str)
            days_left = (deadline_date - today).days
            if days_left < 0:
                info = "(Sudah Lewat)"
            elif days_left == 0:
                info = "*(DEADLINE HARI INI)*"
            elif days_left == 1:
                info = "*(Besok)*"
            else:
                info = f"({days_left} hari lagi)"
            
            message += f"  • {nama} (Deadline: {deadline_str}) {info}\n"
        except ValueError:
            message += f"  • {nama} (Deadline: {deadline_str})\n"
            
    return message

async def show_tugas_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menampilkan menu utama Tugas."""
    query = update.callback_query
    await query.answer()
    
    user_data = json_helper.get_user_data(query.from_user.id)
    message = format_tugas_message(user_data)
    
    keyboard = [
        [
            InlineKeyboardButton("➕ Tambah Tugas", callback_data="tugas:add_start"),
            InlineKeyboardButton("🗑️ Hapus Tugas", callback_data="tugas:delete_menu")
        ],
        [InlineKeyboardButton("« Kembali ke Menu Utama", callback_data="menu:main")]
    ]
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# --- Logika Menambah Tugas (ConversationHandler) ---

async def add_tugas_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Memulai proses penambahan tugas baru."""
    query = update.callback_query
    await query.answer()
    context.user_data['new_tugas'] = {} # Reset
    await query.edit_message_text(
        text="Oke, mari tambahkan tugas baru.\n\n"
             "Ketik *Nama Tugas* (Contoh: Makalah RPL Bab 1)\n\n"
             "Ketik /batal untuk membatalkan.",
        parse_mode="Markdown"
    )
    return TUGAS_NAMA

async def add_tugas_nama(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Menerima input Nama Tugas dan meminta Deadline."""
    nama = update.message.text
    context.user_data['new_tugas']['nama'] = nama
    
    await update.message.reply_text(
        f"Nama Tugas: {nama}\n\n"
        "Sekarang masukkan *Deadline* dalam format *YYYY-MM-DD* (Contoh: 2025-11-20)\n\n"
        "Ketik /batal untuk membatalkan.",
        parse_mode="Markdown"
    )
    return TUGAS_DEADLINE

async def add_tugas_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Menerima input Deadline, validasi, menyimpan, dan mengakhiri percakapan."""
    deadline_str = update.message.text
    
    # Validasi format deadline
    try:
        datetime.date.fromisoformat(deadline_str)
    except ValueError:
        await update.message.reply_text(
            "Format deadline salah. Harap gunakan *YYYY-MM-DD*.\n"
            "Silakan masukkan lagi.\n\n"
            "Ketik /batal untuk membatalkan.",
            parse_mode="Markdown"
        )
        return TUGAS_DEADLINE # Tetap di state ini
    
    context.user_data['new_tugas']['deadline'] = deadline_str
    
    user_id = update.effective_user.id
    user_data = json_helper.get_user_data(user_id)
    
    # Simpan data baru
    user_data['tugas'].append(context.user_data['new_tugas'])
    json_helper.update_user_data(user_id, user_data)
    
    # --- PERUBAHAN DI SINI ---
    await update.message.reply_text(
        f"✅ *Tugas berhasil disimpan:*\n"
        f"Nama: {context.user_data['new_tugas']['nama']}\n"
        f"Deadline: {context.user_data['new_tugas']['deadline']}\n\n"
        "Kamu kembali ke Menu Utama.",
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard() # Kirim keyboard menu utama
    )
    # -------------------------
    
    context.user_data.pop('new_tugas', None) # Bersihkan context
    return ConversationHandler.END

# --- Logika Menghapus Tugas (Ini sudah benar, tidak ada perubahan) ---

async def show_delete_tugas_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menampilkan daftar tugas yang bisa dihapus."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data = json_helper.get_user_data(user_id)
    tugas = user_data.get('tugas', [])
    
    if not tugas:
        await query.edit_message_text(
            text="Tidak ada tugas untuk dihapus.",
            reply_markup=get_back_button("tugas")
        )
        return

    keyboard = []
    # Buat tombol untuk setiap item tugas
    for i, item in enumerate(tugas):
        text = f"Hapus: {item['nama']} (DL: {item['deadline']})"
        callback = f"tugas:delete_confirm:{i}"
        keyboard.append([InlineKeyboardButton(text, callback_data=callback)])
    
    keyboard.append([InlineKeyboardButton("« Kembali", callback_data="menu:tugas")])
    
    await query.edit_message_text(
        text="Pilih tugas yang ingin kamu hapus:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def delete_tugas_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menghapus item tugas berdasarkan index."""
    query = update.callback_query
    await query.answer()
    
    try:
        # Ambil index dari callback data "tugas:delete_confirm:INDEX"
        index_to_delete = int(query.data.split(':')[-1])
        
        user_id = query.from_user.id
        user_data = json_helper.get_user_data(user_id)
        
        if 0 <= index_to_delete < len(user_data['tugas']):
            deleted_item = user_data['tugas'].pop(index_to_delete)
            json_helper.update_user_data(user_id, user_data)
            
            await query.edit_message_text(
                text=f"✅ Tugas '{deleted_item['nama']}' berhasil dihapus."
            )
        else:
            await query.edit_message_text(text="Gagal menghapus. Tugas tidak ditemukan.")
            
    except (ValueError, IndexError):
        await query.edit_message_text(text="Terjadi error saat menghapus.")

    # Tampilkan kembali menu delete (refresh)
    await show_delete_tugas_menu(update, context)