import os
import sqlite3
import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext, ContextTypes,
)

# Replace with your Telegram bot API token
Your_bot_token_id = '7873292564:AAE-iennxxgq5vXYUl-WruZF5HJ7KPAn4FY'  # Replace with your bot's API token

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



# def initialize_database2():
#     connection = sqlite3.connect("messages.db")
#     cursor = connection.cursor()
#     cursor.execute("""
#                    CREATE TABLE IF NOT EXISTS messages (
#                                                            muroajaat_id INTEGER PRIMARY KEY AUTOINCREMENT,
#                                                            username TEXT,
#                                                            user_id INTEGER NOT NULL,
#                                                            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                                                            media_type TEXT,
#                                                            media_id TEXT,
#                                                            text_content TEXT
#                    )
#                    """)
#     connection.commit()
#     connection.close()


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
STATE_AUTH_TOLOV_Q1 = "auth_q1"
STATE_AUTH_TOLOV_Q2 = "auth_q2"
STATE_AUTH_TOLOV_Q3 = "auth_q3"
STATE_AUTH_TOLOV_Q4 = "auth_q4"
STATE_AUTH_TOLOV_Q5 = "auth_q5"
STATE_AUTH_DONE = "auth_done"
STATE_AUTH_FACTOR_Q1 = "auth_f_q1"
STATE_AUTH_FACTOR_Q2 = "auth_f_q2"
STATE_AUTH_FACTOR_Q3 = "auth_f_q3"
STATE_AUTH_FACTOR_Q4 = "auth_f_q4"
STATE_AUTH_FACTOR_Q5 = "auth_f_q5"
STATE_AUTH_KONVERT_Q1 = "auth_k_q1"
STATE_AUTH_KONVERT_Q2 = "auth_k_q2"
STATE_AUTH_KONVERT_Q3 = "auth_k_q3"
STATE_AUTH_KONVERT_Q4 = "auth_k_q4"
STATE_AUTH_KONVERT_Q5 = "auth_k_q5"


user_states = {}
user_answers = {}
user_history = {}   # Dictionary to track user navigation history
                    # A dictionary to manage states for all users

# Define user states
STATE_NONE = "none"
STATE_PROBLEM = "problem"
STATE_FEEDBACK = "feedback"

expert_to_user = {}

def push_to_history(user_id, state):
    if user_id not in user_history:
        user_history[user_id] = []
    user_history[user_id].append(state)

def pop_from_history(user_id):
    if user_id in user_history and user_history[user_id]:
        return user_history[user_id].pop()
    return None  # Default to None if history is empty


async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_message = update.message.text
    except AttributeError:
        logging.warning("Error: Message is not a text message")
        return
    user_id = update.message.chat_id
    logging.warning('Handled')
    if user_message == "Qo'llanmalar":
        push_to_history(user_id, "Qo'llanmalar")
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
        file_path = "C:\\Users\\ibroh\\OneDrive\\Desktop\\Swift to'lovlari.pdf"
        try:
            with open(file_path, "rb") as file:
                await context.bot.send_document(chat_id=user_id, document=file)
            await update.message.reply_text(
                "Hujjat muvaffaqiyatli yuborildi!",
                reply_markup=ReplyKeyboardMarkup([["Orqaga"]], resize_keyboard=True)
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
            "Hujjat muvaffaqiyatli yuborildi!",
            reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton("Orqaga")],
            ], resize_keyboard=True),
        )
        file_path = "C:\\Users\\ibroh\\OneDrive\\Desktop\\Konvertatsiya amaliyoti.pdf"  # Replace with the correct file path
        with open(file_path, "rb") as file:
            await context.bot.send_document(chat_id=user_id, document=file)
            return


    elif user_message == "3. Faktoring amaliyoti":
        # Ask user to choose a language for the document
        await update.message.reply_text(
            "Hujjatni qaysi tilda olishni istaysiz?",
            reply_markup=ReplyKeyboardMarkup(
                [
                    [KeyboardButton("Rus tilida"), KeyboardButton("O'zbek tilida")],
                    [KeyboardButton("Orqaga")],
                ],
                resize_keyboard=True,
            )
        )
        # Update state to wait for language selection
        user_states[user_id] = "LANGUAGE_SELECTION"
        return

    elif user_states.get(user_id) == "LANGUAGE_SELECTION":
        if user_message == "Rus tilida":
            # Send the document in Russian
            file_path = "C:\\Users\\ibroh\\OneDrive\\Desktop\\дебитор_порядок действий v-1.pdf"  # Replace with Russian file path
            with open(file_path, "rb") as file:
                await context.bot.send_document(chat_id=user_id, document=file)
            await update.message.reply_text(
                "Hujjat rus tilida muvaffaqiyatli yuborildi!",
                reply_markup=ReplyKeyboardMarkup(
                    [[KeyboardButton("Orqaga")]],
                    resize_keyboard=True,
                )
            )
        elif user_message == "O'zbek tilida":
            # Send the document in Uzbek
            file_path = "C:\\Users\\ibroh\\OneDrive\\Desktop\\дебитор_порядок действий Uz.docx"  # Replace with Uzbek file path
            with open(file_path, "rb") as file:
                await context.bot.send_document(chat_id=user_id, document=file)
            await update.message.reply_text(
                "Hujjat o'zbek tilida muvaffaqiyatli yuborildi!",
                reply_markup=ReplyKeyboardMarkup(
                    [[KeyboardButton("Orqaga")]],
                    resize_keyboard=True,
                )
            )

        # else:
        #     # Handle invalid input
        #     await update.message.reply_text(
        #         "Iltimos, tugmalardan birini tanlang.",
        #         reply_markup=ReplyKeyboardMarkup(
        #             [
        #                 [KeyboardButton("Rus tilida"), KeyboardButton("O'zbek tilida")],
        #                 [KeyboardButton("Orqaga")],
        #             ],
        #             resize_keyboard=True,
        #         )
        #     )
        # return



    if user_message == "Bank bilan bog'lanish":
        push_to_history(user_id, "Bank bilan bog'lanish")
        user_states[user_id] = STATE_PROBLEM
        await update.message.reply_text(
            "1. Mutahasis bilan bog'lanish uchun Chat tugmasini tanlang.\n 2. Mutahasis kontakt raqamlarini olish uchun Aloqaga chiqish tugmasini tanlang. ",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("1. Chat")],
                 [KeyboardButton("2. Aloqaga chiqish")],
                 [KeyboardButton("Orqaga")]], resize_keyboard=True)
        )
        return

    if user_message == "1. Chat":
        push_to_history(user_id, "1. Chat")
        # Start authentication flow
        user_states[user_id] = STATE_AUTH_TOLOV_Q1
        await update.message.reply_text(
            "Pastdagi tugmalardan birini tanlang",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("1. To'lov bo'yicha")],
                 [KeyboardButton("2. Konvertatsiya bo'yicha")],
                 [KeyboardButton("3. Faktoring bo'yicha")],
                 [KeyboardButton("Orqaga")]], resize_keyboard=True)
        )
        return


    elif user_message == "1. To'lov bo'yicha":
        # Start the form for "To'lov bo'yicha"
        push_to_history(user_id, "1. To'lov bo'yicha")
        user_states[user_id] = STATE_AUTH_TOLOV_Q1
        await update.message.reply_text(
            "Iltimos, Mutahasisga bog'lanish uchun oldin o'zingiz haqingizda ma'lumot bering.\nDastlab korxonaning nomini kiriting"
        )
        return

    elif user_message == "2. Konvertatsiya bo'yicha":
        # Start the form for "To'lov bo'yicha"
        push_to_history(user_id, "2. Konvertatsiya bo'yicha")
        user_states[user_id] = STATE_AUTH_KONVERT_Q1
        await update.message.reply_text(
            "Iltimos, Mutahasisga bog'lanish uchun oldin o'zingiz haqingizda ma'lumot bering.\nDastlab korxonaning nomini kiriting"
        )
        return

    elif user_message == "3. Faktoring bo'yicha":
        # Start the form for "To'lov bo'yicha"
        push_to_history(user_id, "3. Faktoring bo'yicha")
        user_states[user_id] = STATE_AUTH_FACTOR_Q1
        await update.message.reply_text(
            "Iltimos, Mutahasisga bog'lanish uchun oldin o'zingiz haqingizda ma'lumot bering.\nDastlab korxonaning nomini va STIR raqamini kiriting:"
        )
        return

    elif user_message == "Orqaga":
        await handle_orqaga(update, context)
        return

    elif user_states.get(user_id) == STATE_AUTH_TOLOV_Q1:
        # Save answer to first question
        user_answers[user_id] = {"Korxona nomi": user_message}
        user_states[user_id] = STATE_AUTH_TOLOV_Q2
        await update.message.reply_text("Iltimos, Korxonaning manzilini kiriting")
        return

    elif user_states.get(user_id) == STATE_AUTH_TOLOV_Q2:
        # Save second answer
        user_answers[user_id]["Manzil"] = user_message
        user_states[user_id] = STATE_AUTH_TOLOV_Q3
        # You can validate answers here if you want
        await update.message.reply_text(
            "BANK MFO si ",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Orqaga")]], resize_keyboard=True)
        )
        return

    elif user_states.get(user_id) == STATE_AUTH_TOLOV_Q3:
        # Validate if the message contains only numbers
        if not user_message.isdigit():
            await update.message.reply_text(
                "Iltimos, faqat raqamlarni kiriting.",
                reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Orqaga")]], resize_keyboard=True)
            )
            return

        # Save valid answer
        user_answers[user_id]["MFO"] = user_message
        user_states[user_id] = STATE_AUTH_TOLOV_Q4
        await update.message.reply_text(
            "Telefon raqami",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Orqaga")]], resize_keyboard=True)
        )
        return

    elif user_states.get(user_id) == STATE_AUTH_TOLOV_Q4:
        # Validate if the input is a valid phone number (digits only, or allow specific format)
        if not user_message.isdigit() or len(user_message) < 9 or len(user_message) > 15:
            await update.message.reply_text(
                "Iltimos, faqat to'g'ri telefon raqamini kiriting (Masalan 998XXXXXXXXX formatda).",
                reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Orqaga")]], resize_keyboard=True)
            )
            return

        # Save valid phone number
        user_answers[user_id]["Telefon raqam"] = user_message
        user_states[user_id] = STATE_AUTH_TOLOV_Q5
        await update.message.reply_text(
            "Murojatchining FIO si",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Orqaga")]], resize_keyboard=True)
        )
        return


    elif user_states.get(user_id) == STATE_AUTH_TOLOV_Q5:
        # Store the last user message in their details
        user_answers[user_id]["FIO"] = user_message

        # Change the state to indicate the process is done
        user_states[user_id] = STATE_AUTH_DONE

        # Format the collected details for sending back to the user
        filled_out_details = "\n".join([f"{key}: {value}" for key, value in user_answers[user_id].items()])

        # Send a confirmation message along with the filled-out details
        await update.message.reply_text(
            "Tasdiqlash muvaffaqiyatli yakunlandi. Siz to'lov bo'yicha mutahasis bilan bog'lanish uchun quyidagi ma'lumotlarni kiritdingiz:\n\n"
            f"{filled_out_details}\n\n"
            "Endi muammo yoki savolingizni yozingingiz mumkin:",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Orqaga")]], resize_keyboard=True)
        )
        return

    elif user_states.get(user_id) == STATE_AUTH_KONVERT_Q1:
        # Save answer to first question
        user_answers[user_id] = {"Korxona nomi": user_message}
        user_states[user_id] = STATE_AUTH_KONVERT_Q2
        await update.message.reply_text("Iltimos, Korxonaning manzilini kiriting")
        return

    elif user_states.get(user_id) == STATE_AUTH_KONVERT_Q2:
        # Save second answer
        user_answers[user_id]["Manzil"] = user_message
        user_states[user_id] = STATE_AUTH_KONVERT_Q3
        # You can validate answers here if you want
        await update.message.reply_text(
            "BANK MFO si ",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Orqaga")]], resize_keyboard=True)
        )
        return

    elif user_states.get(user_id) == STATE_AUTH_KONVERT_Q3:
        # Validate if the message contains only numbers
        if not user_message.isdigit():
            await update.message.reply_text(
                "Iltimos, faqat raqamlarni kiriting.",
                reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Orqaga")]], resize_keyboard=True)
            )
            return

        # Save valid answer
        user_answers[user_id]["MFO"] = user_message
        user_states[user_id] = STATE_AUTH_KONVERT_Q4
        await update.message.reply_text(
            "Telefon raqami",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Orqaga")]], resize_keyboard=True)
        )
        return

    elif user_states.get(user_id) == STATE_AUTH_KONVERT_Q4:
        # Validate if the input is a valid phone number (digits only, or allow specific format)
        if not user_message.isdigit() or len(user_message) < 9 or len(user_message) > 15:
            await update.message.reply_text(
                "Iltimos, faqat to'g'ri telefon raqamini kiriting (Masalan 998XXXXXXXXX formatda).",
                reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Orqaga")]], resize_keyboard=True)
            )
            return

        # Save valid phone number
        user_answers[user_id]["Telefon raqam"] = user_message
        user_states[user_id] = STATE_AUTH_KONVERT_Q5
        await update.message.reply_text(
            "Murojatchining FIO si",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Orqaga")]], resize_keyboard=True)
        )
        return




    elif user_states.get(user_id) == STATE_AUTH_KONVERT_Q5:
        # Store the last user message in their details
        user_answers[user_id]["FIO"] = user_message

        # Change the state to indicate the process is done
        user_states[user_id] = STATE_AUTH_DONE

        # Format the collected details for sending back to the user
        filled_out_details = "\n".join([f"{key}: {value}" for key, value in user_answers[user_id].items()])

        # Send a confirmation message along with the filled-out details
        await update.message.reply_text(
            "Tasdiqlash muvaffaqiyatli yakunlandi. Siz konvertatsiya bo'yicha mutahasis bilan bog'lanish uchun quyidagi ma'lumotlarni kiritdingiz:\n\n"
            f"{filled_out_details}\n\n"
            "Endi muammo yoki savolingizni yozingingiz mumkin:",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Orqaga")]], resize_keyboard=True)
        )
        return


    elif user_states.get(user_id) == STATE_AUTH_FACTOR_Q1:
        # Save answer to first question
        user_answers[user_id] = {"Korxona nomi va STIR raqami": user_message}
        user_states[user_id] = STATE_AUTH_FACTOR_Q2
        await update.message.reply_text("Iltimos, Korxonaning rahbarining FIO si kiriting")
        return

    elif user_states.get(user_id) == STATE_AUTH_FACTOR_Q2:
        # Save second answer
        user_answers[user_id]["FIO"] = user_message
        user_states[user_id] = STATE_AUTH_FACTOR_Q3
        # You can validate answers here if you want
        await update.message.reply_text(
            "Iltimos, telefon raqamingizni kiriting: ",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Orqaga")]], resize_keyboard=True)
        )
        return

    elif user_states.get(user_id) == STATE_AUTH_FACTOR_Q3:
        # Validate if the input is a valid phone number (digits only, or allow specific format)
        if not user_message.isdigit() or len(user_message) < 9 or len(user_message) > 15:
            await update.message.reply_text(
                "Iltimos, faqat to'g'ri telefon raqamini kiriting (Masalan 998XXXXXXXXX formatda).",
                reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Orqaga")]], resize_keyboard=True)
            )
            return

        # Save valid phone number
        user_answers[user_id]["Telefon raqam"] = user_message
        user_states[user_id] = STATE_AUTH_FACTOR_Q4
        await update.message.reply_text(
            "Bankning qaysi filiali mijozisiz?",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Orqaga")]], resize_keyboard=True)
        )
        return


    elif user_states.get(user_id) == STATE_AUTH_FACTOR_Q4:
        # Save second answer
        user_answers[user_id]["Filial"] = user_message
        user_states[user_id] = STATE_AUTH_FACTOR_Q5
        # You can validate answers here if you want
        await update.message.reply_text(
            "Murojaat maqsadi",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Orqaga")]], resize_keyboard=True)
        )
        return


    elif user_states.get(user_id) == STATE_AUTH_FACTOR_Q5:
        # Store the last user message in their details
        user_answers[user_id]["Murojaatning maqsadi"] = user_message

        # Change the state to indicate the process is done
        user_states[user_id] = STATE_AUTH_DONE

        # Format the collected details for sending back to the user
        filled_out_details = "\n".join([f"{key}: {value}" for key, value in user_answers[user_id].items()])

        # Send a confirmation message along with the filled-out details
        await update.message.reply_text(
            "Tasdiqlash muvaffaqiyatli yakunlandi. Siz faktoring bo'yicha mutahasis bilan bog'lanish uchun quyidagi ma'lumotlarni kiritdingiz:\n\n"
            f"{filled_out_details}\n\n"
            "Endi muammo yoki savolingizni yozingingiz mumkin:",
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



    elif user_message == "Fikr-mulohaza qoldirish":
        user_states[user_id] = STATE_FEEDBACK
        await update.message.reply_text(
            "Bank xizmatlari to'g'risida o'z fikr-mulohazalaringizni qoldiring. Xizmatlarimiz Siz uchun yanada qulay, tez va sodda bo'lishida o'z hissangizni qo'shing",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Orqaga")]], resize_keyboard=True)
        )



    elif user_states.get(user_id) == STATE_AUTH_DONE:
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
            "Kechirasiz, so'rovingizni tushunmadim menyudan tanlang.", reply_markup=main_menu_keyboard()
        )

async def handle_orqaga(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    previous_state = pop_from_history(user_id)

    if previous_state is None:
        # If history is empty, return to the main menu
        await update.message.reply_text(
            "Bosh menyuga qaytdingiz.",
            reply_markup=main_menu_keyboard()
        )
        user_states[user_id] = STATE_NONE
        return

    # Navigate back based on the previous state
    if previous_state == "Qo'llanmalar":
        await update.message.reply_text(
            "Qo'llanmalar bo'limiga qaytdingiz.",
            reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton("1. Internet banking tizimida SWIFT to'lovlari")],
                [KeyboardButton("2. Konvertatsiya amaliyoti")],
                [KeyboardButton("3. Faktoring amaliyoti")],
                [KeyboardButton("Orqaga")]
            ], resize_keyboard=True)
        )
    elif previous_state == "Bank bilan bog'lanish":
        await update.message.reply_text(
            "Bank bilan bog'lanish bo'limiga qaytdingiz.",
            reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton("1. Chat")],
                [KeyboardButton("2. Aloqaga chiqish")],
                [KeyboardButton("Orqaga")]
            ], resize_keyboard=True)
        )
    elif previous_state == "1. Chat":
        await update.message.reply_text(
            "Chat bo'limiga qaytdingiz.",
            reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton("1. To'lov bo'yicha")],
                [KeyboardButton("2. Konvertatsiya bo'yicha")],
                [KeyboardButton("3. Faktoring bo'yicha")],
                [KeyboardButton("Orqaga")]
            ], resize_keyboard=True)
        )


    else:
        # Default fallback for other cases
        await update.message.reply_text(
            "Avvalgi bo'limga qaytdingiz.",
            reply_markup=main_menu_keyboard()
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
    application = Application.builder().token(Your_bot_token_id).build()

    # Add handlers for commands and messages
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("getid", get_group_id))  # Add the handler here
    # application.add_handler(MessageHandler(filters.TEXT &  filters.ChatType.PRIVATE, handle_user_message))
    application.add_handler(MessageHandler(filters.ALL   &  filters.ChatType.PRIVATE, handle_user_message))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUP, handle_expert_reply))



    # Adding handler for text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))


    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
