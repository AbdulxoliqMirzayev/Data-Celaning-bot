import logging
import asyncio
import json
import os
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "7035383827:AAHnt_3Ufqp70pzEs7xrhfB-yqfp8Ig7Lzc"
ADMIN_ID = 5262564837
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Ma'lumotlar fayli
DATA_FILE = "bot_data.json"

# Ma'lumotlarni yuklash/saqlash funksiyalari
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data.get("users"), list):
                    data["users"] = list(data["users"])
                elif not isinstance(data.get("users"), list):
                    data["users"] = []
                return data
        except Exception as e:
            logging.error(f"Ma'lumotlarni yuklashda xatolik: {e}")
            pass
    return {
        "users": [],
        "orders": [],
        "user_count": 0
    }

def save_data(data):
    data_to_save = data.copy()
    if isinstance(data_to_save["users"], set):
        data_to_save["users"] = list(data["users"])
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Ma'lumotlarni saqlashda xatolik: {e}")

# Global ma'lumotlar
try:
    bot_data = load_data()
    users_data = bot_data.get("users", [])
    if isinstance(users_data, list):
        clean_users = []
        for user in users_data:
            if isinstance(user, dict):
                if 'user_id' in user:
                    clean_users.append(user['user_id'])
                elif 'id' in user:
                    clean_users.append(user['id'])
            elif isinstance(user, (int, str)):
                try:
                    clean_users.append(int(user))
                except (ValueError, TypeError):
                    pass
        bot_data["users"] = set(clean_users)
    else:
        bot_data["users"] = set()
except Exception as e:
    logging.error(f"Ma'lumotlarni yuklashda xatolik: {e}")
    bot_data = {
        "users": set(),
        "orders": [],
        "user_count": 0
    }

# States
class OrderState(StatesGroup):
    waiting_for_brand = State()
    waiting_for_model = State()
    waiting_for_case_type = State()
    waiting_for_image = State()
    waiting_for_custom_case = State()
    waiting_for_location = State()
    waiting_for_contact = State()
    waiting_for_confirmation = State()

class AdminState(StatesGroup):
    admin_menu = State()

# iPhone modellari va narxlar
IPHONE_MODELS = {
    "iPhone 7": 70000, "iPhone 7 Plus": 70000,
    "iPhone 8": 70000, "iPhone 8 Plus": 70000,
    "iPhone X": 70000, "iPhone XR": 70000, "iPhone XS": 70000, "iPhone XS Max": 70000,
    "iPhone 11": 70000, "iPhone 11 Pro": 70000, "iPhone 11 Pro Max": 70000,
    "iPhone 12": 70000, "iPhone 12 Mini": 70000, "iPhone 12 Pro": 70000, "iPhone 12 Pro Max": 70000,
    "iPhone 13": 70000, "iPhone 13 Mini": 70000, "iPhone 13 Pro": 70000, "iPhone 13 Pro Max": 70000,
    "iPhone 14": 70000, "iPhone 14 Plus": 70000, "iPhone 14 Pro": 70000, "iPhone 14 Pro Max": 70000,
    "iPhone 15": 80000, "iPhone 15 Plus": 80000, "iPhone 15 Pro": 80000, "iPhone 15 Pro Max": 80000,
    "iPhone 16": 80000, "iPhone 16 Plus": 80000, "iPhone 16 Pro": 80000, "iPhone 16 Pro Max": 80000
}

# Samsung modellari va narxlar
SAMSUNG_MODELS = {
    "Samsung Galaxy S20": 70000, "Samsung Galaxy S20+": 70000, "Samsung Galaxy S20 Ultra": 70000,
    "Samsung Galaxy S21": 70000, "Samsung Galaxy S21+": 70000, "Samsung Galaxy S21 Ultra": 70000,
    "Samsung Galaxy S22": 70000, "Samsung Galaxy S22+": 70000, "Samsung Galaxy S22 Ultra": 70000,
    "Samsung Galaxy S23": 70000, "Samsung Galaxy S23+": 70000, "Samsung Galaxy S23 Ultra": 70000,
    "Samsung Galaxy S24": 70000, "Samsung Galaxy S24+": 70000, "Samsung Galaxy S24 Ultra": 70000,
    "Samsung Galaxy S25": 70000, "Samsung Galaxy S25+": 70000, "Samsung Galaxy S25 Ultra": 70000
}

# Vaqtinchalik zakazlar
temp_orders = {}

# Funksiyalar
def get_price(brand, model, case_type):
    if case_type != "Rasimli (pechat bilan)":
        return 0
    if brand == "iPhone":
        return IPHONE_MODELS.get(model, 0)
    elif brand == "Samsung":
        return SAMSUNG_MODELS.get(model, 0)
    return 0

def register_user(user_id):
    if user_id not in bot_data["users"]:
        bot_data["users"].add(user_id)
        bot_data["user_count"] = len(bot_data["users"])
        save_data(bot_data)

def add_order(order_data):
    order_data["date"] = datetime.now().isoformat()
    order_data["status"] = "pending"
    bot_data["orders"].append(order_data)
    save_data(bot_data)

def mark_order_ready(user_id):
    for order in bot_data["orders"]:
        if order.get("user_id") == user_id and order.get("status") == "pending":
            order["status"] = "ready"
            order["ready_date"] = datetime.now().isoformat()
            save_data(bot_data)
            return True
    return False

def get_ready_orders_stats():
    ready_orders = [order for order in bot_data["orders"] if order.get("status") == "ready"]
    model_stats = {}
    for order in ready_orders:
        model = order.get("model", "Noma'lum")
        if model in model_stats:
            model_stats[model] += 1
        else:
            model_stats[model] = 1
    return model_stats, len(ready_orders)

def get_statistics():
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    year_ago = now - timedelta(days=365)
    
    total_users = len(bot_data["users"])
    total_orders = len(bot_data["orders"])
    
    week_orders = month_orders = year_orders = 0
    
    for order in bot_data["orders"]:
        try:
            order_date = datetime.fromisoformat(order["date"])
            if order_date >= week_ago:
                week_orders += 1
            if order_date >= month_ago:
                month_orders += 1
            if order_date >= year_ago:
                year_orders += 1
        except:
            continue
    
    return {
        "total_users": total_users,
        "total_orders": total_orders,
        "week_orders": week_orders,
        "month_orders": month_orders,
        "year_orders": year_orders
    }

# Klaviaturalar
def get_main_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛒 Buyurtma berish")],
        [KeyboardButton(text="📞 Admin bilan aloqa")]
    ], resize_keyboard=True)

def get_admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="stats")],
        [InlineKeyboardButton(text="📱 Sotilgan modellar", callback_data="sold_models")],
        [InlineKeyboardButton(text="❌ Yopish", callback_data="close_admin")]
    ])

def get_admin_confirmation_keyboard(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Zakaz qabul qilish", callback_data=f"accept_{user_id}")],
        [InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{user_id}")]
    ])

def get_brand_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📱 iPhone")],
        [KeyboardButton(text="📱 Samsung")],
        [KeyboardButton(text="🔙 Bosh menyu")]
    ], resize_keyboard=True, one_time_keyboard=True)

def get_model_keyboard(models_dict):
    keyboard_buttons = []
    for model in models_dict.keys():
        keyboard_buttons.append([KeyboardButton(text=model)])
    keyboard_buttons.append([KeyboardButton(text="🔙 Orqaga")])
    return ReplyKeyboardMarkup(keyboard=keyboard_buttons, resize_keyboard=True, one_time_keyboard=True)

def get_case_type_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🖼️ Rasimli (pechat bilan)")],
        [KeyboardButton(text="🎨 Boshqa chexol tanlash")],
        [KeyboardButton(text="🔙 Orqaga")]
    ], resize_keyboard=True, one_time_keyboard=True)

def get_confirmation_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="✅ Zakazni tasdiqlash")],
        [KeyboardButton(text="❌ Bekor qilish")],
        [KeyboardButton(text="🔙 Orqaga")]
    ], resize_keyboard=True, one_time_keyboard=True)

def get_final_confirmation_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="✅ Ha, aniq tasdiqlyman")],
        [KeyboardButton(text="❌ Yo'q, bekor qilaman")]
    ], resize_keyboard=True, one_time_keyboard=True)

def get_location_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📍 Manzilni yuborish", request_location=True)],
        [KeyboardButton(text="🔙 Orqaga")]
    ], resize_keyboard=True, one_time_keyboard=True)

def get_contact_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)],
        [KeyboardButton(text="🔙 Orqaga")]
    ], resize_keyboard=True, one_time_keyboard=True)

# Admin komandalar
@dp.message(Command("admin"))
async def admin_command(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("👨‍💼 Admin panel\n\nKerakli bo'limni tanlang:", reply_markup=get_admin_keyboard())
    else:
        await message.answer("❌ Sizda admin huquqi yo'q!")

@dp.callback_query(F.data == "stats")
async def show_statistics(callback: types.CallbackQuery):
    if callback.from_user.id == ADMIN_ID:
        stats = get_statistics()
        stats_text = (
            "📊 <b>Bot Statistikasi</b>\n\n"
            f"👥 <b>Jami foydalanuvchilar:</b> {stats['total_users']}\n"
            f"📦 <b>Jami zakazlar:</b> {stats['total_orders']}\n\n"
            f"📅 <b>Oxirgi hafta:</b> {stats['week_orders']} ta zakaz\n"
            f"📅 <b>Oxirgi oy:</b> {stats['month_orders']} ta zakaz\n"
            f"📅 <b>Oxirgi yil:</b> {stats['year_orders']} ta zakaz\n\n"
            f"📈 <b>Oxirgi yangilanish:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )
        await callback.message.edit_text(stats_text, parse_mode="HTML", reply_markup=get_admin_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "sold_models")
async def show_sold_models(callback: types.CallbackQuery):
    if callback.from_user.id == ADMIN_ID:
        model_stats, total_ready = get_ready_orders_stats()
        total_users = len(bot_data["users"])
        
        if not model_stats:
            stats_text = (
                "📱 <b>Sotilgan modellar</b>\n\n"
                "❌ Hozircha tayyor zakazlar yo'q\n\n"
                f"👥 <b>Jami obunachilar:</b> {total_users}"
            )
        else:
            stats_text = "📱 <b>Sotilgan modellar</b>\n\n"
            
            iphone_models = {k: v for k, v in model_stats.items() if "iPhone" in k}
            samsung_models = {k: v for k, v in model_stats.items() if "Samsung" in k}
            other_models = {k: v for k, v in model_stats.items() if "iPhone" not in k and "Samsung" not in k}
            
            if iphone_models:
                stats_text += "🍎 <b>iPhone modellari:</b>\n"
                for model, count in sorted(iphone_models.items()):
                    stats_text += f"   • {model}: {count} ta\n"
                stats_text += "\n"
            
            if samsung_models:
                stats_text += "📱 <b>Samsung modellari:</b>\n"
                for model, count in sorted(samsung_models.items()):
                    stats_text += f"   • {model}: {count} ta\n"
                stats_text += "\n"
            
            if other_models:
                stats_text += "📲 <b>Boshqa modellar:</b>\n"
                for model, count in sorted(other_models.items()):
                    stats_text += f"   • {model}: {count} ta\n"
                stats_text += "\n"
            
            stats_text += f"✅ <b>Jami sotilgan:</b> {total_ready} ta\n"
            stats_text += f"👥 <b>Jami obunachilar:</b> {total_users}"
        
        await callback.message.edit_text(stats_text, parse_mode="HTML", reply_markup=get_admin_keyboard())
    await callback.answer()

@dp.callback_query(F.data.startswith("ready_"))
async def order_ready(callback: types.CallbackQuery):
    if callback.from_user.id == ADMIN_ID:
        try:
            user_id = int(callback.data.split("_")[1])
            
            # Zakazni tayyor deb belgilash
            if mark_order_ready(user_id):
                # Foydalanuvchiga admin kontaktlari bilan xabar yuborish
                await bot.send_message(
                    chat_id=user_id,
                    text="🎉 <b>Zakazingiz tayyor!</b>\n\n"
                         "✅ Sizning telefon chexoli tayyor bo'ldi!\n\n"
                         "📞 <b>Admin bilan bog'laning:</b>\n"
                         "👤 <b>Admin:</b> Mirzayev Muhammadali\n"
                         "📱 <b>Telefon:</b> <code>+998954414666</code>\n"
                         "💬 <b>Telegram:</b> @Ali_Brandss\n\n"
                         "📍 <b>Manzil:</b> Toshkent shahar, Chilonzor tumani\n\n"
                         "Rahmat! 🙏",
                    parse_mode="HTML"
                )
                
                # Admin xabarini yangilash - tugmani o'chirish va status qo'shish
                original_caption = callback.message.caption or callback.message.text
                new_caption = original_caption + "\n\n✅ <b>ZAKAZ TAYYOR! Mijozga xabar yuborildi!</b>"
                
                # Tugmasiz yangi markup
                completed_keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="✅ Tayyor", callback_data="completed")]
                    ]
                )
                
                if callback.message.photo:
                    await callback.message.edit_caption(
                        caption=new_caption,
                        parse_mode="HTML",
                        reply_markup=completed_keyboard
                    )
                elif callback.message.document:
                    await callback.message.edit_caption(
                        caption=new_caption,
                        parse_mode="HTML",
                        reply_markup=completed_keyboard
                    )
                else:
                    await callback.message.edit_text(
                        text=new_caption,
                        parse_mode="HTML",
                        reply_markup=completed_keyboard
                    )
                
                await callback.answer("✅ Mijozga 'Zakaz tayyor' xabari yuborildi!")
            else:
                await callback.answer("❌ Zakaz topilmadi yoki allaqachon tayyor!")
            
        except Exception as e:
            logging.error(f"Zakaz tayyor xabarini yuborishda xatolik: {e}")
            await callback.answer("❌ Xabar yuborishda xatolik yuz berdi!")
    else:
        await callback.answer("❌ Sizda admin huquqi yo'q!")

# Tayyor zakazlar uchun callback (tugma bosilganda xabar berish)
@dp.callback_query(F.data == "completed")
async def show_completed_message(callback: types.CallbackQuery):
    if callback.from_user.id == ADMIN_ID:
        await callback.answer("✅ Bu zakaz allaqachon tayyor va mijozga xabar yuborilgan!", show_alert=True)
    else:
        await callback.answer("❌ Sizda admin huquqi yo'q!")

@dp.callback_query(F.data.startswith("accept_"))
async def accept_order(callback: types.CallbackQuery):
    if callback.from_user.id == ADMIN_ID:
        try:
            user_id = int(callback.data.split("_")[1])
            if user_id in temp_orders:
                await bot.send_message(
                    chat_id=user_id,
                    text="✅ <b>Admin zakazni qabul qildi!</b>\n\n"
                         "❓ <b>Aniq zakazni tasdiqlaysizmi?</b>\n\n"
                         "⚠️ Tasdiqlashdan keyin bekor qilib bo'lmaydi!",
                    reply_markup=get_final_confirmation_keyboard(),
                    parse_mode="HTML"
                )
                await callback.message.edit_caption(
                    caption=callback.message.caption + "\n\n✅ <b>Admin qabul qildi! Mijozdan yakuniy tasdiq kutilmoqda...</b>",
                    parse_mode="HTML"
                )
                await callback.answer("✅ Zakaz qabul qilindi! Mijozdan yakuniy tasdiq kutilmoqda.")
            else:
                await callback.answer("❌ Zakaz topilmadi!")
        except Exception as e:
            logging.error(f"Zakazni qabul qilishda xatolik: {e}")
            await callback.answer("❌ Xatolik yuz berdi!")
    else:
        await callback.answer("❌ Sizda admin huquqi yo'q!")

@dp.callback_query(F.data.startswith("reject_"))
async def reject_order(callback: types.CallbackQuery):
    if callback.from_user.id == ADMIN_ID:
        try:
            user_id = int(callback.data.split("_")[1])
            if user_id in temp_orders:
                del temp_orders[user_id]
                await bot.send_message(
                    chat_id=user_id,
                    text="❌ <b>Kechirasiz, zakazingiz rad etildi</b>\n\n"
                         "📞 Batafsil ma'lumot uchun bog'laning\n"
                         "🔄 Yangi zakaz berish uchun /start ni bosing",
                    reply_markup=get_main_keyboard(),
                    parse_mode="HTML"
                )
                await callback.message.edit_caption(
                    caption=callback.message.caption + "\n\n❌ <b>Admin rad etdi!</b>",
                    parse_mode="HTML"
                )
                await callback.answer("❌ Zakaz rad etildi!")
            else:
                await callback.answer("❌ Zakaz topilmadi!")
        except Exception as e:
            logging.error(f"Zakazni rad etishda xatolik: {e}")
            await callback.answer("❌ Xatolik yuz berdi!")
    else:
        await callback.answer("❌ Sizda admin huquqi yo'q!")

@dp.callback_query(F.data == "close_admin")
async def close_admin(callback: types.CallbackQuery):
    if callback.from_user.id == ADMIN_ID:
        await callback.message.delete()
    await callback.answer()

# Buyurtma jarayoni
@dp.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    register_user(message.from_user.id)
    print(f"Foydalanuvchi ID: {message.from_user.id}")
    print(f"Username: @{message.from_user.username}")
    
    await state.clear()
    await message.answer(
        "Assalomu alaykum! 👋\n\n"
        "📱 Telefon chexoli buyurtma qilish va admin bilan bog'lanish uchun kerakli bo'limni tanlang:",
        reply_markup=get_main_keyboard()
    )

# Asosiy menyu tugmalari
@dp.message(F.text == "🛒 Buyurtma berish")
async def start_order(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "📱 Telefon chexoli buyurtma qilish uchun brendni tanlang:",
        reply_markup=get_brand_keyboard()
    )
    await state.set_state(OrderState.waiting_for_brand)

@dp.message(F.text == "📞 Admin bilan aloqa")
async def contact_admin(message: types.Message):
    await message.answer(
        "📞 <b>Admin bilan aloqa</b>\n\n"
        "👤 <b>Admin:</b> Mirzayev Muhammadali\n"
        "📱 <b>Telefon:</b> <code>+998954414666</code>\n"
        "💬 <b>Telegram:</b> @Ali_Brandss\n\n"
        "📍 <b>Manzil:</b> Toshkent shahar, Chilonzor tumani\n\n"
        "🕐 <b>Ish vaqti:</b> Har kuni 08:00 dan 22:00 gacha\n\n"
        "💡 <b>Eslatma:</b> Iltimos, admin bilan faqat ish vaqtida bog'laning.",
        parse_mode="HTML"
    )

@dp.message(OrderState.waiting_for_brand)
async def process_brand(message: types.Message, state: FSMContext):
    if message.text == "📱 iPhone":
        await state.update_data(brand="iPhone")
        await message.answer("iPhone modelini tanlang:", reply_markup=get_model_keyboard(IPHONE_MODELS))
        await state.set_state(OrderState.waiting_for_model)
    elif message.text == "📱 Samsung":
        await state.update_data(brand="Samsung")
        await message.answer("Samsung modelini tanlang:", reply_markup=get_model_keyboard(SAMSUNG_MODELS))
        await state.set_state(OrderState.waiting_for_model)
    elif message.text == "🔙 Bosh menyu":
        await state.clear()
        await message.answer("Bosh menyu:", reply_markup=get_main_keyboard())
    else:
        await message.answer("Iltimos, faqat tugmalardan foydalaning! Brendni tanlang:", reply_markup=get_brand_keyboard())

@dp.message(OrderState.waiting_for_model)
async def process_model(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Brendni tanlang:", reply_markup=get_brand_keyboard())
        await state.set_state(OrderState.waiting_for_brand)
        return
    
    data = await state.get_data()
    brand = data.get('brand')
    
    if (brand == "iPhone" and message.text in IPHONE_MODELS) or (brand == "Samsung" and message.text in SAMSUNG_MODELS):
        await state.update_data(model=message.text)
        await message.answer("Qanday chexol xohlaysiz?", reply_markup=get_case_type_keyboard())
        await state.set_state(OrderState.waiting_for_case_type)
    else:
        models = IPHONE_MODELS if brand == "iPhone" else SAMSUNG_MODELS
        await message.answer("Iltimos, ro'yxatdan model tanlang:", reply_markup=get_model_keyboard(models))

@dp.message(OrderState.waiting_for_case_type)
async def process_case_type(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        data = await state.get_data()
        brand = data.get('brand')
        models = IPHONE_MODELS if brand == "iPhone" else SAMSUNG_MODELS
        await message.answer(f"{brand} modelini tanlang:", reply_markup=get_model_keyboard(models))
        await state.set_state(OrderState.waiting_for_model)
        return
    
    data = await state.get_data()
    brand = data.get('brand')
    model = data.get('model')
    
    if message.text == "🖼️ Rasimli (pechat bilan)":
        await state.update_data(case_type="Rasimli (pechat bilan)")
        price = get_price(brand, model, "Rasimli (pechat bilan)")
        await message.answer(
            f"💰 <b>Narx:</b> {price:,} so'm\n\n"
            "📄 <b>Muhim!</b> Chexolga uriladigan rasmni <b>FILE</b> ko'rinishida yuboring!\n\n"
            "📎 Rasm formatlar: JPG, PNG, GIF\n"
            "⚠️ Sifatga ta'sir qilmasligi uchun rasmni attachment (📎) orqali file sifatida yuboring.",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="HTML"
        )
        await state.set_state(OrderState.waiting_for_image)
    elif message.text == "🎨 Boshqa chexol tanlash":
        await state.update_data(case_type="Boshqa chexol tanlash")
        await message.answer("Siz tanlagan chexol rasmi yoki screenshot'ini yuboring:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(OrderState.waiting_for_custom_case)
    else:
        await message.answer("Iltimos, chexol turini tanlang:", reply_markup=get_case_type_keyboard())

# RASIMLI PECHAT BO'LIMI - FAQAT FILE FORMATDA QABUL QILADI
@dp.message(OrderState.waiting_for_image, F.document)
async def process_image_document(message: types.Message, state: FSMContext):
    allowed_image_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    
    if message.document.mime_type in allowed_image_types:
        await state.update_data(image_file_id=message.document.file_id, image_type="document")
        await message.answer("✅ Rasm fayli qabul qilindi!\n\n📍 Endi yashash manzilini yuboring:", reply_markup=get_location_keyboard())
        await state.set_state(OrderState.waiting_for_location)
    else:
        await message.answer(
            "❌ Iltimos, faqat rasm fayli yuboring!\n\n"
            "✅ Qo'llab-quvvatlanadigan formatlar:\n"
            "📎 JPG, PNG, GIF, WebP\n\n"
            "📱 Rasmni FILE ko'rinishida yuborish:\n"
            "1. Rasmni tanlang\n"
            "2. 'Attach' yoki '📎' tugmasini bosing\n"
            "3. 'Document' yoki 'File' sifatida yuboring"
        )

@dp.message(OrderState.waiting_for_image)
async def process_wrong_image_type(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Qanday chexol xohlaysiz?", reply_markup=get_case_type_keyboard())
        await state.set_state(OrderState.waiting_for_case_type)
    elif message.photo:
        await message.answer(
            "❌ Iltimos, rasmni FILE ko'rinishida yuboring!\n\n"
            "📱 FILE sifatida yuborish:\n"
            "1. Rasmni tanlang\n"
            "2. 'Attach' yoki '📎' tugmasini bosing\n"
            "3. 'Document' yoki 'File' sifatida yuboring\n\n"
            "⚠️ Oddiy rasm emas, FILE ko'rinishida yuborish kerak!"
        )
    else:
        await message.answer(
            "❌ Iltimos, rasm faylini FILE ko'rinishida yuboring!\n\n"
            "✅ Qo'llab-quvvatlanadigan formatlar:\n"
            "📎 JPG, PNG, GIF, WebP\n\n"
            "📱 FILE sifatida yuborish usuli:\n"
            "1. Rasmni tanlang\n"
            "2. 'Attach' yoki '📎' tugmasini bosing\n"
            "3. 'Document' sifatida yuboring"
        )

# BOSHQA DIZAYN BO'LIMI - HAR QANDAY RASM FORMATINI QABUL QILADI

# Oddiy rasm (photo) formatini qabul qilish
@dp.message(OrderState.waiting_for_custom_case, F.photo)
async def process_custom_case_image(message: types.Message, state: FSMContext):
    await state.update_data(image_file_id=message.photo[-1].file_id, image_type="photo")
    await message.answer("✅ Chexol rasmi qabul qilindi!\n\n📍 Endi yashash manzilini yuboring:", reply_markup=get_location_keyboard())
    await state.set_state(OrderState.waiting_for_location)

# File (document) formatini qabul qilish
@dp.message(OrderState.waiting_for_custom_case, F.document)
async def process_custom_case_document(message: types.Message, state: FSMContext):
    if message.document.mime_type and message.document.mime_type.startswith('image/'):
        await state.update_data(image_file_id=message.document.file_id, image_type="document")
        await message.answer("✅ Chexol rasmi qabul qilindi!\n\n📍 Endi yashash manzilini yuboring:", reply_markup=get_location_keyboard())
        await state.set_state(OrderState.waiting_for_location)
    else:
        await message.answer("❌ Iltimos, faqat rasm fayli yuboring!\n\n✅ Qo'llab-quvvatlanadigan formatlar: JPG, PNG, GIF, WebP")

# Noto'g'ri format yuborilgan holat
@dp.message(OrderState.waiting_for_custom_case)
async def process_wrong_custom_case(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Qanday chexol xohlaysiz?", reply_markup=get_case_type_keyboard())
        await state.set_state(OrderState.waiting_for_case_type)
    else:
        await message.answer(
            "❌ Iltimos, chexol rasmi yoki screenshot'ini yuboring!\n\n"
            "✅ Qo'llab-quvvatlanadigan formatlar: JPG, PNG, GIF, WebP\n"
            "📷 Oddiy rasm yoki 📎 File sifatida yuborish mumkin"
        )

@dp.message(OrderState.waiting_for_location, F.location)
async def process_location(message: types.Message, state: FSMContext):
    location_data = {
        "latitude": message.location.latitude,
        "longitude": message.location.longitude,
        "text": f"Lat: {message.location.latitude}, Lon: {message.location.longitude}"
    }
    await state.update_data(location=location_data)
    await message.answer("✅ Manzil qabul qilindi!\n\n📞 Endi telefon raqamingizni yuboring:", reply_markup=get_contact_keyboard())
    await state.set_state(OrderState.waiting_for_contact)

@dp.message(OrderState.waiting_for_location)
async def process_wrong_location(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        data = await state.get_data()
        case_type = data.get('case_type')
        
        if case_type == "Rasimli (pechat bilan)":
            await message.answer("📄 Chexolga uriladigan rasmni FILE ko'rinishida yuboring:", reply_markup=ReplyKeyboardRemove())
            await state.set_state(OrderState.waiting_for_image)
        elif case_type == "Boshqa chexol tanlash":
            await message.answer("Siz tanlagan chexol rasmi yoki screenshot'ini yuboring:", reply_markup=ReplyKeyboardRemove())
            await state.set_state(OrderState.waiting_for_custom_case)
        else:
            await message.answer("Qanday chexol xohlaysiz?", reply_markup=get_case_type_keyboard())
            await state.set_state(OrderState.waiting_for_case_type)
    else:
        await message.answer("❌ Iltimos, manzilni tugma orqali yuboring! 📍", reply_markup=get_location_keyboard())

@dp.message(OrderState.waiting_for_contact, F.contact)
async def process_contact(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(phone_number=message.contact.phone_number)
    
    brand = data.get('brand')
    model = data.get('model')
    case_type = data.get('case_type')
    location_data = data.get('location', {})
    location_text = location_data.get('text', 'Manzil yuborilmagan')
    price = get_price(brand, model, case_type)
    full_name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()
    
    confirmation_text = (
        "📋 <b>Zakaz ma'lumotlari:</b>\n\n"
        f"👤 <b>Ism:</b> {full_name}\n"
        f"📞 <b>Telefon:</b> {message.contact.phone_number}\n"
        f"📍 <b>Manzil:</b> {location_text}\n\n"
        f"📱 <b>Model:</b> {model}\n"
        f"🎨 <b>Chexol turi:</b> {case_type}\n"
        f"💰 <b>Narx:</b> {price:,} so'm\n\n"
        "⚠️ <b>Diqqat!</b> Zakazni tasdiqlashdan keyin uni bekor qilib bo'lmaydi!\n\n"
        "Zakazni tasdiqlaysizmi?"
    )
    
    await message.answer(confirmation_text, reply_markup=get_confirmation_keyboard(), parse_mode="HTML")
    await state.set_state(OrderState.waiting_for_confirmation)

@dp.message(OrderState.waiting_for_confirmation)
async def process_confirmation(message: types.Message, state: FSMContext):
    if message.text == "✅ Zakazni tasdiqlash":
        data = await state.get_data()
        user_id = message.from_user.id
        
        brand = data.get('brand')
        model = data.get('model')
        case_type = data.get('case_type')
        location_data = data.get('location', {})
        location_text = location_data.get('text', 'Manzil yuborilmagan')
        phone_number = data.get('phone_number')
        username = f"@{message.from_user.username}" if message.from_user.username else "Username yo'q"
        full_name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()
        image_file_id = data.get('image_file_id')
        image_type = data.get('image_type', 'photo')
        price = get_price(brand, model, case_type)
        
        temp_orders[user_id] = {
            "user_id": user_id,
            "username": username,
            "full_name": full_name,
            "phone_number": phone_number,
            "location": location_data,
            "brand": brand,
            "model": model,
            "case_type": case_type,
            "price": price,
            "image_file_id": image_file_id,
            "image_type": image_type,
            "has_image": bool(image_file_id)
        }
        
        admin_message = (
            "🔄 <b>Yangi zakaz tasdiq kutmoqda!</b>\n\n"
            f"👤 <b>Mijoz:</b> {full_name}\n"
            f"🆔 <b>User ID:</b> <code>{user_id}</code>\n"
            f"👤 <b>Username:</b> {username}\n"
            f"📞 <b>Telefon:</b> <code>{phone_number}</code>\n"
            f"📍 <b>Manzil:</b> {location_text}\n\n"
            f"📱 <b>Telefon modeli:</b> {model}\n"
            f"🎨 <b>Chexol turi:</b> {case_type}\n"
            f"💰 <b>Narx:</b> {price:,} so'm\n\n"
            f"📅 <b>Buyurtma vaqti:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
            "❓ <b>Bu zakazni qabul qilasizmi?</b>"
        )
        
        try:
            if image_file_id:
                if image_type == "document":
                    await bot.send_document(
                        chat_id=ADMIN_ID,
                        document=image_file_id,
                        caption=admin_message,
                        parse_mode="HTML",
                        reply_markup=get_admin_confirmation_keyboard(user_id)
                    )
                else:
                    await bot.send_photo(
                        chat_id=ADMIN_ID,
                        photo=image_file_id,
                        caption=admin_message,
                        parse_mode="HTML",
                        reply_markup=get_admin_confirmation_keyboard(user_id)
                    )
            else:
                await bot.send_message(
                    chat_id=ADMIN_ID,
                    text=admin_message,
                    parse_mode="HTML",
                    reply_markup=get_admin_confirmation_keyboard(user_id)
                )
            
            if location_data.get('latitude') and location_data.get('longitude'):
                await bot.send_location(
                    chat_id=ADMIN_ID,
                    latitude=location_data['latitude'],
                    longitude=location_data['longitude']
                )
                await bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"📍 <b>Yuqoridagi zakaz manzili</b>\n👤 Mijoz: {full_name}",
                    parse_mode="HTML"
                )
            
            await message.answer(
                "⏳ <b>Zakazingiz yuborildi!</b>\n\n"
                "🔄 Admin tomonidan ko'rib chiqilmoqda...\n"
                "📱 Tez orada javob beramiz!\n\n"
                "⚠️ Zakazni bekor qilish uchun /start buyrug'ini yuboring.",
                reply_markup=ReplyKeyboardRemove(),
                parse_mode="HTML"
            )
            await state.clear()
            
        except Exception as e:
            logging.error(f"Admin xabarini yuborishda xatolik: {e}")
            await message.answer("❌ Xatolik yuz berdi. Qayta urinib ko'ring.\n/start", reply_markup=ReplyKeyboardRemove())
            await state.clear()
            
    elif message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Zakaz bekor qilindi.\n\n🔄 Yangi zakaz berish uchun menyudan foydalaning.", reply_markup=get_main_keyboard())
        
    elif message.text == "🔙 Orqaga":
        await message.answer("📞 Telefon raqamingizni yuboring:", reply_markup=get_contact_keyboard())
        await state.set_state(OrderState.waiting_for_contact)
    else:
        await message.answer("Iltimos, tugmalardan foydalaning:", reply_markup=get_confirmation_keyboard())

@dp.message(OrderState.waiting_for_contact)
async def process_wrong_contact(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("📍 Yashash manzilini yuboring:", reply_markup=get_location_keyboard())
        await state.set_state(OrderState.waiting_for_location)
    else:
        await message.answer("❌ Iltimos, telefon raqamingizni tugma orqali yuboring! 📞", reply_markup=get_contact_keyboard())

# Yakuniy tasdiqlash
@dp.message()
async def handle_final_confirmation_and_general(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    # Yakuniy tasdiqlash jarayoni
    if user_id in temp_orders and message.text in ["✅ Ha, aniq tasdiqlyman", "❌ Yo'q, bekor qilaman"]:
        if message.text == "✅ Ha, aniq tasdiqlyman":
            try:
                order_data = temp_orders[user_id]
                add_order(order_data)
                del temp_orders[user_id]
                
                await bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"🎉 <b>Zakaz yakuniy tasdiqlandi!</b>\n\n"
                         f"👤 <b>Mijoz:</b> {order_data['full_name']}\n"
                         f"📱 <b>Model:</b> {order_data['model']}\n"
                         f"💰 <b>Narx:</b> {order_data['price']:,} so'm\n\n"
                         "✅ Zakaz ro'yxatga qo'shildi!",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="✅ Zakaz tayyor", callback_data=f"ready_{user_id}")]
                    ])
                )
                
                price = order_data['price']
                confirmation_text = "🎉 <b>Zakaz yakuniy tasdiqlandi!</b>\n\n"
                
                if price > 0:
                    confirmation_text += f"💰 <b>Narx:</b> {price:,} so'm\n\n"
                    confirmation_text += "💳 <b>To'lov uchun karta ma'lumotlari:</b>\n"
                    confirmation_text += "💳 Karta egasi: Mirzayev Muhammadali\n"
                    confirmation_text += "🔢 Karta raqami: <code>5614682215991664</code>\n\n"
                    confirmation_text += "✅ To'lov qilganingizdan so'ng screenshot yuboring.\n\n"
                
                confirmation_text += "📅 Zakaz 3 kun ichida tayyor bo'ladi\n\n"
                confirmation_text += "🔄 Yangi buyurtma berish uchun /start ni bosing."
                
                await message.answer(confirmation_text, reply_markup=get_main_keyboard(), parse_mode="HTML")
                
            except Exception as e:
                logging.error(f"Yakuniy tasdiqlashda xatolik: {e}")
                await message.answer("❌ Xatolik yuz berdi. /start ni bosing.", reply_markup=get_main_keyboard())
                
        elif message.text == "❌ Yo'q, bekor qilaman":
            if user_id in temp_orders:
                del temp_orders[user_id]
            
            await message.answer("❌ Zakaz bekor qilindi.\n\n🔄 Yangi zakaz berish uchun menyudan foydalaning.", reply_markup=get_main_keyboard())
            
            await bot.send_message(
                chat_id=ADMIN_ID,
                text=f"❌ <b>Mijoz zakazni bekor qildi</b>\n\n👤 User ID: <code>{user_id}</code>",
                parse_mode="HTML"
            )
    else:
        # Oddiy xabarlar uchun javob
        current_state = await state.get_state()
        if current_state is None:
            await message.answer("🔄 Buyurtma berish uchun /start ni bosing.\n👨‍💼 Admin bo'lsangiz /admin ni bosing.", reply_markup=get_main_keyboard())
        # Agar foydalanuvchi biror state ichida bo'lsa, hech narsa qilmaymiz - tegishli handler ishlaydi

# Bot ishga tushirish
async def main():
    print("Bot ishga tushmoqda...")
    print(f"Ma'lumotlar fayli: {DATA_FILE}")
    print(f"Hozirgi foydalanuvchilar soni: {len(bot_data['users'])}")
    print(f"Hozirgi zakazlar soni: {len(bot_data['orders'])}")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    asyncio.run(main())