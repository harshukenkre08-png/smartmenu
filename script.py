import streamlit as st
import requests
import random
import time
import difflib
import json
import os
from datetime import datetime
import streamlit.components.v1 as components
from deep_translator import GoogleTranslator
import payment_processor

# --- 1. RESPONSIVE PAGE SETUP ---
st.set_page_config(page_title="Smart Menu", page_icon="🍔", layout="wide", initial_sidebar_state="expanded")

# --- DATABASE SYNC LOGIC ---
DB_FILE = "orders_db.json"


def send_order_to_kitchen(cart_items, total_amount, payment_method):
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f: json.dump([], f)

    try:
        with open(DB_FILE, "r") as f:
            orders = json.load(f)
    except:
        orders = []

    new_order = {
        "order_id": f"ORD_{random.randint(1000, 9999)}",
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
    @keyframes gradient { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    [data-testid="stVerticalBlockBorderWrapper"] { border-radius: 24px !important; background-color: rgba(255, 255, 255, 0.9) !important; backdrop-filter: blur(10px); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03) !important; border: 1px solid rgba(255, 255, 255, 0.5) !important; padding: 15px !important; transition: all 0.3s ease; }
    [data-testid="stVerticalBlockBorderWrapper"]:hover { transform: translateY(-8px) scale(1.02); box-shadow: 0 20px 40px rgba(226, 55, 68, 0.1) !important; border-color: rgba(226, 55, 68, 0.2) !important; }
    [data-testid="stImage"] img { border-radius: 18px !important; transition: transform 0.5s ease; }
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


# --- 3. CACHED DATA FUNCTIONS ---
@st.cache_data(show_spinner=False)
def fetch_menu():
    full_menu = []
    seen_meals = set()
    dish_id = 0
    perfect_breads = [
        {"name": "Garlic Butter Naan",
         "img": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=500&q=80"},
        {"name": "Tandoori Roti", "img": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=500&q=80"},
        {"name": "Stuffed Aloo Paratha",
         "img": "https://images.unsplash.com/photo-1626082896492-766af4eb6501?w=500&q=80"},
        {"name": "Toasted Garlic Bread",
         "img": "https://images.unsplash.com/photo-1573140247632-f8fd74997d5c?w=500&q=80"}
    ]
    for bread in perfect_breads:
        dish_id += 1
        seen_meals.add(bread["name"].lower())
        full_menu.append(
            {"id": dish_id, "name_en": bread["name"], "image": bread["img"], "price": random.randint(60, 150),
             "calories": random.randint(150, 350), "category": "Bread"})

    endpoints = [
        ("Soups", "https://www.themealdb.com/api/json/v1/1/search.php?s=soup"),
        ("Starters", "https://www.themealdb.com/api/json/v1/1/filter.php?c=Starter"),
        ("Bread", "https://www.themealdb.com/api/json/v1/1/search.php?s=bread"),
        ("Rice & Chicken", "https://www.themealdb.com/api/json/v1/1/filter.php?c=Chicken"),
        ("Rice & Chicken", "https://www.themealdb.com/api/json/v1/1/search.php?s=rice"),
        ("Veg", "https://www.themealdb.com/api/json/v1/1/filter.php?c=Vegetarian"),
        ("Veg", "https://www.themealdb.com/api/json/v1/1/filter.php?c=Vegan"),
        ("Non-Veg", "https://www.themealdb.com/api/json/v1/1/filter.php?c=Beef"),
        ("Non-Veg", "https://www.themealdb.com/api/json/v1/1/filter.php?c=Seafood")
    ]
    for category, url in endpoints:
        try:
            response = requests.get(url, timeout=5).json()
            meals = response.get('meals') or []
            for m in meals:
                name_lower = m['strMeal'].lower()
                if name_lower in seen_meals: continue
                if category == "Soups" and "soup" not in name_lower and "broth" not in name_lower: continue
                if category == "Starters" and ("soup" in name_lower or "cake" in name_lower): continue
                seen_meals.add(name_lower)
                dish_id += 1
                full_menu.append({"id": dish_id, "name_en": m['strMeal'], "image": m['strMealThumb'],
                                  "price": random.randint(150, 450), "calories": random.randint(200, 700),
                                  "category": category})
        except:
            continue
    random.shuffle(full_menu)
    return full_menu


@st.cache_data(show_spinner=False)
def translate_text(text, target_lang_code):
    if target_lang_code == "en": return text
    try:
        return GoogleTranslator(source='en', target=target_lang_code).translate(text)
    except:
        return text


def is_fuzzy_match(query, target_text, threshold=0.55):
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


LANG_CODES = {"EN": "en", "HI": "hi", "KN": "kn", "TA": "ta", "TE": "te", "ML": "ml"}
UI_TEXT = {
    "EN": {"title": "The Tech Bistro", "search": "Search for cravings...", "add": "Add to Tray", "cart": "🛒 Your Tray",
           "empty": "Your tray is looking a bit empty!", "checkout": "Proceed to Pay", "status": "⏳ Live Status",
           "feedback": "⭐ Your Experience", "all": "All", "btn_search": "🔍 Find"},
    "HI": {"title": "द टेक बिस्टरो", "search": "व्यंजन खोजें...", "add": "ट्रे में जोड़ें", "cart": "🛒 आपकी ट्रे",
           "empty": "आपकी ट्रे खाली है!", "checkout": "भुगतान करने के लिए आगे बढ़ें", "status": "⏳ लाइव स्थिति",
           "feedback": "⭐ आपका अनुभव", "all": "सभी", "btn_search": "🔍 खोजें"}
}

# --- 4. SESSION STATES ---
if 'lang' not in st.session_state: st.session_state.lang = "EN"
if 'cart' not in st.session_state: st.session_state.cart = []
if 'order_status' not in st.session_state: st.session_state.order_status = None
if 'search_val' not in st.session_state: st.session_state.search_val = ""
if 'tts_trigger' not in st.session_state: st.session_state.tts_trigger = ""
if 'tts_id' not in st.session_state: st.session_state.tts_id = 0
if 'ui_view' not in st.session_state: st.session_state.ui_view = "cart"

with st.spinner("✨ Preparing the menu..."):
    base_menu = fetch_menu()

t = UI_TEXT.get(st.session_state.lang, UI_TEXT["EN"])
current_lang_code = LANG_CODES.get(st.session_state.lang, "en")

# --- 5. MAIN UI ---
st.write("")
h1, h2, h3 = st.columns([1, 6, 1])
with h1:
    new_lang = st.selectbox("🌐", ["EN", "HI", "KN", "TA", "TE", "ML"], label_visibility="collapsed")
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()
with h2:
    st.markdown(f"<h1 class='gradient-text' style='font-size: 3.5rem; margin-bottom: 0;'>{t['title']}</h1>",
                unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center; color:#666; font-size:1.1rem; margin-top:-10px;'>Gourmet flavors, delivered directly to your screen.</p>",
        unsafe_allow_html=True)
with h3:
    if st.button("🔊 / ⏸️", help="Read or Pause the current menu", use_container_width=True):
        trigger_voice("COMMAND_TOGGLE_MENU")

# Search
st.write("")
with st.form("search_form"):
    s1, s2 = st.columns([8, 2])
    with s1: search_query = st.text_input(t['search'], label_visibility="collapsed",
                                          placeholder="E.g., Chicken Tikka, Paneer, Soup...")
    with s2: submitted = st.form_submit_button(t['btn_search'], use_container_width=True)
if submitted: st.session_state.search_val = search_query.strip()
st.write("")

# Filters
category_options = ["All", "Veg", "Non-Veg", "Bread", "Rice & Chicken", "Starters", "Soups"]
translated_categories = [translate_text(cat, current_lang_code) for cat in category_options]
selected_translated_cat = st.radio("Filters", translated_categories, horizontal=True, label_visibility="collapsed")
selected_index = translated_categories.index(selected_translated_cat)
selected_cat_en = category_options[selected_index]

# Grid
st.markdown("<br>", unsafe_allow_html=True)
cols = st.columns(4)
col_index = 0

for dish in base_menu:
    if selected_cat_en != "All" and dish['category'] != selected_cat_en: continue
    local_dish_name = translate_text(dish['name_en'], current_lang_code)
    local_category = translate_text(dish['category'], current_lang_code)
    searchable_text = f"{dish['name_en']} {local_dish_name} {dish['category']} {local_category}"
    if st.session_state.search_val and not is_fuzzy_match(st.session_state.search_val, searchable_text): continue

    with cols[col_index % 4]:
        with st.container(border=True):
            st.image(dish['image'], use_container_width=True)
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
    if st.session_state.search_val: trigger_voice("No dishes matched your craving.")

# --- 6. SIDEBAR CART & PAYMENT ---
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
            col1.metric("Items", len(st.session_state.cart))
            col2.metric("Total", f"₹{total}")

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
            f"<h2>Checkout</h2><div style='background: #fff0f1; padding: 15px; border-radius: 15px; border: 2px solid #E23744; text-align: center; margin-bottom: 20px;'><p style='margin:0; font-weight: 600; color: #495057;'>Amount to Pay</p><h1 style='color: #E23744; margin: 0; font-weight: 800;'>₹{total_amount}</h1></div>",
            unsafe_allow_html=True)
        payment_mode = st.radio("Select Payment Method", ["UPI", "Credit/Debit Card", "Cash at Counter"])

        if payment_mode == "UPI":
            upi_id = st.text_input("Enter UPI ID (e.g., name@okbank)", placeholder="name@okbank")
            if st.button("Pay Now", type="primary", use_container_width=True):
                with st.spinner("Processing UPI Payment..."):
                    result = payment_processor.process_upi_payment(upi_id, total_amount)
                    if result['status'] == 'success':
                        st.success(result['message'])
                        send_order_to_kitchen(st.session_state.cart, total_amount, "UPI")
                        st.session_state.order_status = "Preparing"
                        st.session_state.cart = []
                        st.session_state.ui_view = "cart"
                        trigger_voice("Payment successful. The chefs are preparing your meal now!")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(result['message'])
                        trigger_voice("Payment failed. Please check your UPI ID.")

        elif payment_mode == "Credit/Debit Card":
            card_name = st.text_input("Name on Card")
            card_num = st.text_input("Card Number", max_chars=16, type="password")
            col1, col2 = st.columns(2)
            with col1:
                expiry = st.text_input("Expiry (MM/YY)", max_chars=5)
            with col2:
                cvv = st.text_input("CVV", max_chars=3, type="password")
            if st.button("Pay Now", type="primary", use_container_width=True):
                with st.spinner("Authenticating Card..."):
                    result = payment_processor.process_card_payment(card_name, card_num, expiry, cvv, total_amount)
                    if result['status'] == 'success':
                        st.success(result['message'])
                        send_order_to_kitchen(st.session_state.cart, total_amount, "Card")
                        st.session_state.order_status = "Preparing"
                        st.session_state.cart = []
                        st.session_state.ui_view = "cart"
                        trigger_voice("Payment successful. The chefs are preparing your meal now!")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(result['message'])
                        trigger_voice("Payment failed. Please check your card details.")

        elif payment_mode == "Cash at Counter":
            st.info("Please pay at the billing counter after your meal.")
            if st.button("Place Order Now", type="primary", use_container_width=True):
                result = payment_processor.process_cash_payment(total_amount)
                st.success(result['message'])
                send_order_to_kitchen(st.session_state.cart, total_amount, "Cash")
                st.session_state.order_status = "Preparing"
                st.session_state.cart = []
                st.session_state.ui_view = "cart"
                trigger_voice("Order placed successfully. Pay at the counter.")
                time.sleep(2)
                st.rerun()

        if st.button("← Back to Cart", use_container_width=True):
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
                status_box.info("👨‍🍳 Chefs are chopping ingredients...")
            elif percent_complete < 70:
                status_box.warning("🔥 Cooking your delicious meal...")
            else:
                status_box.success("🛵 Packing your order!")

        status_box.success("🎉 Order Ready & Dispatched!")
        st.balloons()
        st.snow()
        st.session_state.order_status = "Dispatched"
    elif st.session_state.order_status == "Dispatched":
        st.success("🎉 Your order is on its way!")
    else:
        st.markdown(
            "<p style='color: #999; font-weight: 500; font-style: italic;'>Kitchen is resting. Waiting for orders.</p>",
            unsafe_allow_html=True)

    st.divider()
    st.markdown(f"<h2 style='color: #1a1a1a; font-weight: 800;'>{t['feedback']}</h2>", unsafe_allow_html=True)
    st.slider("Rate your experience:", 1, 5, 5)
    st.text_area("Tell us more (Optional):", placeholder="The food was amazing...")
    if st.button("Submit Feedback", use_container_width=True):
        st.toast("Thank you for your feedback! ❤️")
        trigger_voice("Thank you for your valuable feedback.")

    st.markdown(
        "<div style='text-align: center; color: #bbb; font-weight: 500; font-size: 12px; margin-top: 40px;'>Handcrafted with ❤️<br>By Raj Kumar B</div>",
        unsafe_allow_html=True)

# Voice Engine
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