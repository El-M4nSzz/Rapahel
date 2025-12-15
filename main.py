# main.py
import logging
import datetime
import pytz
import config

from telegram import Update 
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Impor handlers
from handlers import menu, jadwal, tugas, pengingat

# Impor states
from handlers.jadwal import (
    JADWAL_HARI, JADWAL_MATKUL, JADWAL_JAM
)
from handlers.tugas import (
    TUGAS_NAMA, TUGAS_DEADLINE
)

# Impor job pengingat
from utils.reminder import check_reminders

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Membatalkan ConversationHandler yang sedang berjalan."""
    await update.message.reply_text(
        "Proses dibatalkan.",
        reply_markup=menu.get_main_menu_keyboard()
    )
    # Bersihkan user_data sementara
    context.user_data.pop('new_jadwal', None)
    context.user_data.pop('new_tugas', None)
    return ConversationHandler.END

def main() -> None:
    """Jalankan bot."""
    
    application = (
        Application.builder()
        .token(config.TOKEN)
        .build()
    )

    # Ambil job_queue bawaan dari application
    job_queue = application.job_queue

    # Atur Job Queue untuk Pengingat Harian
    WIB = pytz.timezone('Asia/Jakarta')
    
    # Pastikan jam server sesuai
    reminder_time = datetime.time(hour=21, minute=5, second=0, tzinfo=WIB)
    
    job_queue.run_daily(check_reminders, time=reminder_time, name="daily_reminder")
    logger.info(f"Job 'daily_reminder' diatur untuk berjalan setiap hari jam 21:00 WIB.")

    # Definisikan Conversation Handlers
    
    # Conversation Handler untuk Tambah Jadwal
    conv_handler_jadwal = ConversationHandler(
        entry_points=[CallbackQueryHandler(jadwal.add_jadwal_start, pattern="^jadwal:add_start$")],
        states={
            JADWAL_HARI: [MessageHandler(filters.TEXT & ~filters.COMMAND, jadwal.add_jadwal_hari)],
            JADWAL_MATKUL: [MessageHandler(filters.TEXT & ~filters.COMMAND, jadwal.add_jadwal_matkul)],
            JADWAL_JAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, jadwal.add_jadwal_jam)],
        },
        fallbacks=[CommandHandler("batal", cancel)],
    )

    # Conversation Handler untuk Tambah Tugas
    conv_handler_tugas = ConversationHandler(
        entry_points=[CallbackQueryHandler(tugas.add_tugas_start, pattern="^tugas:add_start$")],
        states={
            TUGAS_NAMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, tugas.add_tugas_nama)],
            TUGAS_DEADLINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, tugas.add_tugas_deadline)],
        },
        fallbacks=[CommandHandler("batal", cancel)],
    )

    # = Semua Handlers =
    
    # Perintah
    application.add_handler(CommandHandler("start", menu.start))
    application.add_handler(CommandHandler("help", menu.help_command))
    application.add_handler(CommandHandler("contact", menu.contact_command))
    
    # Menu Utama (CallbackQuery)
    application.add_handler(CallbackQueryHandler(menu.main_menu, pattern="^menu:main$"))
    application.add_handler(CallbackQueryHandler(jadwal.show_jadwal_menu, pattern="^menu:jadwal$"))
    application.add_handler(CallbackQueryHandler(tugas.show_tugas_menu, pattern="^menu:tugas$"))
    application.add_handler(CallbackQueryHandler(pengingat.show_pengingat_menu, pattern="^menu:pengingat$"))
    
    # Tambah Data (Conversations)
    application.add_handler(conv_handler_jadwal)
    application.add_handler(conv_handler_tugas)
    
    # Hapus Data (CallbackQuery)
    application.add_handler(CallbackQueryHandler(jadwal.show_delete_jadwal_menu, pattern="^jadwal:delete_menu$"))
    application.add_handler(CallbackQueryHandler(jadwal.delete_jadwal_item, pattern="^jadwal:delete_confirm:"))
    
    application.add_handler(CallbackQueryHandler(tugas.show_delete_tugas_menu, pattern="^tugas:delete_menu$"))
    application.add_handler(CallbackQueryHandler(tugas.delete_tugas_item, pattern="^tugas:delete_confirm:"))
    
    # Jalankan bot
    logger.info("Bot mulai berjalan...")
    application.run_polling()

if __name__ == "__main__":
    main()
