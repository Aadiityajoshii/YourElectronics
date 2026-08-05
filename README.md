# Your Electronixs — Full Stack Setup Guide

## 📁 Project Folder Structure

```
your_electronixs/
│
├── app.py                   ← Main Python Flask backend (all routes & database)
├── requirements.txt         ← Python packages to install
│
├── templates/               ← HTML pages (Jinja2 templates)
│   ├── base.html            ← Shared layout (navbar, footer, flash messages)
│   ├── index.html           ← Home page (hero, products, categories)
│   ├── login.html           ← Login page
│   ├── register.html        ← Register page
│   └── cart.html            ← Shopping cart page
│
├── static/
│   ├── css/
│   │   └── style.css        ← All styles (dark neon theme)
│   ├── js/
│   │   └── main.js          ← Product rendering, cart, animations
│   └── images/
│       └── products/        ← (Optional) save local product images here
│
└── instance/
    └── electronixs.db       ← SQLite database (auto-created on first run)
```

---

## 🚀 Step-by-Step Setup in VS Code

### STEP 1 — Install Python
1. Go to https://python.org/downloads → Download Python 3.11+
2. During install, **check "Add Python to PATH"** ✅
3. Open Terminal in VS Code: `python --version` → should show version

---

### STEP 2 — Install VS Code Extensions
Open VS Code → Extensions (Ctrl+Shift+X) → Install:
- **Python** (by Microsoft) — required
- **Pylance** — smart code hints
- **SQLite Viewer** — see your database visually
- **Live Server** — (optional, for static previews)

---

### STEP 3 — Open Project in VS Code
1. Open VS Code
2. File → Open Folder → Select the `your_electronixs` folder
3. You should see all files in the Explorer panel on the left

---

### STEP 4 — Create Virtual Environment
Open Terminal in VS Code (Ctrl+` backtick):

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

You'll see `(venv)` appear in your terminal — this means it's active ✅

---

### STEP 5 — Install Dependencies
With your virtual environment active:

```bash
pip install -r requirements.txt
```

This installs Flask, SQLAlchemy, and Werkzeug.

---

### STEP 6 — Run the Website

```bash
python app.py
```

You'll see:
```
✅ Products seeded!
 * Running on http://127.0.0.1:5000
```

Open your browser → go to **http://localhost:5000** 🎉

---

### STEP 7 — Using the Website
| Feature | How to access |
|---|---|
| Home Page | http://localhost:5000 |
| Register | Click "Register" in navbar |
| Login | Click "Login" in navbar |
| Add to Cart | Click "Add to Cart" on any product (must be logged in) |
| View Cart | Click "🛒 Cart" or floating cart button |
| Checkout | In Cart page → "Proceed to Checkout" |
| Search | Type in the search bar in navbar |
| Filter | Click category tabs above product grid |

---

## 🔧 How It Works (For Understanding)

### Backend (app.py)
- **Flask** handles all URLs (routes)
- **SQLAlchemy** manages the SQLite database
- **Session** keeps users logged in
- Routes: `/`, `/login`, `/register`, `/cart`, `/add-to-cart/<id>`, `/checkout`
- API: `/api/products?category=Laptops&search=apple`

### Frontend (templates + static)
- **base.html** — shared navbar, footer, canvas animations
- **index.html** — extends base, adds hero + products sections
- **main.js** — renders product cards from server data, handles cart AJAX
- **style.css** — full dark neon theme

### Database (SQLite)
Tables created automatically:
- `user` — stores registered users (passwords are hashed)
- `product` — all 12 products with real image URLs
- `cart_item` — links users to products in their cart
- `order` — placed orders history

---

## 🛠️ Common Issues & Fixes

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: flask` | Run `pip install -r requirements.txt` with venv active |
| `venv\Scripts\activate` not working (Windows) | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first |
| Port 5000 already in use | Change `app.run(debug=True, port=5001)` in app.py |
| Images not loading | They load from official brand CDNs — check internet connection |
| Database errors | Delete `instance/electronixs.db` and restart — it recreates automatically |

---

## 🌟 Next Steps to Expand
- Add product detail pages (`/product/<id>`)
- Add admin panel to add/edit products
- Integrate Razorpay for real payments
- Add address/shipping form at checkout
- Deploy to PythonAnywhere or Render.com (free hosting)
