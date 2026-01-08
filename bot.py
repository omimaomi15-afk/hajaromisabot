import random
import requests
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ChatMemberHandler,
)

# =========================
# 🔐 الإعدادات
# =========================
TOKEN = os.getenv("TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
CITY = "Algiers"
COUNTRY = "DZ"
TIMEZONE = "Africa/Algiers"
GROUP_NAME = "🇩🇿фGosRaф🇩🇿"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # الرابط الكامل للـ Render service مع HTTPS

# =========================
# 🕌 نصوص الأذان
# =========================
ADHAN_MESSAGES = {
    "Fajr": "**🕌 أذان الفجر**\n**حان الآن موعد أذان الفجر بالجزائر**\nقوم يا قلبي صلّي 🤍",
    "Dhuhr": "**🕌 أذان الظهر**\n**حان الآن موعد أذان الظهر بالجزائر**\nصلاتك خير من الدنيا 🌸",
    "Asr": "**🕌 أذان العصر**\n**حان الآن موعد أذان العصر بالجزائر**\nما تنساش صلاتك 🤲",
    "Maghrib": "**🕌 أذان المغرب**\n**حان الآن موعد أذان المغرب بالجزائر**\nقوموا صلوووا واذكروا الله 🍃",
    "Isha": "**🕌 أذان العشاء**\n**حان الآن موعد أذان العشاء بالجزائر**\nاختم نهارك بالصلاة 🌙"
}

# =========================
# 👋 الترحيب
# =========================
WELCOME_MESSAGES = [
    """{name}
😂🧕 الحاجة روميصة ترحّب بيك! 🧕😂
يااااا مرحبااااااااااا 👀
آه لا لا… استنى… وين راني؟ 🤔
آه صح صح! راهو/راهي عضو جديد دخل لجروبنا {group} 🎉
مرحبا بيك يا وليدي/بنيّتي 🤍
اقعد اقعد… جيب/جيبي كرسي 🪑
تحب/تحبي قهوة ☕ ولا ننساك ومنرجعلك بعد ساعتين؟ 😂
راك بين ناسك،
ضحك 🤣، قصرة 🗣، نقاشات 🔥
وإذا شفتني نعاود نفس الهضرة 3 مرات… سامحني 😌
الزهايمر دار حالة اليوم 🧠💨
المهم:
✋ احترم الناس
👀 اقرا/اقراي القوانين (عند عمك الشرطي)👈 /rules
😂 واضحك بلا حدود
— الحاجة روميصة 🧕💚""",
   """{name} 😎 واو! عضو جديد وصل!
🤩 مرحبا بيك في {group} 
☕ اجلس، خذ قهوة، وخلينا نضحك شوية 😆
👀 اقرا/اقراي القوانين (عند عمك الشرطي)👈 /rules
— الحاجة روميصة 🧕""",
    """{name} 🤩 أهلاً بك!
🌟 مرحبا في {group} 
☕ خذ قهوتك، استرخي وخلينا نضحك سوا 😆
👀 اقرا/اقراي القوانين (عند عمك الشرطي)👈 /rules
— الحاجة روميصة 🧕"""
]

# =========================
# 🕌 جلب أوقات الصلاة
# =========================
def get_prayer_times():
    url = f"https://api.aladhan.com/v1/timingsByCity?city={CITY}&country={COUNTRY}&method=3"
    try:
        data = requests.get(url, timeout=10).json()
        timings = data["data"]["timings"]
        return {
            "Fajr": timings["Fajr"],
            "Dhuhr": timings["Dhuhr"],
            "Asr": timings["Asr"],
            "Maghrib": timings["Maghrib"],
            "Isha": timings["Isha"]
        }
    except Exception as e:
        print("⚠️ خطأ جلب الأذان:", e)
        return {}

# =========================
# 🕌 إرسال الأذان مع صورة
# =========================
async def send_adhan(app, prayer):
    try:
        image_path = os.path.join("images", f"{prayer}.png")
        await app.bot.send_photo(
            chat_id=CHAT_ID,
            photo=open(image_path, "rb"),
            caption=ADHAN_MESSAGES[prayer]
        )
        print(f"✅ أُرسل أذان {prayer}")
    except Exception as e:
        print(f"⚠️ خطأ أذان {prayer}:", e)

# =========================
# 🕋 الصلاة على النبي
# =========================
async def send_salat(app):
    try:
        image_path = os.path.join("images", "salat.png")
        await app.bot.send_photo(
            chat_id=CHAT_ID,
            photo=open(image_path, "rb"),
            caption="اللهم صل وسلم وبارك على نبينا محمد ﷺ 🌹"
        )
        print("✅ الصلاة على النبي أُرسلت مع صورة")
    except Exception as e:
        print("⚠️ خطأ الصلاة:", e)

# =========================
# 👋 الترحيب بالاعضاء
# =========================
async def welcome_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    old_status = update.chat_member.old_chat_member.status
    new_status = update.chat_member.new_chat_member.status
    if old_status in ("left", "kicked") and new_status == "member":
        user = update.chat_member.new_chat_member.user
        text = random.choice(WELCOME_MESSAGES).format(name=user.full_name, group=GROUP_NAME)
        await update.effective_chat.send_message(text)
        print(f"👋 تم الترحيب بـ {user.full_name}")

# =========================
# ▶️ أمر /start
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("🧕 الحاجة روميصة راهي تخدم 🤍")

# =========================
# 🔄 جدولة الأذان والصلاة
# =========================
async def on_startup(app):
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)
    await send_salat(app)

    prayers = get_prayer_times()
    for prayer, time_str in prayers.items():
        hour, minute = map(int, time_str.split(":"))
        scheduler.add_job(send_adhan, "cron", hour=hour, minute=minute, args=[app, prayer])

    scheduler.add_job(send_salat, "interval", hours=1, args=[app])
    scheduler.start()
    print("🟢 البوت يعمل بثبات")

# =========================
# 🚀 Webhook التشغيل
# =========================
async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(ChatMemberHandler(welcome_member, ChatMemberHandler.CHAT_MEMBER))
    await on_startup(app)

    # إعداد Webhook
    await app.bot.set_webhook(WEBHOOK_URL)
    print(f"🟢 البوت جاهز على Webhook: {WEBHOOK_URL}")

    # لا حاجة لـ run_polling في Webhook
    await app.initialize()
    await app.start()
    await app.updater.start_polling()  # Polling داخلي فقط لأجل scheduler
    await app.updater.wait_closed()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
