# -*- coding: utf-8 -*-

import time
import requests
import hashlib
import json
import re
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

# ================== CONFIG ==================
API_URL = "http://147.135.212.197/crapi/st/viewstats?token=RVJVRkVBUzRrd2OCgJOKaGKBjVxJZ49gioRsSVlyh0JmhZlghGJ2aw"
BOT_TOKEN = "8239921544:AAEOqXAOeftRKfdKA27Z1_TvydW9MRwQ-G4"
CHAT_ID = "-1003458386292"
CHANNEL_URL = "https://t.me/+w0lkolNArRc4ZDc0"

POLL_INTERVAL = 15
TIMEOUT = 120
HASH_FILE = "sent_hashes.json"

# ================== SESSION ==================
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Linux; Android 10)",
    "Accept": "*/*",
    "Connection": "keep-alive"
})

bot = Bot(token=BOT_TOKEN)

# ================== LOAD HASHES ==================
try:
    with open(HASH_FILE, "r") as f:
        sent_hashes = set(json.load(f))
except:
    sent_hashes = set()

def save_hashes():
    with open(HASH_FILE, "w") as f:
        json.dump(list(sent_hashes), f)

# ================== COUNTRY MAP ==================
COUNTRIES = {
    "234": ("🇳🇬", "NG"),
    "92":  ("🇵🇰", "PK"),
    "93":  ("🇦🇫", "AF"),
    "58":  ("🇻🇪", "VE"),
    "670": ("🇹🇱", "TL"),
    "269": ("🇰🇲", "KM"),
}

def detect_country(number):
    for code in sorted(COUNTRIES.keys(), key=len, reverse=True):
        if number.startswith(code):
            return COUNTRIES[code]
    return ("🌐", "UN")

# ================== PLATFORM SHORT ==================
PLATFORM_SHORT = {
    "WhatsApp": "WP",
    "WhatsApp Business": "WP",
    "Facebook": "FB",
    "Telegram": "TG",
    "Instagram": "IG",
    "Twitter": "TW",
    "Google": "GO",
}

# ================== OTP EXTRACT ==================
def extract_otp(text):
    text = str(text).replace("n", "\n")
    match = re.search(r'\b(\d{3,4}[- ]\d{3,4}|\d{4,8})\b', text)
    return match.group(0) if match else None

# ================== HASH ==================
def make_hash(item):
    platform, number, text, _ = item
    return hashlib.md5(f"{platform}|{number}|{text}".encode()).hexdigest()

# ================== MASK NUMBER ==================
def mask_number(number):
    if len(number) >= 7:
        return f"{number[:3]}****{number[-4:]}"
    return number

# ================== MESSAGE FORMAT ==================
def format_message(item):
    platform, number, text, timestamp = item

    otp = extract_otp(text)
    if not otp:
        return None  # Skip if no OTP

    flag, country_short = detect_country(str(number))
    platform_short = PLATFORM_SHORT.get(platform, platform[:2].upper())
    masked = mask_number(str(number))

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 𝗖𝗛𝗔𝗡𝗡𝗘𝗟", url=CHANNEL_URL)]
    ])

    msg = (
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"{flag} <b>{country_short}</b>  <b>{platform_short}</b> {masked}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"    ⚔️         <code>{otp}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━"
    )

    return msg, keyboard

# ================== MAIN LOOP ==================
print("✅ VIP OTP BOT STARTED WITH BUTTONS")

while True:
    try:
        r = session.get(API_URL, timeout=TIMEOUT)
        data = r.json()

        if not isinstance(data, list):
            time.sleep(POLL_INTERVAL)
            continue

        for item in data:
            if not isinstance(item, list) or len(item) < 4:
                continue

            h = make_hash(item)
            if h in sent_hashes:
                continue

            result = format_message(item)
            if not result:
                continue

            msg, keyboard = result

            bot.send_message(
                chat_id=CHAT_ID,
                text=msg,
                parse_mode="HTML",
                reply_markup=keyboard,
                disable_notification=True
            )

            sent_hashes.add(h)
            print("✅ OTP Forwarded with button")

        if len(sent_hashes) > 5000:
            sent_hashes.clear()

        save_hashes()

    except Exception as e:
        print("⚠️ ERROR:", e)

    time.sleep(POLL_INTERVAL)
