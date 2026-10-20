# 🏪 Django Shop & Restaurant Inventory System

A lightweight, local, database-driven **Point of Sale (POS) and inventory registry** application built with Python and Django. This project implements full **CRUD architecture**, stateful user sessions, and global middleware role security.

## 🚀 Key Features

* **Create (C):** Manager-only dashboard to register new products with unique item codes, prices, and initial stock counts.
* **Read (R):** A clean cashier registry scanning screen to look up real-time prices and stock availability instantly.
* **Update (U):** Interactive session-based shopping cart that dynamically recalculates totals and automatically decrements stock counts in the database upon item scans.
* **Delete (D):** Interactive data tables allowing managers to completely purge discontinued items with security confirmations.
* **Global Security (Middleware):** Custom authorization pipeline that intercepts network requests to globally block regular users from accessing manager paths (`/manager/*`).

## 🛠️ Tech Stack & Environment

* **Language:** Python
* **Framework:** Django 5.x
* **Database:** SQLite (Local relational database)
* **Editor:** Zed Editor
* **OS:** Linux

## 📦 How to Install and Run Locally

Follow these steps to replicate this environment on your local machine:

1. **Clone the repository:**
   ```bash
   git clone https://github.com
   cd django-shop-inventory
   ```

2. **Set up and activate a Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install Django:**
   ```bash
   pip install django
   ```

4. **Apply database migrations & create an admin user:**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Fire up the development server:**
   ```bash
   python manage.py runserver
   ```

6. **Access the endpoints:**
   * Cashier Scanner Panel: `http://127.0.0`
   * Manager Inventory Dashboard: `http://127.0.0`
   * Django Admin Back-office: `http://127.0.0`
