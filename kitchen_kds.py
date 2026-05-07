import streamlit as st
import json
import os

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Kitchen Dashboard", page_icon="👨‍🍳", layout="wide")

# --- 2. SESSION STATE ---
if 'admin_logged_in' not in st.session_state: st.session_state.admin_logged_in = False
if 'admin_user_db' not in st.session_state:
    # MOCK DB: format is {"username": "password"}
    st.session_state.admin_user_db = {"admin": "123", "chef": "pass"}

# --- 3. PREMIUM CSS (Dark Mode) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');
    html, body, [class*="css"], * { font-family: 'Outfit', sans-serif !important; }
    .stApp { background-color: #1e1e2f; color: white; }

    /* Login Card */
    .auth-card { background: #2a2a3b; border-radius: 20px; padding: 40px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.5); max-width: 400px; margin: 100px auto; border: 1px solid #444; }
    .gradient-text { background: linear-gradient(45deg, #E23744, #ff6b6b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 2.5rem; margin-bottom: 5px; }

    /* Order Tickets */
    .ticket { background: #2a2a3b; border-radius: 15px; padding: 20px; margin-bottom: 20px; border-left: 5px solid #E23744; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
    .ticket.preparing { border-left-color: #f39c12; }
    .ticket.ready { border-left-color: #2ecc71; opacity: 0.7; }
    .ticket-header { display: flex; justify-content: space-between; border-bottom: 1px solid #444; padding-bottom: 10px; margin-bottom: 10px; }
    .ticket-id { font-weight: 800; font-size: 1.2rem; color: #fff; }
    .ticket-time { color: #888; font-size: 0.9rem; }
    .item-list { list-style-type: none; padding: 0; margin: 0; }
    .item-list li { padding: 5px 0; font-size: 1.1rem; border-bottom: 1px dashed #444; color: #fff;}

    /* Buttons */
    .stButton > button { border-radius: 10px !important; font-weight: 700 !important; transition: all 0.2s; width: 100%; margin-top: 10px; }
    button[data-testid="baseButton-primary"] { background: #E23744 !important; color: white !important; border: none !important; }
    .stTextInput input { border-radius: 10px !important; padding: 10px !important; }

    /* Sidebar Fix for Dark Mode */
    [data-testid="stSidebar"] { background-color: #2a2a3b !important; }
    [data-testid="stSidebar"] .stMarkdown h2, [data-testid="stSidebar"] .stMarkdown h1 { color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. DATABASE FUNCTIONS ---
DB_FILE = "orders_db.json"
MENU_DB = "menu_db.json"
ASSETS_DIR = "assets"

# Ensure assets directory exists for images
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)


def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f: json.dump([], f)
    if not os.path.exists(MENU_DB):
        with open(MENU_DB, "w") as f: json.dump([], f)


def get_orders():
    init_db()
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def update_order_status(order_id, new_status):
    orders = get_orders()
    for o in orders:
        if o['order_id'] == order_id: o['status'] = new_status
    with open(DB_FILE, "w") as f:
        json.dump(orders, f)


# --- 5. SECURE LOGIN GATEWAY ---
if not st.session_state.admin_logged_in:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
        st.markdown("<h1 class='gradient-text'>Kitchen Access</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color:#aaa;'>Authorized Personnel Only</p>", unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Login", "Register Chef"])

        with tab1:
            l_user = st.text_input("Admin ID", placeholder="e.g. admin")
            l_pass = st.text_input("Password", type="password", placeholder="e.g. 123")
            if st.button("Enter Dashboard", type="primary"):
                if l_user in st.session_state.admin_user_db and st.session_state.admin_user_db[l_user] == l_pass:
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid Credentials.")

        with tab2:
            r_user = st.text_input("New Admin ID")
            r_pass = st.text_input("New Password", type="password")
            if st.button("Register Chef"):
                if r_user and r_pass:
                    st.session_state.admin_user_db[r_user] = r_pass
                    st.success(f"Registered {r_user} successfully! You can now login.")
                else:
                    st.error("Fill all fields.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 6. DISH MANAGEMENT (SIDEBAR FEATURE) ---
with st.sidebar:
    st.markdown("<h2 style='color:#E23744;'>➕ Add New Dish</h2>", unsafe_allow_html=True)
    with st.form("add_dish_form", clear_on_submit=True):
        d_name = st.text_input("Dish Name")
        d_price = st.number_input("Price (₹)", min_value=0)
        d_kcal = st.number_input("Calories", min_value=0)
        d_cat = st.selectbox("Category", ["Veg", "Non-Veg", "Starters", "Soups", "Bread"])
        d_file = st.file_uploader("Upload Dish Image", type=["jpg", "png", "jpeg"])

        if st.form_submit_button("Publish to Menu", use_container_width=True):
            if d_name and d_file:
                # Save Image to Assets
                file_path = os.path.join(ASSETS_DIR, d_file.name)
                with open(file_path, "wb") as f:
                    f.write(d_file.getbuffer())

                # Update menu_db.json
                init_db()
                with open(MENU_DB, "r") as f:
                    current_menu = json.load(f)

                new_dish = {
                    "id": len(current_menu) + 1000,
                    "name_en": d_name,
                    "price": d_price,
                    "calories": d_kcal,
                    "category": d_cat,
                    "image": file_path
                }

                current_menu.append(new_dish)
                with open(MENU_DB, "w") as f:
                    json.dump(current_menu, f, indent=4)

                st.success(f"✅ {d_name} is now Live!")
            else:
                st.error("Missing Name or Image!")

# --- 7. MAIN KITCHEN DASHBOARD ---
h1, h2, h3 = st.columns([6, 2, 1])
with h1: st.title("🔥 Live Kitchen Dashboard")
with h2:
    if st.button("🔄 Refresh Orders", use_container_width=True): st.rerun()
with h3:
    if st.button("🚪 Logout"):
        st.session_state.admin_logged_in = False
        st.rerun()
st.markdown("---")

orders = get_orders()
pending_orders = [o for o in orders if o['status'] == 'Pending']
preparing_orders = [o for o in orders if o['status'] == 'Preparing']
ready_orders = [o for o in orders if o['status'] == 'Ready']

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"<h3 style='color:#E23744;'>🛑 New Orders ({len(pending_orders)})</h3>", unsafe_allow_html=True)
    for o in pending_orders:
        st.markdown(f"""
            <div class='ticket'>
                <div class='ticket-header'><span class='ticket-id'>{o['order_id']}</span><span class='ticket-time'>{o['time']}</span></div>
                <ul class='item-list'>{''.join([f"<li>1x {item['display_name']}</li>" for item in o['items']])}</ul>
            </div>
        """, unsafe_allow_html=True)
        if st.button(f"👨‍🍳 Start Preparing", key=f"start_{o['order_id']}", type="primary"):
            update_order_status(o['order_id'], 'Preparing')
            st.rerun()

with col2:
    st.markdown(f"<h3 style='color:#f39c12;'>🔥 Preparing ({len(preparing_orders)})</h3>", unsafe_allow_html=True)
    for o in preparing_orders:
        st.markdown(f"""
            <div class='ticket preparing'>
                <div class='ticket-header'><span class='ticket-id'>{o['order_id']}</span><span class='ticket-time'>{o['time']}</span></div>
                <ul class='item-list'>{''.join([f"<li>1x {item['display_name']}</li>" for item in o['items']])}</ul>
            </div>
        """, unsafe_allow_html=True)
        if st.button(f"✅ Mark Ready", key=f"ready_{o['order_id']}"):
            update_order_status(o['order_id'], 'Ready')
            st.rerun()

with col3:
    st.markdown(f"<h3 style='color:#2ecc71;'>✅ Ready for Pickup ({len(ready_orders)})</h3>", unsafe_allow_html=True)
    for o in reversed(ready_orders[-5:]):
        st.markdown(f"""
            <div class='ticket ready'>
                <div class='ticket-header'><span class='ticket-id'>{o['order_id']}</span><span class='ticket-time'>Done</span></div>
                <p style='margin:0; color:#aaa;'>Order is waiting at counter.</p>
            </div>
        """, unsafe_allow_html=True)
