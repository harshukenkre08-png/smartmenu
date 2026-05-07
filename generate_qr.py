import qrcode

# Put your NEW Streamlit Network URL here (make sure it ends in 8501!)
MENU_URL = "http://192.168.137.1:8501"

print(f"Generating QR Code for: {MENU_URL}")

qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
qr.add_data(MENU_URL)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
img.save("table_qr_code.png")
print("✅ Success! Check PyCharm for 'table_qr_code.png'")