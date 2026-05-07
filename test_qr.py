import qrcode

# We are using Google as our universal dummy test!
DUMMY_URL = "https://www.google.com"

print("🧪 Generating DUMMY TEST QR Code...")

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=15, # Made it slightly bigger for easier scanning
    border=4,
)

qr.add_data(DUMMY_URL)
qr.make(fit=True)

# Create and save the image
img = qr.make_image(fill_color="black", back_color="white")
img.save("dummy_test_qr.png")

print("✅ Success! Look for 'dummy_test_qr.png' in PyCharm, double-click it, and scan it!")