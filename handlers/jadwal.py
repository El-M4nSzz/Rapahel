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
JADWAL_HARI, JADWAL_MATKUL, JADWAL_JAM = range(3)

# --- Tombol Kembali ---
def get_back_button(menu: str = "jadwal") -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton("« Kembali", callback_data=f"menu:{menu}")]]
    return InlineKeyboardMarkup(keyboard)

def get_back_to_main_menu_button() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton("« Kembali ke Menu Utama", callback_data="menu:main")]]
    return InlineKeyboardMarkup(keyboard)


# --- Logika Menampilkan Jadwal ---
def format_jadwal_message(user_data: dict) -> str:
    """Menyusun pesan daftar jadwal dari data user."""
    jadwal = user_data.get('jadwal', [])
    if not jadwal:
        return "Kamu belum memiliki jadwal kuliah yang tersimpan."
    
    # Sortir berdasarkan hari
    hari_order = ['senin', 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu', 'minggu']
    jadwal_sorted = sorted(jadwal, key=lambda x: (
        hari_order.index(x.get('hari', '').lower()) if x.get('hari', '').lower() in hari_order else 99,
        x.get('jam', '')
    ))
    
    message = "📚 *Jadwal Kuliah Kamu:*\n\n"
    current_day = ""
    for item in jadwal_sorted:
        hari = item.get('hari', 'N/A').capitalize()
        if hari != current_day:
            message += f"\n*{hari}*\n"
            current_day = hari
        message += f"  • {item.get('mata_kuliah', 'N/A')} (Jam {item.get('jam', 'N/A')})\n"
    return message

async def show_jadwal_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menampilkan menu utama Jadwal Kuliah."""
    query = update.callback_query
    await query.answer()
    
    user_data = json_helper.get_user_data(query.from_user.id)
    message = format_jadwal_message(user_data)
    
    keyboard = [
        [
            InlineKeyboardButton("➕ Tambah Jadwal", callback_data="jadwal:add_start"),
            InlineKeyboardButton("🗑️ Hapus Jadwal", callback_data="jadwal:delete_menu")
        ],
        [InlineKeyboardButton("« Kembali ke Menu Utama", callback_data="menu:main")]
    ]
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# --- Logika Menambah Jadwal (ConversationHandler) ---

async def add_jadwal_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Memulai proses penambahan jadwal baru."""
    query = update.callback_query
    await query.answer()
    context.user_data['new_jadwal'] = {} # Reset
    await query.edit_message_text(
        text="Oke, mari tambahkan jadwal baru.\n\n"
             "Ketik nama *Hari* (Contoh: Senin, Selasa, ...)\n\n"
             "Ketik /batal untuk membatalkan.",
        parse_mode="Markdown"
    )
    return JADWAL_HARI

async def add_jadwal_hari(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Menerima input Hari dan meminta Mata Kuliah."""
    hari = update.message.text
    context.user_data['new_jadwal']['hari'] = hari.capitalize()
    
    await update.message.reply_text(
        f"Hari: {hari}\n\n"
        "Sekarang masukkan *Nama Mata Kuliah* (Contoh: Rekayasa Perangkat Lunak)\n\n"
        "Ketik /batal untuk membatalkan.",
        parse_mode="Markdown"
    )
    return JADWAL_MATKUL

async def add_jadwal_matkul(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Menerima input Mata Kuliah dan meminta Jam."""
    matkul = update.message.text
    context.user_data['new_jadwal']['mata_kuliah'] = matkul
    
    await update.message.reply_text(
        f"Mata Kuliah: {matkul}\n\n"
        "Terakhir, masukkan *Jam Mulai* (Contoh: 08:00)\n\n"
        "Ketik /batal untuk membatalkan.",
        parse_mode="Markdown"
    )
    return JADWAL_JAM

async def add_jadwal_jam(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Menerima input Jam, menyimpan, dan mengakhiri percakapan."""
    jam = update.message.text
    context.user_data['new_jadwal']['jam'] = jam
    
    user_id = update.effective_user.id
    user_data = json_helper.get_user_data(user_id)
    
    # Simpan data baru
    user_data['jadwal'].append(context.user_data['new_jadwal'])
    json_helper.update_user_data(user_id, user_data)
    
    # --- PERUBAHAN DI SINI ---
    # Kita tidak bisa memanggil show_jadwal_menu, karena itu untuk CallbackQuery
    # Kita kirim pesan baru sebagai balasan
    await update.message.reply_text(
        f"✅ *Jadwal berhasil disimpan:*\n"
        f"Hari: {context.user_data['new_jadwal']['hari']}\n"
        f"Matkul: {context.user_data['new_jadwal']['mata_kuliah']}\n"
        f"Jam: {context.user_data['new_jadwal']['jam']}\n\n"
        "Kamu kembali ke Menu Utama.",
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard() # Kirim keyboard menu utama
    )
    # -------------------------
    
    context.user_data.pop('new_jadwal', None) # Bersihkan context
    return ConversationHandler.END

# --- Logika Menghapus Jadwal (Ini sudah benar, tidak ada perubahan) ---

async def show_delete_jadwal_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menampilkan daftar jadwal yang bisa dihapus."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data = json_helper.get_user_data(user_id)
    jadwal = user_data.get('jadwal', [])
    
    if not jadwal:
        await query.edit_message_text(
            text="Tidak ada jadwal untuk dihapus.",
            reply_markup=get_back_button("jadwal")
        )
        return

    keyboard = []
    # Buat tombol untuk setiap item jadwal
    # Index dipakai agar unik
    for i, item in enumerate(jadwal):
        text = f"Hapus: {item['hari']} - {item['mata_kuliah']} ({item['jam']})"
        callback = f"jadwal:delete_confirm:{i}"
        keyboard.append([InlineKeyboardButton(text, callback_data=callback)])
    
    keyboard.append([InlineKeyboardButton("« Kembali", callback_data="menu:jadwal")])
    
    await query.edit_message_text(
        text="Pilih jadwal yang ingin kamu hapus:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def delete_jadwal_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menghapus item jadwal berdasarkan index."""
    query = update.callback_query
    await query.answer()
    
    try:
        # Ambil index dari callback data "jadwal:delete_confirm:INDEX"
        index_to_delete = int(query.data.split(':')[-1])
        
        user_id = query.from_user.id
        user_data = json_helper.get_user_data(user_id)
        
        if 0 <= index_to_delete < len(user_data['jadwal']):
            deleted_item = user_data['jadwal'].pop(index_to_delete)
            json_helper.update_user_data(user_id, user_data)
            
            await query.edit_message_text(
                text=f"✅ Jadwal '{deleted_item['mata_kuliah']}' berhasil dihapus."
            )
        else:
            await query.edit_message_text(text="Gagal menghapus. Jadwal tidak ditemukan.")
            
    except (ValueError, IndexError):
        await query.edit_message_text(text="Terjadi error saat menghapus.")

    # Tampilkan kembali menu delete (refresh)
    # Ini Boleh, karena delete_jadwal_item dipanggil oleh CallbackQuery
    await show_delete_jadwal_menu(update, context)