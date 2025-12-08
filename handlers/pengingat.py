# handlers/pengingat.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

async def show_pengingat_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Memberi info tentang fitur pengingat otomatis."""
    query = update.callback_query
    await query.answer()
    
    message = (
        "⏰ *Info Pengingat Harian*\n\n"
        "Fitur ini aktif secara otomatis untuk semua pengguna.\n\n"
        "Setiap hari jam *21:00 WIB* (9 malam), saya akan mengirimkan "
        "rangkuman jadwal kuliah untuk *besok* dan "
        "tugas yang mendekati deadline (H-3).\n\n"
        "Kamu tidak perlu melakukan pengaturan apa pun."
    )
    
    keyboard = [[InlineKeyboardButton("« Kembali ke Menu Utama", callback_data="menu:main")]]
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )