import os
import pandas as pd
import matplotlib.pyplot as plt
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext, MessageHandler, CallbackQueryHandler, filters
from flask import Flask
import threading

# Flask app server
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running"

# Global dictionary to store datasets and user preferences for each user
user_data = {}
user_language = {}

# Start command handler
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("O'zbek tili", callback_data='lang_uz')],
        [InlineKeyboardButton("English", callback_data='lang_en')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Iltimos, tilni tanlang / Please select a language:", reply_markup=reply_markup)

# Function to handle language selection
async def set_language(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.message.chat_id
    lang = query.data.split('_')[1]
    user_language[user_id] = lang

    if lang == 'uz':
        await query.edit_message_text(" Assalomu alaykum! Iltimos, tahlil qilish uchun datasetni yuboring.")
    elif lang == 'en':
        await query.edit_message_text(" Hello! Please send the dataset for analysis.")

# Function to get the text based on user language
def get_text(user_id, text_key):
    texts = {
        'uz': {
            'upload_dataset': "Iltimos, tahlil qilish uchun datasetni yuboring.",
            'nan_summary': "Quyidagi ustunlarda nan qiymatlar mavjud:\n{summary}\nUlarni median qiymatlar bilan avtomatik to‘ldiramiz.",
            'nan_filled': "Dataset nan qiymatlar to‘ldirildi va tozalangan dataset tayyor.",
            'no_nan': "Datasetda nan qiymatlar mavjud emas.",
            'select_column': "Qaysi ustunlarni grafikda ko‘rishni xohlaysiz?",
            'select_graph_type': "{column} ustuni uchun qaysi grafik turini ko‘rishni xohlaysiz?",
            'graph_error': "Grafik yaratishda xatolik yuz berdi: {error}",
            'another_graph': "Yana bir grafik ko‘rishni xohlaysizmi?",
            'cleaned_dataset': "Tozalangan dataset yuborildi.",
            'show_features': "Botning asosiy xususiyatlari bilan tanishing.",
            'features': (
                "Botimizning hozirgi xususiyati:\n"
                "- Datasetni cleaning qilish, tozalash va NaN qiymatlarni o‘rniga median qiymatlar bilan to‘ldirish.\n\n"
                "To‘liq xususiyatlari hali ishga tushirilmagan, lekin qo‘shilishi mumkin bo‘lgan xususiyatlar:\n"
                "- Foydalanuvchi xohlagan ustunlarni xohlagan grafiklarda vizualizatsiya qilish.\n"
                "- Keraksiz ustunlarni olib tashlash.\n"
                "- Machine Learning orqali kichik modellar yaratish va trening qilish.\n\n"
                "Kutilayotgan xususiyatlar tez orada qo‘shiladi. 😊"
            )
        },
        'en': {
            'upload_dataset': "Please send the dataset for analysis.",
            'nan_summary': "The following columns have NaN values:\n{summary}\nWe will automatically fill them with median values.",
            'nan_filled': "The dataset has been cleaned and NaN values filled.",
            'no_nan': "The dataset has no NaN values.",
            'select_column': "Which columns would you like to visualize?",
            'select_graph_type': "Which type of graph would you like for the {column} column?",
            'graph_error': "Error occurred while generating the graph: {error}",
            'another_graph': "Would you like to see another graph?",
            'cleaned_dataset': "The cleaned dataset has been sent.",
            'show_features': "Get to know the main features of the bot.",
            'features': (
                "Current features of our bot:\n"
                "- Dataset cleaning, removing NaN values, and filling them with median values.\n\n"
                "Full features are not yet implemented, but the following features may be added:\n"
                "- Visualizing selected columns in various charts.\n"
                "- Removing unnecessary columns.\n"
                "- Creating small models and training them using Machine Learning.\n\n"
                "Expected features will be added soon. 😊"
            )
        }
    }
    lang = user_language.get(user_id, 'uz')
    return texts[lang].get(text_key, '')

# Function to handle received dataset
async def receive_dataset(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat_id
    file = await update.message.document.get_file()
    file_path = f"{user_id}_dataset.csv"
    await file.download_to_drive(file_path)

    # Load dataset
    try:
        df = pd.read_csv(file_path)
        user_data[user_id] = df
    except Exception as e:
        await update.message.reply_text(f"Datasetni yuklashda xatolik yuz berdi: {str(e)}")
        return

    # Identify columns with NaN values
    nan_columns = df.columns[df.isna().any()].tolist()
    if nan_columns:
        nan_summary = "\n".join([f"{col}: {df[col].isna().sum()} NaN values" for col in nan_columns])
        await update.message.reply_text(get_text(user_id, 'nan_summary').format(summary=nan_summary))
        
        # Automatically fill NaN values with median for numeric columns and mode for non-numeric columns
        for col in nan_columns:
            if df[col].dtype in ['float64', 'int64']:
                df[col].fillna(df[col].median(), inplace=True)
            else:
                df[col].fillna(df[col].mode()[0], inplace=True)
        
        user_data[user_id] = df
        df.to_csv(f'{user_id}_cleaned_dataset.csv', index=False)
        
        # Inform the user and send cleaned dataset
        await update.message.reply_text(get_text(user_id, 'nan_filled'))
        with open(f'{user_id}_cleaned_dataset.csv', 'rb') as file:
            await context.bot.send_document(chat_id=user_id, document=file)

        # Add button to show bot's main features
        keyboard = [[InlineKeyboardButton(get_text(user_id, 'show_features'), callback_data='show_bot_features')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=user_id, text=get_text(user_id, 'show_features'), reply_markup=reply_markup)
    else:
        await update.message.reply_text(get_text(user_id, 'no_nan'))

# Function to handle graph column selection
async def graph_column(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.message.chat_id
    df = user_data.get(user_id)

    if df is None or df.empty:
        await query.answer("Hech qanday dataset topilmadi.")
        return

    column = query.data.replace('graph_', '')
    keyboard = [
        [InlineKeyboardButton("Histogram", callback_data=f'hist_{column}')],
        [InlineKeyboardButton("Line chart", callback_data=f'line_{column}')],
        [InlineKeyboardButton("Boxplot", callback_data=f'box_{column}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(get_text(user_id, 'select_graph_type').format(column=column), reply_markup=reply_markup)

# Function to generate the selected graph
async def graph_type(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.message.chat_id
    df = user_data.get(user_id)

    if df is None or df.empty:
        await query.answer("Hech qanday dataset topilmadi.")
        return

    data = query.data.split('_')
    graph_type, column = data[0], data[1]

    plt.figure()
    try:
        if graph_type == 'hist':
            df[column].plot(kind='hist')
        elif graph_type == 'line':
            df[column].plot(kind='line')
        elif graph_type == 'box':
            df[column].plot(kind='box')

        plt.title(f'{column} uchun {graph_type}')
        plt.savefig(f'{user_id}_{column}.png')
        plt.close()

        with open(f'{user_id}_{column}.png', 'rb') as file:
            await context.bot.send_photo(chat_id=user_id, photo=file)
        os.remove(f'{user_id}_{column}.png')
    except Exception as e:
        await query.edit_message_text(get_text(user_id, 'graph_error').format(error=str(e)))
        return

    keyboard = [
        [InlineKeyboardButton("Ha", callback_data='view_another_graph')],
        [InlineKeyboardButton("Yo‘q", callback_data='send_cleaned_dataset')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(get_text(user_id, 'another_graph'), reply_markup=reply_markup)

# Function to handle after viewing graph
async def view_another_graph(update: Update, context: CallbackContext) -> None:
    await generate_graph(update.callback_query, context)

# Function to send cleaned dataset
async def send_cleaned_dataset(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.message.chat_id
    file_path = f'{user_id}_cleaned_dataset.csv'
    try:
        with open(file_path, 'rb') as file:
            await context.bot.send_document(chat_id=user_id, document=file)
        await query.edit_message_text(get_text(user_id, 'cleaned_dataset'))
        # Add button to show bot's main features
        keyboard = [[InlineKeyboardButton(get_text(user_id, 'show_features'), callback_data='show_bot_features')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=user_id, text=get_text(user_id, 'show_features'), reply_markup=reply_markup)
    except Exception as e:
        await query.edit_message_text(f"Datasetni yuborishda xatolik yuz berdi: {str(e)}")

# Function to show bot features
async def show_bot_features(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.edit_message_text(get_text(query.message.chat_id, 'features'))

# Main function to start the bot
def main():
    token = "7292225510:AAFUWV9w9RyCsrH9qgRSCxnXzegsrptYkIY"

    if not token:
        raise ValueError("Bot tokeni kiritilmadi")

    application = ApplicationBuilder().token(token).build()

    # Add handlers to the application
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(set_language, pattern='^lang_.*'))
    application.add_handler(MessageHandler(filters.Document.MimeType("text/csv"), receive_dataset))
    application.add_handler(CallbackQueryHandler(graph_column, pattern='^graph_.*'))
    application.add_handler(CallbackQueryHandler(graph_type, pattern='^(hist|line|box)_.*'))
    application.add_handler(CallbackQueryHandler(view_another_graph, pattern='view_another_graph'))
    application.add_handler(CallbackQueryHandler(send_cleaned_dataset, pattern='send_cleaned_dataset'))
    application.add_handler(CallbackQueryHandler(show_bot_features, pattern='show_bot_features'))

    # Flask serverini yangi ipda va portda ishga tushirish
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))).start()

    # Botni ishga tushirish
    application.run_polling()

if __name__ == '__main__':
    main()
