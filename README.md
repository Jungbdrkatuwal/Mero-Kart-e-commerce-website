# 🛒 MeroKart – E-Commerce Website

MeroKart is a fully functional **Django-based e-commerce platform** that allows users to browse products, manage carts, place orders, and handle authentication securely.  
This project is built to demonstrate a complete e-commerce workflow including user accounts, product categories, search, and cart management.

---

## 🚀 Features
- ✅ User Registration & Authentication (Login/Signup)
- ✅ Product Categories
- ✅ Add to Cart / Remove from Cart
- ✅ Order Placement & Checkout
- ✅ Search & Filter Products
- ✅ Image Upload for Products
- ✅ Responsive Templates with HTML, CSS, JS
- ✅ SQLite Database (default, can be changed to PostgreSQL/MySQL)

---

## 📂 Project Structure
```
MeroKart/         -> Main project settings
accounts/         -> User authentication & profiles
carts/            -> Cart and checkout logic
category/         -> Product category management
media/photos/     -> Uploaded product images
orders/           -> Order processing and history
static/           -> Static files (CSS, JS, images)
store/            -> Product store, search, filtering
templates/        -> HTML templates
db.sqlite3        -> Default database
manage.py         -> Django management file
```

---

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/MeroKart.git
   cd MeroKart
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate   # On Windows
   source venv/bin/activate   # On Mac/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser (admin)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver

7. Don't Forgot to give star ✌️✌️


## 🔑 Tech Stack
- **Backend:** Python, Django
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite (default), PostgreSQL/MySQL (optional)
- **Authentication:** Django Auth System

---

## 🙌 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.

---

## 📜 License
This project is licensed under the MIT License – feel free to use and modify it.

---


👨‍💻 Developed by **Pusparaj Katuwal**
