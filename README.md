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
    - 🗑️ **Delete Demo / Test Invoices:** If you generated a test or checking invoice, tap **`🗑️ Delete this Demo / Test Invoice`** (or the trash icon in Recent Invoices). This automatically deletes the files and restores the invoice number counter (e.g. rolls back from `INV-0156-C` to `INV-0156-B`) so no numbers are wasted!

---

## 🌐 24/7 Cloud Deployment (Use Anywhere, Anytime from Phone):

To run this 24/7 on your phone without needing your laptop turned on:

1. **Deploy to Render (Free):**
   - Go to [render.com](https://render.com) and Sign In with GitHub.
   - Click **New +** -> **Web Service**.
   - Select your repository: **`satishmehtre037/InvoiceWWGenerator`**.
   - Settings:
     - **Name:** `invoicewwgenerator`
     - **Runtime:** `Python 3`
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `gunicorn app:app`
   - Click **Deploy Web Service**.
2. **Access Anywhere:**
   - Render gives you a free HTTPS link like `https://invoicewwgenerator.onrender.com`.
   - Open this URL on your phone's browser, bookmark it or add it to your Home Screen as an App! Now you can generate invoices anywhere, anytime on the go.

---

## ⏰ How to Keep Render Awake 24/7 (Never Sleeps / Instant Loading):

Render free tier goes to sleep after 15 minutes of inactivity. To keep your app **awake 24/7 with zero waiting time**:

### Method 1: Free Uptime Monitor (Recommended — Takes 1 min)
1. Go to **[cron-job.org](https://cron-job.org)** or **[uptimerobot.com](https://uptimerobot.com)** (both 100% free).
2. Create a free account and click **Create Cronjob** / **Add Monitor**.
3. Set URL to your Render ping URL:
   `https://<your-render-app-name>.onrender.com/ping`
4. Set schedule / interval to **every 10 minutes** (or 14 minutes).
5. Done! Because it receives a ping every 10 minutes, Render will **NEVER sleep** and will always load instantly on your phone!

### Method 2: Automatic Built-in Self-Ping
- In your Render Dashboard ➔ Environment Variables, add:
  - Key: `KEEP_AWAKE_URL`
  - Value: `https://<your-render-app-name>.onrender.com`
- The app has a built-in background worker that will automatically ping itself every 10 minutes.

---

## 💻 On Laptop (Local Network):
You can also open:
👉 **`http://localhost:5000`** in Chrome / Edge on your laptop anytime!
