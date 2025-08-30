

<h1>
<div style="display: flex; align-items: center;">
<img src="SMS Automation.png" width="200" alt="SpareChange Logo" style="margin-right: 15px;">
<span>SpareChange</span>
</div>
</h1>

Welcome to **SpareChange** 💰✨ – an AI-powered **FinTech platform** that helps you save effortlessly and access **micro-loans** with dignity. By rounding up your daily UPI transactions and pooling them into savings, SpareChange builds financial resilience and enables **P2P micro-lending** for underbanked communities, students, and gig workers.

---

## 💡 What is SpareChange?

**SpareChange** is more than a savings app — it’s a **smart companion for financial inclusion**.
It combines:

* **Automatic Round-Up Savings** 🪙 from UPI transactions.
* **P2P Micro-Lending** 🤝 powered by pooled savings.
* **AI-driven Credit Scoring** 📊 to ensure safe and fair lending.

Our goal is to make savings and micro-credit **safe, effortless, and stigma-free**.

---

## ✨ Key Features

* 💰 **Automatic Round-Up Savings**
* 🤝 **P2P Micro-Lending**
* 🤖 **AI-Powered Safeguards**
* 📊 **Transparent Workflows**
* 🌍 **Financial Inclusion**

---

## 🏗️ Project Structure

```
SpareChange/
│── backend/                # FastAPI backend
│   ├── main.py             # FastAPI entry point
│   ├── crud.py             # CRUD operations
│   ├── database.py         # SQLite DB connection
│   ├── models.py           # SQLAlchemy models
│   ├── schemas.py          # Pydantic schemas
│
│── frontend/               # Frontend (HTML UI)
│   ├── index.html          # Landing page
│   ├── frontpage.html      # Dashboard
│
│── microsavings.db         # SQLite database
│── requirements.txt        # Dependencies
│── README.md               # Documentation
```

---

## ⚙️ Technical Details & Setup

### 🔧 1. Clone the Repository

```bash
git clone https://github.com/yourusername/SpareChange.git
cd SpareChange
```

### 🐍 2. Create a Virtual Environment (venv)

#### On Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

#### On Windows

```bash
python -m venv venv
venv\Scripts\activate
```

*(Make sure `venv` is activated — you should see `(venv)` in your terminal prompt.)*

### 📦 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 🚀 4. Run the FastAPI Backend

```bash
uvicorn backend.main:app --reload
```

* API Root → [http://127.0.0.1:8000](http://127.0.0.1:8000)
* Swagger UI → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* ReDoc → [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### 🎨 5. Open the Frontend

* Open `frontend/index.html` in your browser.

---

## 📡 API Endpoints (Examples)

### Savings

* `POST /savings/` → Add spare change savings
* `GET /savings/{user_id}` → Fetch savings balance

### Loans

* `POST /loan/request` → Request loan
* `POST /loan/repay` → Repay loan
* `GET /loan/history/{user_id}` → Loan history

### Users

* `POST /users/` → Register user
* `GET /users/{id}` → Fetch user info

---

## 👩‍💻 Creators

<div align="center" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 2rem; max-width: 900px; margin: 2rem auto;">

<div style="text-align: center;">
  <p style="margin-top: 0.5rem; font-weight: bold;">Ashish B</p>
</div>

<div style="text-align: center;">
  <p style="margin-top: 0.5rem; font-weight: bold;">Rayhana S</p>
</div>

<div style="text-align: center;">
  <p style="margin-top: 0.5rem; font-weight: bold;">Levana P Saju</p>
</div>

<div style="text-align: center;">
  <p style="margin-top: 0.5rem; font-weight: bold;">Cyriac James Boby</p>
</div>

</div>

---

## 📜 License

This project is licensed under the **MIT License**. See the [`LICENSE.md`](LICENSE) file for details.

---
