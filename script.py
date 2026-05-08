import streamlit as st
import time
import difflib
import json
import os
import requests
import hashlib
from datetime import datetime
import streamlit.components.v1 as components
from deep_translator import GoogleTranslator
try:
    import payment_processor
except ImportError:
    pass

# --- 1. RESPONSIVE PAGE SETUP ---
try:
    st.set_page_config(page_title="Smart Menu", page_icon="🍔", layout="wide", initial_sidebar_state="expanded")
except:
    pass

# --- DATABASE SYNC LOGIC ---
DB_FILE = "orders_db.json"
MENU_DB = "menu_db.json"

def send_order_to_kitchen(cart_items, total_amount, payment_method):
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f: json.dump([], f)

    try:
        with open(DB_FILE, "r") as f:
            orders = json.load(f)
    except:
        orders = []

    new_order = {
        "order_id": f"ORD_{int(time.time())}",
        "time": datetime.now().strftime("%H:%M"),
        "items": cart_items,
        "total": total_amount,
        "payment": payment_method,
        "status": "Pending"
    }
    orders.append(new_order)
    with open(DB_FILE, "w") as f:
        json.dump(orders, f)


# --- 2. PREMIUM CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');
    html, body, [class*="css"], * { font-family: 'Outfit', sans-serif !important; }
    .stApp { background-color: #f8f9fc !important; background-image: radial-gradient(#e5e7eb 1px, transparent 1px) !important; background-size: 20px 20px !important; }
    .gradient-text { background: linear-gradient(45deg, #E23744, #ff6b6b, #E23744); background-size: 200% auto; color: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: gradient 3s linear infinite; font-weight: 800; text-align: center; letter-spacing: -1px; }

    [data-testid="stVerticalBlockBorderWrapper"] { border-radius: 24px !important; background-color: rgba(255, 255, 255, 0.9) !important; backdrop-filter: blur(10px); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03) !important; border: 1px solid rgba(255, 255, 255, 0.5) !important; padding: 15px !important; transition: all 0.3s ease; }
    [data-testid="stVerticalBlockBorderWrapper"]:hover { transform: translateY(-8px) scale(1.02); box-shadow: 0 20px 40px rgba(226, 55, 68, 0.1) !important; border-color: rgba(226, 55, 68, 0.2) !important; }

    [data-testid="stImage"] img { border-radius: 18px !important; transition: transform 0.5s ease; height: 180px !important; width: 100% !important; object-fit: cover !important; background-color: #eee; }

    .stButton > button { border-radius: 30px !important; font-weight: 700 !important; background-color: #ffffff !important; color: #E23744 !important; border: 2px solid #E23744 !important; transition: all 0.3s ease !important; padding: 8px 24px !important; text-transform: uppercase; }
    .stButton > button:hover { background-color: #E23744 !important; color: white !important; }
    button[data-testid="baseButton-primary"] { background: linear-gradient(45deg, #E23744, #ff4757) !important; color: white !important; border: none !important; }
    [data-testid="stForm"] { background-color: rgba(255, 255, 255, 0.8); backdrop-filter: blur(12px); border-radius: 30px; border: 1px solid rgba(255,255,255,0.6); box-shadow: 0 8px 32px rgba(0,0,0,0.05); padding: 20px 25px 5px 25px; }
    .stTextInput input { border-radius: 20px !important; background-color: #ffffff !important; border: 2px solid #f1f3f5 !important; font-weight: 600 !important; color: #333 !important; padding: 12px 20px !important; transition: border-color 0.3s ease; }
    .stTextInput input:focus { border-color: #E23744 !important; box-shadow: none !important; }
    div[role="radiogroup"] { display: flex; flex-wrap: wrap; gap: 12px; justify-content: center; padding: 20px 0; }
    div[role="radiogroup"] label { background-color: white !important; padding: 12px 25px !important; border-radius: 40px !important; border: 2px solid #f1f3f5 !important; box-shadow: 0 4px 10px rgba(0,0,0,0.02) !important; cursor: pointer; transition: all 0.3s ease; }
    div[role="radiogroup"] label p { color: #495057 !important; font-weight: 700 !important; font-size: 15px !important; margin: 0 !important; }
    div[role="radiogroup"] label:hover, div[role="radiogroup"] label[data-checked="true"] { border-color: #E23744 !important; background-color: #fff0f1 !important; transform: translateY(-2px); box-shadow: 0 6px 15px rgba(226, 55, 68, 0.15) !important; }
    div[role="radiogroup"] label[data-checked="true"] p { color: #E23744 !important; }
    [data-testid="stSidebar"] { background: rgba(255, 255, 255, 0.7) !important; backdrop-filter: blur(20px); border-right: 1px solid rgba(255,255,255,0.5); }
    </style>
""", unsafe_allow_html=True)

# --- 3. FULL UI DICTIONARY ---
UI_TEXT = {
    "EN": {"title": "SMART MENU", "subtitle": "Gourmet flavors, delivered directly to your screen.", "search": "Search for cravings...", "btn_search": "Find", "add": "Add to Tray", "cart": "🛒 Your Tray", "empty": "Your tray is looking a bit empty!", "items": "Items", "total": "Total", "checkout": "Proceed to Pay", "checkout_title": "Checkout", "amount_pay": "Amount to Pay", "pay_method": "Select Payment Method", "upi": "UPI", "card": "Credit/Debit Card", "cash": "Cash at Counter", "pay_now": "Pay Now", "place_order": "Place Order Now", "back_cart": "← Back to Cart", "status": "⏳ Live Status", "s1": "👨‍🍳 Chefs are chopping ingredients...", "s2": "🔥 Cooking your delicious meal...", "s3": "🛵 Packing your order!", "s4": "🎉 Order Ready & Dispatched!", "s5": "🎉 Your order is on its way!", "s6": "Kitchen is resting. Waiting for orders.", "feedback": "⭐ Your Experience", "rate_exp": "Rate your experience:", "tell_more": "Tell us more (Optional):", "submit_feed": "Submit Feedback"},
    "HI": {"title": "स्मार्ट मेनू", "subtitle": "स्वादिष्ट व्यंजन, सीधे आपकी स्क्रीन पर।", "search": "व्यंजन खोजें...", "btn_search": "खोजें", "add": "ट्रे में जोड़ें", "cart": "🛒 आपकी ट्रे", "empty": "आपकी ट्रे खाली है!", "items": "आइटम", "total": "कुल", "checkout": "भुगतान करें", "checkout_title": "चेकआउट", "amount_pay": "भुगतान राशि", "pay_method": "भुगतान विधि चुनें", "upi": "यूपीआई (UPI)", "card": "क्रेडिट/डेबिट कार्ड", "cash": "काउंटर पर नकद", "pay_now": "अभी भुगतान करें", "place_order": "अभी ऑर्डर दें", "back_cart": "← ट्रे पर वापस जाएँ", "status": "⏳ लाइव स्थिति", "s1": "👨‍🍳 शेफ सामग्री काट रहे हैं...", "s2": "🔥 आपका स्वादिष्ट भोजन पक रहा है...", "s3": "🛵 आपका ऑर्डर पैक हो रहा है!", "s4": "🎉 ऑर्डर तैयार और भेज दिया गया!", "s5": "🎉 आपका ऑर्डर रास्ते में है!", "s6": "रसोई बंद है। ऑर्डर की प्रतीक्षा है।", "feedback": "⭐ आपका अनुभव", "rate_exp": "अपने अनुभव को रेट करें:", "tell_more": "हमें और बताएं (वैकल्पिक):", "submit_feed": "प्रतिक्रिया जमा करें"},
    "KN": {"title": "ಸ್ಮಾರ್ಟ್ ಮೆನು", "subtitle": "ರುಚಿಯಾದ ಊಟ, ನೇರವಾಗಿ ನಿಮ್ಮ ಪರದೆಗೆ.", "search": "ಹುಡುಕಿ...", "btn_search": "ಹುಡುಕಿ", "add": "ಸೇರಿಸಿ", "cart": "🛒 ನಿಮ್ಮ ಟ್ರೇ", "empty": "ನಿಮ್ಮ ಟ್ರೇ ಖಾಲಿಯಾಗಿದೆ!", "items": "ವಸ್ತುಗಳು", "total": "ಒಟ್ಟು", "checkout": "ಪಾವತಿಸಲು ಮುಂದುವರಿಯಿರಿ", "checkout_title": "ಚೆಕ್ಔಟ್", "amount_pay": "ಪಾವತಿಸಬೇಕಾದ ಮೊತ್ತ", "pay_method": "ಪಾವತಿ ವಿಧಾನವನ್ನು ಆಯ್ಕೆಮಾಡಿ", "upi": "ಯುಪಿಐ (UPI)", "card": "ಕ್ರೆಡಿಟ್/ಡೆಬಿಟ್ ಕಾರ್ಡ್", "cash": "ಕೌಂಟರ್‌ನಲ್ಲಿ ನಗದು", "pay_now": "ಈಗ ಪಾವತಿಸಿ", "place_order": "ಈಗ ಆದೇಶಿಸಿ", "back_cart": "← ಟ್ರೇಗೆ ಹಿಂತಿರುಗಿ", "status": "⏳ ಲೈವ್ ಸ್ಥಿತಿ", "s1": "👨‍🍳 ಬಾಣಸಿಗರು ಪದಾರ್ಥಗಳನ್ನು ಕತ್ತರಿಸುತ್ತಿದ್ದಾರೆ...", "s2": "🔥 ನಿಮ್ಮ ರುಚಿಕರವಾದ ಊಟ ತಯಾರಾಗುತ್ತಿದೆ...", "s3": "🛵 ನಿಮ್ಮ ಆದೇಶವನ್ನು ಪ್ಯಾಕ್ ಮಾಡಲಾಗುತ್ತಿದೆ!", "s4": "🎉 ಆದೇಶ ಸಿದ್ಧವಾಗಿದೆ ಮತ್ತು ರವಾನಿಸಲಾಗಿದೆ!", "s5": "🎉 ನಿಮ್ಮ ಆದೇಶ ದಾರಿಯಲ್ಲಿದೆ!", "s6": "ಅಡುಗೆಮನೆ ವಿಶ್ರಾಂತಿ ಪಡೆಯುತ್ತಿದೆ. ಆದೇಶಗಳಿಗಾಗಿ ಕಾಯಲಾಗುತ್ತಿದೆ.", "feedback": "⭐ ನಿಮ್ಮ ಅನುಭವ", "rate_exp": "ನಿಮ್ಮ ಅನುಭವವನ್ನು ರೇಟ್ ಮಾಡಿ:", "tell_more": "ನಮಗೆ ಇನ್ನಷ್ಟು ತಿಳಿಸಿ (ಐಚ್ಛಿಕ):", "submit_feed": "ಪ್ರತಿಕ್ರಿಯೆ ಸಲ್ಲಿಸಿ"},
    "TA": {"title": "ஸ்மார்ட் மெனு", "subtitle": "சுவையான உணவுகள், நேரடியாக உங்கள் திரைக்கு.", "search": "தேடு...", "btn_search": "தேடு", "add": "சேர்க்க", "cart": "🛒 உங்கள் தட்டு", "empty": "உங்கள் தட்டு காலியாக உள்ளது!", "items": "பொருட்கள்", "total": "மொத்தம்", "checkout": "பணம் செலுத்த தொடரவும்", "checkout_title": "வெளியேறு", "amount_pay": "செலுத்த வேண்டிய தொகை", "pay_method": "கட்டண முறையைத் தேர்ந்தெடுக்கவும்", "upi": "யுபிஐ (UPI)", "card": "கிரெடிட்/டெபிட் கார்டு", "cash": "கவுண்டரில் பணம்", "pay_now": "இப்போது பணம் செலுத்துங்கள்", "place_order": "இப்போது ஆர்டர் செய்", "back_cart": "← தட்டுக்குத் திரும்பு", "status": "⏳ நேரடி நிலை", "s1": "👨‍🍳 சமையல்காரர்கள் பொருட்களை வெட்டுகிறார்கள்...", "s2": "🔥 உங்கள் சுவையான உணவு தயாராகிறது...", "s3": "🛵 உங்கள் ஆர்டர் பேக் செய்யப்படுகிறது!", "s4": "🎉 ஆர்டர் தயார் & அனுப்பப்பட்டது!", "s5": "🎉 உங்கள் ஆர்டர் வழியில் உள்ளது!", "s6": "சமையலறை ஓய்வெடுக்கிறது. ஆர்டர்களுக்காக காத்திருக்கிறது.", "feedback": "⭐ உங்கள் அனுபவம்", "rate_exp": "உங்கள் அனுபவத்தை மதிப்பிடுங்கள்:", "tell_more": "மேலும் சொல்லுங்கள்:", "submit_feed": "கருத்தை சமர்ப்பிக்கவும்"},
    "TE": {"title": "స్మార్ట్ మెను", "subtitle": "రుచికరమైన భోజనం, నేరుగా మీ స్క్రీన్‌పైకి.", "search": "వెతకండి...", "btn_search": "వెతకండి", "add": "జోడించు", "cart": "🛒 మీ ట్రే", "empty": "మీ ట్రే ఖాళీగా ఉంది!", "items": "వస్తువులు", "total": "మొత్తం", "checkout": "చెల్లించడానికి కొనసాగండి", "checkout_title": "చెక్అవుట్", "amount_pay": "చెల్లించాల్సిన మొత్తం", "pay_method": "చెల్లింపు పద్ధతిని ఎంచుకోండి", "upi": "యూపీఐ (UPI)", "card": "క్రెడిట్/డెబిట్ కార్డ్", "cash": "కౌంటర్ వద్ద నగదు", "pay_now": "ఇప్పుడే చెల్లించండి", "place_order": "ఇప్పుడే ఆర్డర్ చేయండి", "back_cart": "← ట్రేకి తిరిగి వెళ్లండి", "status": "⏳ లైవ్ స్థితి", "s1": "👨‍🍳 చెఫ్‌లు పదార్థాలను కత్తిరిస్తున్నారు...", "s2": "🔥 మీ రుచికరమైన భోజనం వండబడుతోంది...", "s3": "🛵 మీ ఆర్డర్ ప్యాక్ చేయబడుతోంది!", "s4": "🎉 ఆర్డర్ సిద్ధంగా ఉంది & పంపబడింది!", "s5": "🎉 మీ ఆర్డర్ దారిలో ఉంది!", "s6": "వంటగది విశ్రాంతి తీసుకుంటోంది. ఆర్డర్‌ల కోసం వేచి ఉంది.", "feedback": "⭐ మీ అనుభవం", "rate_exp": "మీ అనుభవాన్ని రేట్ చేయండి:", "tell_more": "మాకు మరింత చెప్పండి:", "submit_feed": "అభిప్రాయాన్ని సమర్పించండి"},
    "ML": {"title": "സ്മാർട്ട് മെനു", "subtitle": "രുചികരമായ ഭക്ഷണം, നേരിട്ട് നിങ്ങളുടെ സ്ക്രീനിൽ.", "search": "തിരയുക...", "btn_search": "തിരയുക", "add": "ചേർക്കുക", "cart": "🛒 നിങ്ങളുടെ ട്രേ", "empty": "നിങ്ങളുടെ ട്രേ ശൂന്യമാണ്!", "items": "ഇനങ്ങൾ", "total": "ആകെ", "checkout": "പണമടയ്ക്കാൻ തുടരുക", "checkout_title": "ചെക്ക്ഔട്ട്", "amount_pay": "അടയ്ക്കേണ്ട തുക", "pay_method": "പേയ്മെന്റ് രീതി തിരഞ്ഞെടുക്കുക", "upi": "യുപിഐ (UPI)", "card": "ക്രെഡിറ്റ്/ഡെബിറ്റ് കാർഡ്", "cash": "കൗണ്ടറിൽ പണം", "pay_now": "ഇപ്പോൾ പണമടയ്ക്കുക", "place_order": "ഇപ്പോൾ ഓർഡർ ചെയ്യുക", "back_cart": "← ട്രേയിലേക്ക് മടങ്ങുക", "status": "⏳ തത്സമയ അവസ്ഥ", "s1": "👨‍🍳 പാചകക്കാർ ചേരുവകൾ മുറിക്കുന്നു...", "s2": "🔥 നിങ്ങളുടെ രുചികരമായ ഭക്ഷണം പാകം ചെയ്യുന്നു...", "s3": "🛵 നിങ്ങളുടെ ഓർഡർ പായ്ക്ക് ചെയ്യുന്നു!", "s4": "🎉 ഓർഡർ തയ്യാറാണ് & അയച്ചിരിക്കുന്നു!", "s5": "🎉 നിങ്ങളുടെ ഓർഡർ വഴിയിലാണ്!", "s6": "അടുക്കള വിശ്രമിക്കുന്നു. കാത്തിരിക്കുന്നു.", "feedback": "⭐ നിങ്ങളുടെ അനുഭവം", "rate_exp": "നിങ്ങളുടെ അനുഭവം റേറ്റുചെയ്യുക:", "tell_more": "കൂടുതൽ പറയുക:", "submit_feed": "അഭിപ്രായം സമർപ്പിക്കുക"}
}

LANG_DISPLAY_MAP = {"English": "EN", "हिन्दी": "HI", "ಕನ್ನಡ": "KN", "தமிழ்": "TA", "తెలుగు": "TE", "മലയാളം": "ML"}
LANG_CODES = {"EN": "en", "HI": "hi", "KN": "kn", "TA": "ta", "TE": "te", "ML": "ml"}


@st.cache_data(show_spinner=False)
def translate_dish(text, target_lang_code):
    if target_lang_code == "en" or not text: return text
    try:
        return GoogleTranslator(source='en', target=target_lang_code).translate(str(text))
    except:
        return text

# Note the ttl=2 here! This refreshes the cache so custom dishes appear instantly
@st.cache_data(show_spinner=False, ttl=2)
def fetch_menu():
    """Fetches real dishes from API AND local dishes from Kitchen KDS."""
    menu = []
    # 1. FETCH FROM API
    try:
        api_endpoints = [
            ("Veg", "https://www.themealdb.com/api/json/v1/1/filter.php?c=Vegetarian"),
            ("Non-Veg", "https://www.themealdb.com/api/json/v1/1/filter.php?c=Chicken"),
            ("Starters", "https://www.themealdb.com/api/json/v1/1/filter.php?c=Starter"),
            ("Soups", "https://www.themealdb.com/api/json/v1/1/search.php?s=soup")
        ]

        for category, url in api_endpoints:
            response = requests.get(url, timeout=5).json()
            meals = response.get('meals', [])[:8]

            for m in meals:
                dish_id = m['idMeal']
                name = m['strMeal']
                hash_num = int(hashlib.md5(dish_id.encode()).hexdigest(), 16)
                price = 150 + (hash_num % 350)
                kcal = 200 + (hash_num % 500)

                menu.append({
                    "id": dish_id,
                    "name_en": name,
                    "image": m['strMealThumb'],
                    "price": price,
                    "calories": kcal,
                    "category": category
                })
    except Exception as e:
        st.error("Failed to connect to the Internet Menu Database.")

    # 2. FETCH FROM KITCHEN KDS DB
    try:
        if os.path.exists(MENU_DB):
            with open(MENU_DB, "r") as f:
                local_dishes = json.load(f)
                menu.extend(local_dishes) # Add KDS dishes directly to the menu
    except Exception as e:
        pass

    return menu


def is_fuzzy_match(query, target_text):
    if not query: return True
    query, target_text = str(query).lower(), str(target_text).lower()
    if query in target_text: return True
    target_words, query_words = target_text.split(), query.split()
    for q_word in query_words:
        if len(q_word) < 3: continue
        for t_word in target_words:
            if difflib.SequenceMatcher(None, q_word, t_word).ratio() >= 0.7: return True
    return False


def trigger_voice(text):
    st.session_state.tts_trigger = text
    st.session_state.tts_id = time.time()


# --- 4. SESSION STATES ---
if 'display_lang' not in st.session_state: st.session_state.display_lang = "English"
if 'lang' not in st.session_state: st.session_state.lang = "EN"
if 'cart' not in st.session_state: st.session_state.cart = []
if 'order_status' not in st.session_state: st.session_state.order_status = None
if 'search_val' not in st.session_state: st.session_state.search_val = ""
if 'tts_trigger' not in st.session_state: st.session_state.tts_trigger = ""
if 'tts_id' not in st.session_state: st.session_state.tts_id = 0
if 'ui_view' not in st.session_state: st.session_state.ui_view = "cart"

with st.spinner("🌍 Fetching live global menu..."):
    base_menu = fetch_menu()

t = UI_TEXT.get(st.session_state.lang, UI_TEXT["EN"])
current_lang_code = LANG_CODES.get(st.session_state.lang, "en")

# --- 5. MAIN UI ---
st.write("")
h1, h2, h3 = st.columns([1, 6, 1])
with h1:
    lang_keys = list(LANG_DISPLAY_MAP.keys())
    new_lang_display = st.selectbox("🌐", lang_keys, index=lang_keys.index(st.session_state.display_lang),
                                    label_visibility="collapsed")
    if new_lang_display != st.session_state.display_lang:
        st.session_state.display_lang = new_lang_display
        st.session_state.lang = LANG_DISPLAY_MAP[new_lang_display]
        st.rerun()

with h2:
    st.markdown(f"<h1 class='gradient-text' style='font-size: 3.5rem; margin-bottom: 0;'>{t['title']}</h1>",
                unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#666; font-size:1.1rem; margin-top:-10px;'>{t['subtitle']}</p>",
                unsafe_allow_html=True)
with h3:
    if st.button("🔊 / ⏸️", help="Read or Pause the current menu", width="stretch"):
        trigger_voice("COMMAND_TOGGLE_MENU")

# Search
st.write("")
with st.form("search_form"):
    s1, s2 = st.columns([8, 2])
    with s1: search_query = st.text_input("Search", label_visibility="collapsed", placeholder=t['search'])
    with s2: submitted = st.form_submit_button(f"🔍 {t['btn_search']}")
if submitted: st.session_state.search_val = search_query.strip()
st.write("")

# Filters
category_options = ["All", "Veg", "Non-Veg", "Starters", "Soups"]
translated_categories = [translate_dish(cat, current_lang_code) for cat in category_options]
selected_translated_cat = st.radio("Filters", translated_categories, horizontal=True, label_visibility="collapsed")
selected_index = translated_categories.index(selected_translated_cat)
selected_cat_en = category_options[selected_index]

# Grid
st.markdown("<br>", unsafe_allow_html=True)
cols = st.columns(4)
col_index = 0

for dish in base_menu:
    if selected_cat_en != "All" and dish['category'] != selected_cat_en: continue
    local_dish_name = translate_dish(dish['name_en'], current_lang_code)
    local_category = translate_dish(dish['category'], current_lang_code)
    searchable_text = f"{dish['name_en']} {local_dish_name} {dish['category']} {local_category}"
    if st.session_state.search_val and not is_fuzzy_match(st.session_state.search_val, searchable_text): continue

    with cols[col_index % 4]:
        with st.container(border=True):
            st.image(dish['image'])
            st.markdown(
                f"<h4 style='margin: 12px 0 5px 0; font-size: 1.15rem; font-weight: 800; color: #1a1a1a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;' title='{local_dish_name}'>{local_dish_name}</h4>",
                unsafe_allow_html=True)
            st.markdown(
                f"<h3 style='color: #E23744; margin:0; font-weight: 800; font-size: 1.5rem;'>₹{dish['price']}</h3>",
                unsafe_allow_html=True)
            st.markdown(f"""
                <div style='display:flex; gap:8px; margin: 8px 0 15px 0;'>
                    <span style='background:#fff0f1; color:#E23744; padding:3px 8px; border-radius:12px; font-size:11px; font-weight:700;'>🔥 {dish['calories']} kcal</span>
                    <span style='background:#f1f3f5; color:#495057; padding:3px 8px; border-radius:12px; font-size:11px; font-weight:700;'>{local_category}</span>
                </div>
            """, unsafe_allow_html=True)

            if st.button(t['add'], key=f"btn_{dish['id']}", use_container_width=True):
                dish_copy = dish.copy()
                dish_copy['display_name'] = local_dish_name
                st.session_state.cart.append(dish_copy)
                st.toast(f"Mmm... {local_dish_name} added! 😋", icon="🛒")
                trigger_voice(f"Added {local_dish_name} to your tray.")
    col_index += 1

if col_index == 0:
    st.info("🍽️ No dishes matched your craving.")

# --- 6. SIDEBAR CART, PAYMENT & ADMIN ACCESS ---
with st.sidebar:
    if st.session_state.ui_view == "cart":
        st.markdown(
            f"<h2 style='color: #1a1a1a; font-weight: 800; margin-top: -20px; font-size: 2rem;'>{t['cart']}</h2>",
            unsafe_allow_html=True)
        if not st.session_state.cart:
            st.markdown(
                f"<div style='text-align:center; padding: 30px 10px; background: rgba(255,255,255,0.5); border-radius: 20px; border: 2px dashed #ddd;'><h1 style='font-size: 3rem; margin:0; opacity:0.5;'>🍽️</h1><p style='color: #888; font-weight: 600; margin-top: 10px;'>{t['empty']}</p></div>",
                unsafe_allow_html=True)
        else:
            total = sum(item['price'] for item in st.session_state.cart)
            col1, col2 = st.columns(2)
            col1.metric(t["items"], len(st.session_state.cart))
            col2.metric(t["total"], f"₹{total}")

            with st.container():
                for i, item in enumerate(st.session_state.cart):
                    st.markdown(
                        f"<div style='padding: 12px; background: white; border-radius: 15px; margin-bottom: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); display:flex; justify-content:space-between; align-items:center;'><div style='font-weight:600; color:#333; font-size: 14px; text-overflow:ellipsis; overflow:hidden; white-space:nowrap; max-width:70%;'>{item['display_name']}</div><div style='color:#E23744; font-weight:800; font-size: 15px;'>₹{item['price']}</div></div>",
                        unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(t['checkout'], type="primary", use_container_width=True):
                st.session_state.ui_view = "payment"
                st.rerun()

    elif st.session_state.ui_view == "payment":
        total_amount = sum(item['price'] for item in st.session_state.cart)
        st.markdown(
            f"<h2>{t['checkout_title']}</h2><div style='background: #fff0f1; padding: 15px; border-radius: 15px; border: 2px solid #E23744; text-align: center; margin-bottom: 20px;'><p style='margin:0; font-weight: 600; color: #495057;'>{t['amount_pay']}</p><h1 style='color: #E23744; margin: 0; font-weight: 800;'>₹{total_amount}</h1></div>",
            unsafe_allow_html=True)

        pay_modes = [t["upi"], t["card"], t["cash"]]
        payment_mode = st.radio(t["pay_method"], pay_modes)

        if payment_mode == t["cash"]:
            if st.button(t["place_order"], type="primary", use_container_width=True):
                st.success("Placed!")
                send_order_to_kitchen(st.session_state.cart, total_amount, "Cash")
                st.session_state.order_status = "Preparing"
                st.session_state.cart = []
                st.session_state.ui_view = "cart"
                trigger_voice("Order placed successfully. Pay at the counter.")
                time.sleep(2)
                st.rerun()

        if st.button(t["back_cart"], use_container_width=True):
            st.session_state.ui_view = "cart"
            st.rerun()

    st.divider()

    st.markdown(f"<h2 style='color: #1a1a1a; font-weight: 800;'>{t['status']}</h2>", unsafe_allow_html=True)
    if st.session_state.order_status == "Preparing":
        status_box = st.empty()
        progress_bar = st.progress(0)
        for percent_complete in range(100):
            time.sleep(0.02)
            progress_bar.progress(percent_complete + 1)
            if percent_complete < 30:
                status_box.info(t['s1'])
            elif percent_complete < 70:
                status_box.warning(t['s2'])
            else:
                status_box.success(t['s3'])
        status_box.success(t['s4'])
        st.session_state.order_status = "Dispatched"
    elif st.session_state.order_status == "Dispatched":
        st.success(t['s5'])
    else:
        st.markdown(f"<p style='color: #999; font-weight: 500; font-style: italic;'>{t['s6']}</p>",
                    unsafe_allow_html=True)

    # ---> FULL FEEDBACK RESTORATION (WITH STARS) <---
    st.divider()
    st.markdown(f"<h2 style='color: #1a1a1a; font-weight: 800;'>{t['feedback']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-weight: 600; margin-bottom: 5px; color: #495057;'>{t['rate_exp']}</p>", unsafe_allow_html=True)
    st.radio("Stars", ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"], index=4, horizontal=True, label_visibility="collapsed")
    st.text_area(t['tell_more'])
    if st.button(t['submit_feed'], use_container_width=True):
        st.toast("❤️", icon="👍")
        trigger_voice("Thank you for your valuable feedback.")

    # ---> NEW ADMIN LINK <---
    st.divider()
    st.markdown("<h3 style='color: #1a1a1a; font-weight: 800;'>👨‍🍳 Staff / Admin</h3>", unsafe_allow_html=True)
    st.markdown("Add custom dishes and manage live orders through the KDS panel.")
    # Assuming you run the KDS on port 8502
    st.markdown(
        """
        <a href="http://localhost:8502" target="_blank" style="
            display: block; 
            text-align: center; 
            background: linear-gradient(45deg, #1a1a1a, #333); 
            color: white; 
            padding: 10px; 
            border-radius: 15px; 
            text-decoration: none; 
            font-weight: 700; 
            margin-top: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        ">Launch Kitchen Dashboard ↗</a>
        """, unsafe_allow_html=True
    )
    st.markdown(
        "<div style='text-align: center; color: #bbb; font-weight: 500; font-size: 12px; margin-top: 40px;'>Handcrafted with ❤️<br>By Harshitha</div>",
        unsafe_allow_html=True)

# Voice Engine Code (Restored properly)
if st.session_state.tts_trigger:
    command_str = st.session_state.tts_trigger.replace("'", "\\'")
    js_tts = f"""
    <script>
        const command = "{command_str}";
        const currentMsgId = "{st.session_state.tts_id}";
        const synth = window.parent.speechSynthesis;

        if (command === "COMMAND_TOGGLE_MENU") {{
            if (synth.speaking) {{
                if (synth.paused) synth.resume();
                else synth.pause();
            }} else {{
                const dishTitles = window.parent.document.querySelectorAll('h4');
                let textToRead = "On the menu right now: ";
                let count = 0;
                dishTitles.forEach(el => {{
                    if (el.innerText && count < 15) {{ 
                        textToRead += el.innerText + ", ";
                        count++;
                    }}
                }});
                if (count === 0) textToRead = "No dishes found to read.";
                const utterance = new SpeechSynthesisUtterance(textToRead);
                synth.speak(utterance);
            }}
        }} else {{
            if (window.parent.lastSpokenMsgId !== currentMsgId) {{
                synth.cancel(); 
                const utterance = new SpeechSynthesisUtterance(command);
                synth.speak(utterance);
                window.parent.lastSpokenMsgId = currentMsgId; 
            }}
        }}
    </script>
    """
    components.html(js_tts, height=0, width=0)
