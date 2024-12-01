# Data-Celaning-bot
# Telegram Data Analysis Bot

## Overview
This is a Telegram bot developed to assist users in performing data analysis tasks, such as cleaning datasets, handling missing values, and visualizing data through graphs. The bot provides support for both Uzbek and English languages, enabling broader accessibility. Below, you'll find details about the main features and capabilities of this bot.

## Features

### 1. Language Selection (O'zbek & English)
Upon starting the bot, users are prompted to select their preferred language: Uzbek or English. The bot tailors all its responses to the selected language for ease of use.

### 2. Dataset Upload
Users can send a CSV dataset to the bot, which it processes for further analysis. This feature is especially useful for individuals looking to explore and clean their data without the need for advanced tools or programming.

### 3. Data Cleaning
The bot automatically analyzes the dataset for missing values (NaN values). For columns with NaN values:
- Numeric columns are filled with their respective median values.
- Non-numeric columns are filled with the most frequent values.

After cleaning, users receive the updated dataset.

### 4. Data Visualization
The bot allows users to visualize data by creating different types of graphs:
- **Histogram**
- **Line Chart**
- **Boxplot**

Users can select specific columns to visualize, providing a better understanding of the dataset.

### 5. Dataset Analysis Report
After the dataset has been cleaned and visualized, the bot sends a cleaned version of the dataset along with any relevant analysis reports.

### 6. Bot Feature Overview
Users are given an overview of the bot's features upon request. This serves as a helpful guide, especially for new users exploring its capabilities.

### Planned Features
- Allow users to remove unwanted columns from the dataset.
- Develop small machine learning models for prediction purposes.
- Expand visualizations with more advanced options.
- Introduce custom analysis and reporting features based on user requirements.

## Usage Instructions
1. **Start the Bot**: Send the `/start` command to initialize the bot. You will be prompted to choose your language.
2. **Upload Dataset**: Upload a CSV file containing the dataset you want to analyze.
3. **Data Cleaning**: The bot will automatically clean the data by handling missing values.
4. **Visualization**: Select columns and graph types to visualize the cleaned dataset.
5. **Receive Cleaned Data**: Once cleaning and visualization are done, you can request the cleaned dataset.


# Telegram Ma'lumot Tahlili Bot

## Umumiy Ma'lumot
Bu Telegram bot foydalanuvchilarga ma'lumotlarni tahlil qilishda yordam berish uchun ishlab chiqilgan. Botning vazifalari orasida datasetlarni tozalash, yetishmayotgan qiymatlarni to'ldirish va grafik orqali ma'lumotlarni vizualizatsiya qilish kiradi. Bot o'zbek va ingliz tillarini qo'llab-quvvatlaydi.

## Xususiyatlar

### 1. Til Tanlash (O'zbek va Ingliz)
Botni ishga tushirganda, foydalanuvchi o'ziga qulay tilni tanlashi mumkin: o'zbek yoki ingliz. Bot tanlangan tilga mos ravishda barcha javoblarni moslashtiradi.

### 2. Dataset Yuklash
Foydalanuvchilar botga CSV formatidagi datasetni yuborishlari mumkin. Bot bu datasetni tahlil qilish uchun qayta ishlaydi.

### 3. Ma'lumot Tozalash
Bot datasetda NaN qiymatlarning mavjudligini aniqlaydi. Quyidagicha tozalash ishlari amalga oshiriladi:
- Raqamli ustunlar uchun median qiymatlar bilan to'ldiriladi.
- Raqamli bo'lmagan ustunlar uchun eng ko'p uchraydigan qiymat bilan to'ldiriladi.

Tozalangan dataset foydalanuvchiga yuboriladi.

### 4. Ma'lumotlarni Vizualizatsiya Qilish
Bot ma'lumotlarni quyidagi grafiklar yordamida vizualizatsiya qilish imkonini beradi:
- **Gistogramma**
- **Chiziqli Grafik**
- **Boxplot**

Foydalanuvchi qaysi ustunlarni vizualizatsiya qilishni tanlashi mumkin.

### 5. Dataset Tahlil Hisoboti
Dataset tozalangandan va vizualizatsiya qilingandan so'ng, foydalanuvchiga tozalangan versiyasi va tahlil hisobotlari yuboriladi.

### Rejalashtirilayotgan Xususiyatlar
- Foydalanuvchilarga kerakmas ustunlarni olib tashlash imkonini berish.
- Kichik machine learning modellar yaratish.
- Vizualizatsiyalarni kengaytirish.
- Foydalanuvchi talabiga asosan maxsus tahlil va hisobot yaratish.

## Foydalanish Bo'yicha Qo'llanma
1. **Botni Boshlash**: `/start` komandasini yuboring va tilni tanlang.
2. **Dataset Yuklash**: Tahlil qilish uchun CSV faylni yuboring.
3. **Ma'lumot Tozalash**: Bot avtomatik ravishda datasetni tozalaydi.
4. **Vizualizatsiya**: Ustunlarni va grafik turini tanlab, ma'lumotlarni vizualizatsiya qiling.
5. **Tozalangan Ma'lumotni Qabul Qilish**: Tahlil va tozalash tugagach, tozalangan datasetni olish mumkin.

## O'rnatish va Sozlash
Botni lokal kompyuterda ishlatish uchun quyidagi qadamlarni bajaring:
1. Repozitoriyani klonlang:
   ```sh
   git clone https://github.com/yourusername/telegram-data-analysis-bot.git
   ```
2. Zaruriy kutubxonalarni o'rnating:
   ```sh
   pip install -r requirements.txt
   ```
3. Bot tokenini `main()` funksiyasida o'rnating.
4. Botni ishga tushiring:
   ```sh
   python bot.py
   ```

## Kutubxonalar
- **Python**: 3.x
- **pandas**: Ma'lumotlarni tahlil qilish uchun
- **matplotlib**: Ma'lumotlarni vizualizatsiya qilish uchun
- **python-telegram-bot**: Telegram API bilan ishlash uchun

