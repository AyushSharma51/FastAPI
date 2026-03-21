# ⚽ Football League Management API

A backend system built using **FastAPI** for managing football leagues, including players, teams, matches, statistics, and secure authentication.

---

## 🚀 Features

* Player CRUD
* Team CRUD
* Match Management
* Player Match Stats
* Team & Player Cumulative Stats
* Standings

---

## 🔐 Authentication

* OAuth2 Password Flow
* JWT-based authentication
* Protected routes
* Password hashing (Argon2)

---

## 📦 Tech Stack

* FastAPI
* SQLAlchemy
* SQLite / PostgreSQL
* OAuth2 + JWT
* Streamlit (Frontend)

---

## 📡 API Endpoints

### 🔐 Auth

* `POST /token`

### 👤 Users

* `GET /users/me/`
* `GET /users/me/items/`

### ⚽ Core

* `/players`
* `/teams`
* `/matches`
* `/match-stats`
* `/team-players`

---

## 🛠️ Setup (Ubuntu + Poetry)

### 1️⃣ Install Poetry

```bash
sudo apt update
sudo apt install python3-pip -y
pip install poetry
```

### 2️⃣ Clone Repository

```bash
git clone <your-repo-link>
cd football-api
```

### 3️⃣ Install Dependencies

```bash
poetry install
```

### 4️⃣ Activate Virtual Environment

```bash
poetry shell
```

---

## ▶️ Run Backend Server

```bash
uvicorn main:app --reload
```

---

## 💻 Run Frontend (Streamlit)

Make sure backend is running first.

```bash
streamlit run frontend.py
```

### ⚠️ Notes

* Ensure API base URL in frontend is correct (e.g., `http://127.0.0.1:8000`)
* Login is required to access protected routes
* Token is stored in session (Streamlit)

---

## 🔐 Using Authentication

1. Call `/token` with username & password
2. Get `access_token`
3. Use in header:

```
Authorization: Bearer <token>
```

---

## 📄 Summary

A RESTful API with secure JWT-based authentication and a Streamlit-based frontend for managing football league data.

---
