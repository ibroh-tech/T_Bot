import os
import sqlite3
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext, ContextTypes,
)

# Replace with your Telegram bot API token
BOT_API_TOKEN = ""  # Replace with your bot's API token

# Replace with the group chat ID where experts will see customer queries
EXPERT_GROUP_CHAT_ID = -4806778713  # Replace with your group chat ID

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO  # Use DEBUG for more detailed logs
)
logger = logging.getLogger(__name__)

# Dictionaries to track states
customer_to_expert = {}
expert_to_user = {}  # Maps expert group message ID to user ID
feedback_states = {}


# Initialize the SQLite database
def initialize_database():
    connection = sqlite3.connect("feedback.db")  # Creates the database file if it doesn't exist
    cursor = connection.cursor()
    # Create the feedback table
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS feedback2 (
                                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                            user_id INTEGER NOT NULL,
                                                            feedback TEXT NOT NULL,
                                                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                   )
                   """)
    connection.commit()
    connection.close()




# Save feedback to the database
def save_feedback(user_id, feedback_text):
    try:
        connection = sqlite3.connect("feedback.db")
        cursor = connection.cursor()
        cursor.execute("""
                       INSERT INTO feedback2 (user_id, feedback)
                       VALUES (?, ?)
                       """, (user_id, feedback_text))
        connection.commit()
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
    finally:
        connection.close()


# Main menu keyboard
def main_menu_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("Qo'llanmalar")],
        [KeyboardButton("Bank bilan bog'lanish")],
        [KeyboardButton("Fikr-mulohaza qoldirish")]
    ], resize_keyboard=True, one_time_keyboard=True)


# Start command
async def start(update: Update, context: CallbackContext):
    logger.info(f"User {update.message.chat_id} started the bot.")
    await update.message.reply_text(
        "Xush kelibsiz! Sizga qanday yordam bera olishim mumkin?",
        reply_markup=main_menu_keyboard()
    )


# Handle user messages
user_states = {}  # A dictionary to manage states for all users

# Define user states
STATE_NONE = "none"
STATE_PROBLEM = "problem"
STATE_FEEDBACK = "feedback"

expert_to_user = {}
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_message = update.message.text
    except AttributeError:
        logging.warning("Error: Message is not a text message")
        return
    user_id = update.message.chat_id
    logging.warning('Handled')
    if user_message == "Qo'llanmalar":
        await update.message.reply_text(
            "Bu bo'limda Siz tashqi iqtisodiy foaliyatingiz doirasida bank tomonidan ko'rsatiladigan xizmatlardan foydalanish bo'yicha qo'llanmalar bilan tanishib chiqishingiz mumkin",
            reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton("1. Internet banking tizimida SWIFT to'lovlari")],
                [KeyboardButton("2. Konvertatsiya amaliyoti")],
                [KeyboardButton("3. Faktoring amaliyoti")],
                [KeyboardButton("Orqaga")]
            ], resize_keyboard=True)
        )
        return
    elif user_message == "1. Internet banking tizimida SWIFT to'lovlari":
        file_path = "C:\\Users\\ibroh\\OneDrive\\Desktop\\example.docx"
        try:
            with open(file_path, "rb") as file:
                await context.bot.send_document(chat_id=user_id, document=file)
            await update.message.reply_text(
                "Hujjat muvaffaqiyatli yuborildi!",
                reply_markup=ReplyKeyboardMarkup([["Orqaga"], ["Bosh sahifa"]], resize_keyboard=True),
            )
            return
        except FileNotFoundError:
            await update.message.reply_text("Kechirasiz, fayl topilmadi.")
            logger.error(f"File not found: {file_path}")
        except Exception as e:
            await update.message.reply_text(f"Xatolik yuz berdi: {e}")
            logger.error(f"Error opening file: {e}")

    elif user_message == "2. Konvertatsiya amaliyoti":
        await update.message.reply_text(
            "Kredit olish uchun ariza to'ldiring va kerakli hujjatlarni taqdim eting.",
            reply_markup=ReplyKeyboardMarkup([["Orqaga"], ["Bosh sahifa"]], resize_keyboard=True)
        )
        file_path = "C:\\Users\\ibroh\\OneDrive\\Desktop\\example2.docx"
        with open(file_path, "rb") as file:
            await context.bot.send_document(chat_id=user_id, document=file)
            return

    elif user_message == "3. Faktoring amaliyoti":
        await update.message.reply_text(
            "To'lov xabarnomasini kiritish va jo'natish shartnomasi uchun qo'llanma.",
            reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton("Orqaga")],
                [KeyboardButton("Bosh sahifa")]
            ], resize_keyboard=True)
        )
        file_path = "C:\\Users\\ibroh\\OneDrive\\Desktop\\example3.docx"  # Replace with the correct file path
        with open(file_path, "rb") as file:
            await context.bot.send_document(chat_id=user_id, document=file)
            return


    if user_message == "Bank bilan bog'lanish":
        user_states[user_id] = STATE_PROBLEM
        await update.message.reply_text(
            "Iltimos, muammo yoki savolingizni yozib qoldiring. Biz uni mutaxassislarga yuboramiz.",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("1. Chat")],
                 [KeyboardButton("2. Aloqaga chiqish")],
                 [KeyboardButton("Orqaga")]], resize_keyboard=True)
        )
        return




    elif user_message == "1. Chat":
        user_states[user_id] = STATE_PROBLEM
        await update.message.reply_text(
            "Iltimos, muammo yoki savolingizni yozib qoldiring. Biz uni mutaxassislarga yuboramiz.",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Orqaga")]], resize_keyboard=True)
        )
        return




    elif user_message == "2. Aloqaga chiqish":
        await update.message.reply_text(
            "Operator bilan bog'lanish uchun +998123456789 raqamiga qo'ng'iroq qiling yoki onlayn chatga yozing.",
            reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton("Orqaga")],
                #[KeyboardButton("Bosh sahifa")]
            ], resize_keyboard=True)
        )
        return

    elif user_message == "Orqaga":
        # Reset the state and avoid processing further as a problem
        user_states[user_id] = STATE_NONE
        await update.message.reply_text(
            "Jarayon bekor qilindi.", reply_markup=main_menu_keyboard()
        )
        return

    elif user_message == "Fikr-mulohaza qoldirish":
        user_states[user_id] = STATE_FEEDBACK
        await update.message.reply_text(
            "Bank xizmatlari to'g'risida o'z fikr-mulohazalaringizni qoldiring. Xizmatlarimiz Siz uchun yanada qulay, tez va sodda bo'lishida o'z hissangizni qo'shing",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Orqaga")]], resize_keyboard=True)
        )



    elif user_states.get(user_id) == STATE_PROBLEM:
        try:
            if update.message.text:
            # Forward the user's text problem to the expert group
                forwarded_message = await context.bot.send_message(
                    chat_id=EXPERT_GROUP_CHAT_ID,
                    text=f"📢 Yangi muammo (User {user_id}): {update.message.text}",
                )
            # Update the mapping of forwarded message to the original user
                expert_to_user[forwarded_message.message_id] = user_id
                await update.message.reply_text(
                    "Muammo mutaxassislarga yuborildi. Tez orada javob beramiz.",
                    reply_markup=main_menu_keyboard(),
                )

            elif update.message.photo:
                # Forward the user's photo problem to the expert group
                photo = update.message.photo[-1]  # Get the highest resolution photo
                forwarded_message = await context.bot.send_photo(
                    chat_id=EXPERT_GROUP_CHAT_ID,
                    photo=photo.file_id,
                    caption=f"📢 Yangi surat (User {user_id}):",
                )
            # Update the mapping
                expert_to_user[forwarded_message.message_id] = user_id
                await update.message.reply_text(
                    "Surat mutaxassislarga yuborildi. Tez orada javob beramiz.",
                    reply_markup=main_menu_keyboard(),
                )

            elif update.message.video:
                # Forward the user's video problem to the expert group
                video = update.message.video
                forwarded_message = await context.bot.send_video(
                    chat_id=EXPERT_GROUP_CHAT_ID,
                    video=video.file_id,
                    caption=f"📢 Yangi video (User {user_id}):",
                )
            # Update the mapping
                expert_to_user[forwarded_message.message_id] = user_id
                await update.message.reply_text(
                    "Video mutaxassislarga yuborildi. Tez orada javob beramiz.",
                    reply_markup=main_menu_keyboard(),
                )

            elif update.message.document:
                # Forward the user's document to the expert group
                document = update.message.document
                forwarded_message = await context.bot.send_document(
                    chat_id=EXPERT_GROUP_CHAT_ID,
                    document=document.file_id,
                    caption=f"📢 Yangi hujjat (User {user_id}):",
                )
            # Update the mapping
                expert_to_user[forwarded_message.message_id] = user_id
                await update.message.reply_text(
                    "Hujjat mutaxassislarga yuborildi. Tez orada javob beramiz.",
                    reply_markup=main_menu_keyboard(),
                )

            else:
                # Handle unsupported message types
                await update.message.reply_text(
                    "Kechirasiz, ushbu turdagi fayllar qabul qilinmaydi.",
                    reply_markup=main_menu_keyboard(),
                )

        except Exception as e:
            logger.error(f"Error forwarding message to experts: {e}")
            await update.message.reply_text(
                "Kechirasiz, xabarni yuborishda xatolik yuz berdi.",
                reply_markup=main_menu_keyboard(),
            )


        #user_states[user_id] = STATE_NONE

    elif user_states.get(user_id) == STATE_FEEDBACK:
        save_feedback(user_id, user_message)
        await update.message.reply_text(
            "Rahmat! Fikr-mulohazangiz saqlandi.",
            reply_markup=main_menu_keyboard(),
        )
        user_states[user_id] = STATE_NONE

    else:
        await update.message.reply_text(
            "Kechirasiz, so'rovingizni tushunmadim.", reply_markup=main_menu_keyboard()
        )



# Handle expert replies
async def handle_expert_reply(update: Update, context: CallbackContext):
    # Ensure it's coming from the expert group
    if update.message.chat_id == EXPERT_GROUP_CHAT_ID:
        replied_message = update.message.reply_to_message
        if replied_message:
            # Fetch the original user ID using the mapping
            original_user_id = expert_to_user.get(replied_message.message_id)
            if original_user_id:
                try:
                    # Forward the expert's reply to the original user
                    await context.bot.send_message(
                        chat_id=original_user_id,
                        text=f"Mutaxassisdan javob: {update.message.text}"
                    )
                except Exception as e:
                    logger.error(f"Error forwarding expert reply to user: {e}")
            else:
                logger.warning("No user mapping found for expert reply.")
        else:
            logger.warning("Expert reply is not a reply to a forwarded message.")




async def forward_media_to_experts(user_id, file_id, media_type, update, context):
    try:
        if media_type == "photo":
            await context.bot.send_photo(
                chat_id=EXPERT_GROUP_CHAT_ID,
                photo=file_id,
                caption=f"📢 Yangi surat (User {user_id}):",
            )
        elif media_type == "video":
            await context.bot.send_video(
                chat_id=EXPERT_GROUP_CHAT_ID,
                video=file_id,
                caption=f"📢 Yangi video (User {user_id}):",
            )
        elif media_type == "document":
            await context.bot.send_document(
                chat_id=EXPERT_GROUP_CHAT_ID,
                document=file_id,
                caption=f"📢 Yangi hujjat (User {user_id}):",
            )
        else:
            await update.message.reply_text(
                "Kechirasiz, ushbu turdagi fayllarni jo'nata olmaymiz."
            )
        # Confirm to the user
        await update.message.reply_text("Fayl mutaxassislarga yuborildi.", reply_markup=main_menu_keyboard())
    except Exception as e:
        logger.error(f"Error forwarding {media_type} to experts: {e}")
        await update.message.reply_text(
            "Kechirasiz, faylni yuborishda xatolik yuz berdi.", reply_markup=main_menu_keyboard()
        )




# Add this function to get the group chat ID
# Function to get group ID
async def get_group_id(update: Update, context: CallbackContext):
    chat = update.effective_chat
    await update.message.reply_text(f"Group ID: {chat.id}\nGroup Title: {chat.title}")


def get_feedbacks():
    connection = sqlite3.connect("feedback.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM feedback")  # Ensure table name is correct
    rows = cursor.fetchall()
    connection.close()
    return rows


# async def get_feedbacks_command(update: Update, context: CallbackContext):
#     # Check if the user is an admin (optional)
#     admin_ids = [5005475085]  # replace with your admin Telegram user IDs
#     if update.effective_user.id not in admin_ids:
#         await update.message.reply_text("Sizda bu buyruqni ishlatish uchun ruxsat yo'q.")
#         return
#
#     await send_feedbacks_to_group(context)
#     await update.message.reply_text("Fikr-mulohazalar admin guruhiga yuborildi.")
#
# # Add handler somewhere in your setup
# dispatcher.add_handler(CommandHandler("get_feedbacks", get_feedbacks_command))


def main():
    initialize_database()
    application = Application.builder().token(BOT_API_TOKEN).build()

    # Add handlers for commands and messages
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("getid", get_group_id))  # Add the handler here
    # application.add_handler(MessageHandler(filters.TEXT &  filters.ChatType.PRIVATE, handle_user_message))
    application.add_handler(MessageHandler(filters.ALL   &  filters.ChatType.PRIVATE, handle_user_message))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUP, handle_expert_reply))


    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()


