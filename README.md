# Wanderworld Holidays - Mobile & Laptop Invoice Dashboard

This system lets you generate official, high-resolution **Wanderworld Holidays** invoices on your **phone** (or laptop) in just 1 tap.

---

## 📱 How to Use on Your Phone:

1. Double-click [**`Open_Phone_Dashboard.bat`**](file:///c:/Users/Satish/OneDrive/Desktop/HimachalTripProject/InvoiceGenerater/Open_Phone_Dashboard.bat) (or run `python app.py`).
2. Make sure your phone is connected to the **same Wi-Fi or Mobile Hotspot** as your laptop.
3. Open your phone's browser and go to:
   👉 **`http://192.168.0.112:5000`**  *(or scan the QR code printed in the terminal!)*
4. **On Your Phone:**
   - Tap your payment stage: **Booking (₹999)**, **1st Installment (₹5,000)**, **2nd Installment (₹5,000)**, or **Early Bird (₹14,699)**.
   - Enter Student Name (e.g. `Aarav Mehta`).
   - The invoice number automatically increments (`INV-0156-B`, `INV-0156-C`, ...).
   - Tap **⚡ Generate Official Invoice**.
5. **Instant Actions on Phone:**
   - 🖼️ **Save Image (PNG):** Saves high-res image directly to your phone gallery.
   - 📄 **Save PDF:** Saves print-ready official PDF.
   - 💬 **Share on WhatsApp:** 1-tap button that generates and pre-fills the verification message:
     ```text
     *🏔️ WW | Himachal '27 — Mountains & Memories 🏔️*

     Hey *{Student Name}*, your payment has been *VERIFIED & CONFIRMED*! 🎉

     💰 Amount Credited: ₹999
     🏷️ Payment Stage: Booking
     📉 Remaining Balance: ₹13,700

     Attached is your official invoice copy. Welcome aboard! ❄️✨
     ```
   - 📋 **Copy WhatsApp Message Template:** Copies the formatted text to clipboard so you can paste it into the student's chat with the image.

---

## 🌐 24/7 Cloud Deployment (Use Anywhere, Anytime from Phone):

To run this 24/7 on your phone without needing your laptop turned on:

1. **Deploy to Render (Free):**
   - Go to [render.com](https://render.com) and Sign In with GitHub.
   - Click **New +** -> **Web Service**.
   - Select your repository: **`satishmehtre037/InvoiceWWGenerator`**.
   - Settings:
     - **Name:** `invoicewwgenerator` (or your choice)
     - **Runtime:** `Python 3`
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `gunicorn app:app`
   - Click **Deploy Web Service**.
2. **Access Anywhere:**
   - Render gives you a free HTTPS link like `https://invoicewwgenerator.onrender.com`.
   - Open this URL on your phone's browser, bookmark it or add it to your Home Screen as an App! Now you can generate invoices anywhere, anytime on the go.

---

## 💻 On Laptop (Local Network):
You can also open:
👉 **`http://localhost:5000`** in Chrome / Edge on your laptop anytime!
