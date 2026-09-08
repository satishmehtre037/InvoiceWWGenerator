"""
Wanderworld Holidays - Mobile & Web Invoice Dashboard
======================================================
Allows generating official invoices directly from your smartphone or laptop browser.
Features:
- Responsive mobile-first interface designed for iPhone / Android
- 1-Tap payment presets (Booking ₹999, Installments 1/2/3, Early Bird)
- Auto-incrementing invoice numbers (INV-0156-B, INV-0156-C, ...)
- Instant visual preview on phone
- 1-Tap Download PNG (for WhatsApp) and PDF (for Email)
- 1-Tap WhatsApp confirmation message generator & share button
- Recent invoice history log with download links
"""

import os
import sys
import socket
import csv
import re
import threading
import time
import urllib.request
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify, send_from_directory

from generate_invoice import (
    create_invoice,
    get_next_invoice_number,
    delete_invoice_record,
    PRESETS,
    OUTPUT_DIR,
    HISTORY_FILE
)

app = Flask(__name__)

def keep_awake_worker():
    """Background worker to automatically ping Render web service every 10 minutes to stay awake 24/7."""
    time.sleep(20)
    app_url = os.environ.get("RENDER_EXTERNAL_URL") or os.environ.get("KEEP_AWAKE_URL")
    if not app_url:
        return

    ping_url = f"{app_url.rstrip('/')}/ping"
    print(f"[+] Keep-awake worker started. Pinging {ping_url} every 10 minutes.")

    while True:
        try:
            req = urllib.request.Request(ping_url, headers={'User-Agent': 'RenderKeepAwake/1.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                pass
        except Exception:
            pass
        time.sleep(600)

# Start background keep-awake thread
threading.Thread(target=keep_awake_worker, daemon=True).start()

def get_local_ip():
    """Finds the local network IP for phone access."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Wanderworld | Invoice Hub</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #FBD813;
            --primary-hover: #e5c40d;
            --bg: #0d1117;
            --card-bg: #161b22;
            --card-border: #30363d;
            --text-main: #f0f6fc;
            --text-muted: #8b949e;
            --accent: #238636;
            --accent-blue: #58a6ff;
            --font-display: 'Outfit', sans-serif;
            --font-body: 'Plus Jakarta Sans', sans-serif;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            font-family: var(--font-body);
            background-color: var(--bg);
            color: var(--text-main);
            min-height: 100vh;
            padding: 16px 12px 60px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .container {
            width: 100%;
            max-width: 520px;
        }

        /* Header */
        .header {
            text-align: center;
            margin-bottom: 20px;
            padding: 10px 0;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(251, 216, 19, 0.15);
            color: var(--primary);
            border: 1px solid rgba(251, 216, 19, 0.3);
            padding: 5px 14px;
            border-radius: 20px;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 10px;
        }

        .title {
            font-family: var(--font-display);
            font-size: 1.75rem;
            font-weight: 800;
            color: #fff;
            letter-spacing: -0.5px;
            line-height: 1.2;
        }

        .subtitle {
            color: var(--text-muted);
            font-size: 0.88rem;
            margin-top: 4px;
        }

        /* Card */
        .card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 18px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
            margin-bottom: 20px;
        }

        .section-label {
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        /* Form Controls */
        .form-group {
            margin-bottom: 16px;
        }

        label {
            display: block;
            font-size: 0.85rem;
            font-weight: 600;
            color: #c9d1d9;
            margin-bottom: 6px;
        }

        input, select {
            width: 100%;
            background: #0d1117;
            border: 1.5px solid #30363d;
            border-radius: 12px;
            padding: 13px 14px;
            font-size: 0.98rem;
            color: #fff;
            font-family: var(--font-body);
            transition: all 0.2s ease;
            outline: none;
        }

        input:focus, select:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(251, 216, 19, 0.2);
        }

        .row-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }

        /* Preset Chips */
        .presets-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 18px;
        }

        .preset-btn {
            background: #21262d;
            border: 1.5px solid #30363d;
            color: #c9d1d9;
            padding: 12px 10px;
            border-radius: 12px;
            text-align: left;
            cursor: pointer;
            transition: all 0.18s ease;
            display: flex;
            flex-direction: column;
            gap: 3px;
        }

        .preset-btn:active {
            transform: scale(0.97);
        }

        .preset-btn.active {
            background: rgba(251, 216, 19, 0.12);
            border-color: var(--primary);
            color: #fff;
        }

        .preset-name {
            font-size: 0.82rem;
            font-weight: 700;
            color: #fff;
        }

        .preset-price {
            font-family: var(--font-display);
            font-size: 1.05rem;
            font-weight: 800;
            color: var(--primary);
        }

        .preset-bal {
            font-size: 0.72rem;
            color: var(--text-muted);
        }

        /* Submit Button */
        .btn-generate {
            width: 100%;
            background: var(--primary);
            color: #0d1117;
            border: none;
            border-radius: 14px;
            padding: 16px;
            font-family: var(--font-display);
            font-size: 1.1rem;
            font-weight: 800;
            letter-spacing: 0.2px;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 4px 18px rgba(251, 216, 19, 0.35);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            margin-top: 8px;
        }

        .btn-generate:hover {
            background: var(--primary-hover);
        }

        .btn-generate:active {
            transform: scale(0.98);
        }

        .btn-generate:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        /* Result Section */
        #resultCard {
            display: none;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .preview-img {
            width: 100%;
            border-radius: 12px;
            border: 1px solid var(--card-border);
            margin-bottom: 16px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.5);
        }

        .action-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 12px;
        }

        .action-btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            padding: 12px;
            border-radius: 12px;
            font-size: 0.9rem;
            font-weight: 700;
            text-decoration: none;
            text-align: center;
            border: none;
            cursor: pointer;
            transition: all 0.15s ease;
        }

        .btn-whatsapp {
            background: #25D366;
            color: #fff;
            grid-column: span 2;
            padding: 14px;
            font-size: 0.98rem;
            font-weight: 700;
        }

        .btn-pdf {
            background: #e5534b;
            color: #fff;
        }

        .btn-png {
            background: #238636;
            color: #fff;
        }

        .btn-copy {
            background: #21262d;
            border: 1px solid var(--card-border);
            color: #c9d1d9;
            grid-column: span 2;
            padding: 10px;
            font-size: 0.85rem;
        }

        .btn-delete-demo {
            background: rgba(248, 81, 73, 0.12);
            border: 1px solid rgba(248, 81, 73, 0.35);
            color: #f85149;
            grid-column: span 2;
            padding: 10px;
            font-size: 0.85rem;
            cursor: pointer;
            border-radius: 10px;
            transition: all 0.2s ease;
            font-weight: 600;
        }

        .btn-delete-demo:hover, .btn-delete-demo:active {
            background: rgba(248, 81, 73, 0.25);
            transform: scale(0.98);
        }

        /* History Table */
        .history-list {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .history-item {
            background: #21262d;
            border: 1px solid #30363d;
            padding: 12px 14px;
            border-radius: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .hist-info h4 {
            font-size: 0.92rem;
            font-weight: 700;
            color: #fff;
        }

        .hist-info p {
            font-size: 0.78rem;
            color: var(--text-muted);
            margin-top: 2px;
        }

        .hist-actions {
            display: flex;
            gap: 8px;
        }

        .hist-icon-btn {
            background: #30363d;
            color: #fff;
            padding: 8px 10px;
            border-radius: 8px;
            font-size: 0.78rem;
            text-decoration: none;
            font-weight: 600;
            border: none;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }

        .hist-del-btn {
            background: rgba(248, 81, 73, 0.15) !important;
            color: #f85149 !important;
            border: 1px solid rgba(248, 81, 73, 0.3) !important;
        }

        .hist-del-btn:hover, .hist-del-btn:active {
            background: rgba(248, 81, 73, 0.35) !important;
            transform: scale(0.95);
        }

        .toast {
            position: fixed;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%) translateY(100px);
            background: #238636;
            color: #fff;
            padding: 10px 20px;
            border-radius: 30px;
            font-size: 0.88rem;
            font-weight: 600;
            box-shadow: 0 8px 25px rgba(0,0,0,0.6);
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            opacity: 0;
            z-index: 999;
        }

        .toast.show {
            transform: translateX(-50%) translateY(0);
            opacity: 1;
        }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <div class="badge">🏔️ Wanderworld Holidays</div>
        <h1 class="title">Invoice Generator</h1>
        <p class="subtitle">Official Mobile & Web Dashboard</p>
    </div>

    <!-- Generator Card -->
    <div class="card">
        <div class="section-label">⚡ Select Payment Stage</div>
        <div class="presets-grid">
            <button type="button" class="preset-btn active" onclick="selectPreset(1, 999, 'Booking', '13,700/-')">
                <span class="preset-name">Booking Stage</span>
                <span class="preset-price">₹999</span>
                <span class="preset-bal">Bal: ₹13,700/-</span>
            </button>
            <button type="button" class="preset-btn" onclick="selectPreset(2, 5000, '1st Installment', '8,700/-')">
                <span class="preset-name">1st Installment</span>
                <span class="preset-price">₹5,000</span>
                <span class="preset-bal">Bal: ₹8,700/-</span>
            </button>
            <button type="button" class="preset-btn" onclick="selectPreset(3, 5000, '2nd Installment', '3,700/-')">
                <span class="preset-name">2nd Installment</span>
                <span class="preset-price">₹5,000</span>
                <span class="preset-bal">Bal: ₹3,700/-</span>
            </button>
            <button type="button" class="preset-btn" onclick="selectPreset(4, 3700, '3rd Installment', '0/-')">
                <span class="preset-name">3rd Installment</span>
                <span class="preset-price">₹3,700</span>
                <span class="preset-bal">Bal: ₹0 (Paid)</span>
            </button>
            <button type="button" class="preset-btn" onclick="selectPreset(5, 14699, 'Early Bird Full Pass', '0/-')">
                <span class="preset-name">Early Bird Pass</span>
                <span class="preset-price">₹14,699</span>
                <span class="preset-bal">Full Clearance</span>
            </button>
            <button type="button" class="preset-btn" onclick="selectPreset(7, null, 'Custom', '')">
                <span class="preset-name">Custom Amount</span>
                <span class="preset-price">Custom</span>
                <span class="preset-bal">Manual Input</span>
            </button>
        </div>

        <form id="invoiceForm" onsubmit="handleGenerate(event)">
            <div class="form-group">
                <label>Student / Passenger Name</label>
                <input type="text" id="custName" placeholder="e.g. Rahul Sharma" required autofocus>
            </div>

            <div class="row-2">
                <div class="form-group">
                    <label>Invoice Number</label>
                    <input type="text" id="invNo" value="{{ next_inv_no }}" required>
                </div>
                <div class="form-group">
                    <label>Stage / Type</label>
                    <input type="text" id="stage" value="Booking" required>
                </div>
            </div>

            <div class="row-2">
                <div class="form-group">
                    <label>Amount Paid (₹)</label>
                    <input type="number" step="any" id="amount" value="999" required>
                </div>
                <div class="form-group">
                    <label>Remaining Balance</label>
                    <input type="text" id="balance" value="13,700/-" required>
                </div>
            </div>

            <div class="row-2">
                <div class="form-group">
                    <label>Date (DD/MM/YYYY)</label>
                    <input type="text" id="dateStr" value="{{ today_date }}" required>
                </div>
                <div class="form-group">
                    <label>Time</label>
                    <input type="text" id="timeStr" value="{{ current_time }}">
                </div>
            </div>

            <div class="form-group">
                <label>Description</label>
                <input type="text" id="desc" value="Himachal Winter Trip 2027" required>
            </div>

            <button type="submit" class="btn-generate" id="genBtn">
                ⚡ Generate Official Invoice
            </button>
        </form>
    </div>

    <!-- Result / Preview Section -->
    <div class="card" id="resultCard">
        <div class="section-label" style="color: #25D366;">🎉 Generated Successfully</div>
        <img id="previewImg" class="preview-img" src="" alt="Invoice Preview">

        <div class="action-grid">
            <a id="btnWhatsApp" href="#" target="_blank" class="action-btn btn-whatsapp">
                💬 Share on WhatsApp
            </a>
            <a id="btnDownloadPng" href="#" download class="action-btn btn-png">
                🖼️ Save Image (PNG)
            </a>
            <a id="btnDownloadPdf" href="#" download class="action-btn btn-pdf">
                📄 Save PDF
            </a>
            <button type="button" class="action-btn btn-copy" onclick="copyWhatsAppTemplate()">
                📋 Copy WhatsApp Message Template
            </button>
            <button type="button" class="btn-delete-demo" onclick="deleteCurrentInvoice()">
                🗑️ Delete this Demo / Test Invoice
            </button>
        </div>
    </div>

    <!-- Recent Invoices -->
    <div class="card">
        <div class="section-label">📜 Recent Invoices Log</div>
        <div class="history-list" id="historyList">
            {% for item in history %}
            <div class="history-item">
                <div class="hist-info">
                    <h4>{{ item.name }}</h4>
                    <p>{{ item.inv_no }} • {{ item.stage }} • ₹{{ item.amount }} ({{ item.date }})</p>
                </div>
                <div class="hist-actions">
                    <a href="/download/{{ item.png_name }}" target="_blank" class="hist-icon-btn">PNG</a>
                    <a href="/download/{{ item.pdf_name }}" target="_blank" class="hist-icon-btn">PDF</a>
                    <button type="button" onclick="deleteInvoice('{{ item.inv_no }}', '{{ item.name }}')" class="hist-icon-btn hist-del-btn" title="Delete Invoice">🗑️</button>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</div>

<div class="toast" id="toast">Message copied to clipboard!</div>

<script>
let lastGeneratedData = null;

function selectPreset(id, amt, stage, bal) {
    document.querySelectorAll('.preset-btn').forEach(btn => btn.classList.remove('active'));
    event.currentTarget.classList.add('active');

    if (amt !== null) {
        document.getElementById('amount').value = amt;
    }
    if (stage) {
        document.getElementById('stage').value = stage;
    }
    if (bal) {
        document.getElementById('balance').value = bal;
    }
}

async function handleGenerate(e) {
    e.preventDefault();
    const btn = document.getElementById('genBtn');
    btn.disabled = true;
    btn.innerHTML = '⏳ Creating Invoice...';

    const payload = {
        name: document.getElementById('custName').value.trim(),
        inv_no: document.getElementById('invNo').value.trim(),
        stage: document.getElementById('stage').value.trim(),
        amount: parseFloat(document.getElementById('amount').value),
        balance: document.getElementById('balance').value.trim(),
        date: document.getElementById('dateStr').value.trim(),
        time: document.getElementById('timeStr').value.trim(),
        desc: document.getElementById('desc').value.trim()
    };

    try {
        const res = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            lastGeneratedData = data;
            // Update Preview
            document.getElementById('previewImg').src = data.png_url + '?t=' + new Date().getTime();
            document.getElementById('btnDownloadPng').href = data.png_url;
            document.getElementById('btnDownloadPdf').href = data.pdf_url;

            // WhatsApp link
            const waMsg = `*🏔️ WW | Himachal '27 — Mountains & Memories 🏔️*\\n\\nHey *${data.name}*, your payment has been *VERIFIED & CONFIRMED*! 🎉\\n\\n💰 *Amount Credited:* ₹${Number(data.amount).toLocaleString('en-IN')}\\n🏷️ *Payment Stage:* ${data.stage}\\n📉 *Remaining Balance:* ₹${data.balance}\\n\\nAttached is your official invoice copy. Welcome aboard! ❄️✨`;
            document.getElementById('btnWhatsApp').href = `https://api.whatsapp.com/send?text=${encodeURIComponent(waMsg)}`;

            document.getElementById('resultCard').style.display = 'block';
            document.getElementById('resultCard').scrollIntoView({ behavior: 'smooth' });

            // Fetch next invoice number
            const nextRes = await fetch('/api/next-no');
            const nextData = await nextRes.json();
            document.getElementById('invNo').value = nextData.next_no;
            document.getElementById('custName').value = '';

            showToast('Invoice Generated: ' + data.inv_no);
            loadHistory();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (err) {
        alert('Failed to connect to server: ' + err);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '⚡ Generate Official Invoice';
    }
}

function copyWhatsAppTemplate() {
    if (!lastGeneratedData) return;
    const waMsg = `*🏔️ WW | Himachal '27 — Mountains & Memories 🏔️*\\n\\nHey *${lastGeneratedData.name}*, your payment has been *VERIFIED & CONFIRMED*! 🎉\\n\\n💰 *Amount Credited:* ₹${Number(lastGeneratedData.amount).toLocaleString('en-IN')}\\n🏷️ *Payment Stage:* ${lastGeneratedData.stage}\\n📉 *Remaining Balance:* ₹${lastGeneratedData.balance}\\n\\nAttached is your official invoice copy. Welcome aboard! ❄️✨`;
    navigator.clipboard.writeText(waMsg.replace(/\\\\n/g, '\\n'));
    showToast('WhatsApp confirmation message copied!');
}

function showToast(msg) {
    const t = document.getElementById('toast');
    t.innerText = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 3000);
}

async function deleteCurrentInvoice() {
    if (!lastGeneratedData) return;
    deleteInvoice(lastGeneratedData.inv_no, lastGeneratedData.name);
}

async function deleteInvoice(invNo, name) {
    if (!confirm(`Are you sure you want to delete invoice ${invNo} (${name})?\n\nThis will permanently delete the invoice files and automatically recover the invoice counter if this was the latest invoice.`)) {
        return;
    }
    try {
        const res = await fetch('/api/delete-invoice', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ inv_no: invNo })
        });
        const data = await res.json();
        if (data.success) {
            showToast(`Invoice ${invNo} deleted!`);
            if (lastGeneratedData && lastGeneratedData.inv_no === invNo) {
                document.getElementById('resultCard').style.display = 'none';
                lastGeneratedData = null;
            }
            if (data.next_no) {
                document.getElementById('invNo').value = data.next_no;
            }
            loadHistory();
        } else {
            alert('Error: ' + (data.error || 'Failed to delete invoice'));
        }
    } catch (e) {
        alert('Network error deleting invoice: ' + e);
    }
}

async function loadHistory() {
    try {
        const res = await fetch('/api/history');
        const data = await res.json();
        const list = document.getElementById('historyList');
        if (!data.history || data.history.length === 0) {
            list.innerHTML = '<p style="font-size: 0.85rem; color: #8b949e; text-align: center; padding: 12px;">No invoices generated yet.</p>';
            return;
        }
        list.innerHTML = data.history.map(item => `
            <div class="history-item">
                <div class="hist-info">
                    <h4>${item.name}</h4>
                    <p>${item.inv_no} • ${item.stage} • ₹${item.amount} (${item.date})</p>
                </div>
                <div class="hist-actions">
                    <a href="/download/${item.png_name}" target="_blank" class="hist-icon-btn">PNG</a>
                    <a href="/download/${item.pdf_name}" target="_blank" class="hist-icon-btn">PDF</a>
                    <button type="button" onclick="deleteInvoice('${item.inv_no}', '${item.name}')" class="hist-icon-btn hist-del-btn" title="Delete Invoice">🗑️</button>
                </div>
            </div>
        `).join('');
    } catch (e) {}
}
</script>

</body>
</html>
"""

def extract_filename(val):
    if not val:
        return ""
    return re.split(r'[\\/]', str(val).strip())[-1]

def read_history_records():
    """Reads history from CSV."""
    records = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
                if len(rows) > 1:
                    for r in reversed(rows[1:]):
                        if len(r) >= 10:
                            records.append({
                                "date": r[2],
                                "inv_no": r[1],
                                "name": r[3],
                                "desc": r[4],
                                "stage": r[5],
                                "amount": r[6],
                                "balance": r[7],
                                "pdf_name": extract_filename(r[8]),
                                "png_name": extract_filename(r[9])
                            })
        except Exception:
            pass
    return records[:15]

@app.route('/')
def index():
    today_date = datetime.now().strftime("%d/%m/%Y")
    current_time = datetime.now().strftime("%H:%M")
    next_inv = get_next_invoice_number()
    history = read_history_records()
    return render_template_string(
        HTML_TEMPLATE,
        next_inv_no=next_inv,
        today_date=today_date,
        current_time=current_time,
        history=history
    )

@app.route('/ping')
@app.route('/health')
def ping():
    return jsonify({
        "status": "awake",
        "service": "Wanderworld Invoice Generator",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/api/next-no')
def api_next_no():
    return jsonify({"next_no": get_next_invoice_number()})

@app.route('/api/history')
def api_history():
    return jsonify({"history": read_history_records()})

@app.route('/api/delete-invoice', methods=['POST'])
def api_delete_invoice():
    try:
        data = request.json or {}
        inv_no = data.get("inv_no", "").strip()
        if not inv_no:
            return jsonify({"success": False, "error": "Invoice number required"}), 400

        success, msg = delete_invoice_record(inv_no)
        if not success:
            return jsonify({"success": False, "error": msg}), 404

        next_no = get_next_invoice_number()
        return jsonify({
            "success": True,
            "message": msg,
            "next_no": next_no
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def api_generate():
    try:
        data = request.json
        name = data.get("name", "").strip()
        if not name:
            return jsonify({"success": False, "error": "Name is required"}), 400

        amount = float(data.get("amount", 999.0))
        stage = data.get("stage", "Booking").strip()
        balance = data.get("balance", "13,700/-").strip()
        inv_no = data.get("inv_no", "").strip() or None
        date_str = data.get("date", "").strip() or None
        time_str = data.get("time", "").strip() or None
        desc = data.get("desc", "Himachal Winter Trip 2027").strip()

        pdf_path, png_path = create_invoice(
            customer_name=name,
            amount=amount,
            payment_stage=stage,
            remaining_balance=balance,
            invoice_no=inv_no,
            date_str=date_str,
            time_str=time_str,
            description=desc,
            auto_increment=True
        )

        png_filename = os.path.basename(png_path)
        pdf_filename = os.path.basename(pdf_path)

        return jsonify({
            "success": True,
            "name": name,
            "inv_no": inv_no or os.path.splitext(pdf_filename)[0].split('_')[0],
            "stage": stage,
            "amount": amount,
            "balance": balance,
            "png_url": f"/download/{png_filename}",
            "pdf_url": f"/download/{pdf_filename}"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    clean_filename = extract_filename(filename)
    return send_from_directory(OUTPUT_DIR, clean_filename, as_attachment=False)

def print_banner(port=5000):
    local_ip = get_local_ip()
    url = f"http://{local_ip}:{port}"
    localhost_url = f"http://localhost:{port}"

    print("\n" + "=" * 65)
    print("      WANDERWORLD HOLIDAYS - MOBILE INVOICE DASHBOARD")
    print("=" * 65)
    print(f"\n[+] Dashboard is LIVE!")
    print(f"    Laptop Browser : {localhost_url}")
    print(f"    Phone Browser  : {url}")
    print("\n[+] Scan QR Code on your Phone Camera to open instantly:\n")

    try:
        import qrcode
        qr = qrcode.QRCode(border=1)
        qr.add_data(url)
        qr.make(fit=True)
        qr.print_ascii(invert=True)
    except Exception:
        pass

    print("\n" + "=" * 65)
    print(f"Tip: Make sure your phone is on the same WiFi / Mobile Hotspot!")
    print("=" * 65 + "\n")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print_banner(port)
    app.run(host='0.0.0.0', port=port, debug=False)
