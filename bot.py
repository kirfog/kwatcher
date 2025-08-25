import io
import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from handle_voice import rec_voice

load_dotenv()

TOKEN = os.environ["BOT_TOKEN"]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"An utterance from {user.username} received. Processing..."
    )

    if update.message.voice:
        file_id = update.message.voice.file_id
    elif update.message.audio:
        file_id = update.message.audio.file_id
    elif update.message.video_note:
        file_id = update.message.video_note.file_id
    elif update.message.video:
        file_id = update.message.video.file_id

    file = await context.bot.get_file(file_id)
    audio_stream = io.BytesIO()
    await file.download_to_memory(audio_stream)
    result_text = rec_voice(audio_stream)
    await update.message.reply_text(result_text, parse_mode="HTML")


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    try:
        app.initialize()
        app.add_handler(
            MessageHandler(
                filters.VOICE | filters.AUDIO | filters.VIDEO_NOTE | filters.VIDEO,
                handle_voice,
            )
        )
        app.run_polling()
    finally:
        app.shutdown()
