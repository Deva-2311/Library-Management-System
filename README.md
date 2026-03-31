# 📚 LibraryOS — Library Management System

A full-stack Library Management System built with **HTML + CSS + JavaScript** (frontend),
**Python + Flask** (backend), and **MySQL** (database).

---

## 🗂️ Project Structure

```
library_mgmt/
├── app.py               ← Flask backend (all routes & logic)
├── schema.sql           ← MySQL database schema + seed data
├── setup_users.py       ← One-time script to hash demo passwords
├── requirements.txt     ← Python dependencies
├── templates/
│   ├── base.html        ← Base layout (sidebar, topbar, flash messages)
│   ├── login.html       ← Login page
│   ├── register.html    ← Registration page
│   ├── dashboard.html   ← Dashboard with stats & activity
│   ├── books.html       ← Book catalogue (grid view)
│   ├── book_form.html   ← Add / Edit book form
│   ├── reservations.html← Reservations list & management
│   ├── users.html       ← Members management (admin only)
│   └── profile.html     ← User profile & borrow history
└── static/
    ├── css/style.css    ← Full stylesheet (Forest/Gold theme)
    └── js/main.js       ← Client-side interactions
```

---

## ⚙️ Setup Instructions

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 2. Create MySQL database
```bash
mysql -u root -p < schema.sql
```

### 3. Update DB credentials in app.py
Open `app.py` and find `DB_CONFIG`:
```python
DB_CONFIG = {
    'host': 'localhost',
    'database': 'library_db',
    'user': 'root',
    'password': 'yourpassword',   # ← Change this
}
```

### 4. Hash demo passwords (run once)
```bash
# Also update DB credentials in setup_users.py first
python setup_users.py
```

### 5. Run the application
```bash
python app.py
```

Open browser → **http://localhost:5000**

---

## 🔑 Demo Login Credentials

| Role   | Email                 | Password   |
|--------|-----------------------|------------|
| Admin  | admin@library.com     | admin123   |
| Member | arjun@email.com       | member123  |

---

## ✨ Features

### For Members
- Register & Login securely
- Browse the full book catalogue
- Search books by title, author, ISBN
- Filter by genre
- Reserve available books (14-day loan period)
- View own reservation history & fines
- Update profile & change password

### For Admins
- Everything members can do, plus:
- Add, edit, delete books
- View all reservations across all members
- Issue books (reserved → borrowed)
- Process returns (calculates overdue fines: ₹2/day)
- Manage members (activate/deactivate, promote to admin)
- Live dashboard with stats & activity feed
- Trigger overdue status update via API

---

## 🧩 Tech Stack

| Layer        | Technology                          |
|--------------|-------------------------------------|
| Frontend     | HTML5, CSS3, Vanilla JavaScript     |
| Backend      | Python 3.10+, Flask 3.0             |
| Database     | MySQL 8.0                           |
| DB Connector | mysql-connector-python              |
| Auth         | Werkzeug password hashing + sessions|

---

## 📌 Notes for Submission

- All passwords are **hashed** using PBKDF2-SHA256 (Werkzeug)
- Session management uses Flask's signed cookies
- Fine calculation: **₹2 per overdue day** (automated on return)
- The `/api/stats` endpoint returns live JSON stats
- Responsive design works on mobile, tablet, and desktop
# Library-Management-System
