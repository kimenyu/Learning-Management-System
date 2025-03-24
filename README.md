
# 🧠 Learning Management System Backend

A robust, scalable, and feature-rich **Learning Management System (LMS)** backend built with Django REST Framework (DRF). This project enables educational platforms to manage users, courses, content, quizzes, grading, and more through a clean RESTful API architecture.

---

## 🚀 Features

- **Role-Based Access Control**: Admin, Instructor, and Student roles with customized permissions.
- **Course Management**: Instructors can create, update, and publish courses.
- **Content Delivery**: Support for multimedia (PDFs, videos) and modular course design.
- **Quiz and Assessment System**: Quizzes with grading logic and student performance tracking.
- **Progress Tracking**: Students can track their learning journey.
- **Authentication & Authorization**:
  - JWT Authentication (`djangorestframework-simplejwt`)
  - Secure account creation and login via `djoser`
- **API Documentation**: Fully documented using `drf-spectacular` (OpenAPI 3).
- **Asynchronous Support**:
  - Real-time features powered by `channels` and `channels_redis`
  - Task queue powered by `Celery` and `Redis`
- **Cloud Integration**:
  - Media storage via Cloudinary
 
---

## 🛠 Tech Stack

- **Backend**: Django 5.1, Django REST Framework
- **Auth**: JWT
- **Async**: Redis
- **Storage**: Cloudinary
- **Database**: Default SQLite (easy to swap with PostgreSQL)

---

## 📁 Project Structure

```bash
LearningManagementSystem/
├── accounts/       # User management, roles, authentication
├── courses/        # Course models, views, enrollment
├── quizzes/        # Quiz creation, submission, grading
├── media/          # Uploaded content files
├── manage.py
├── requirements.txt
└── .env            
```

---

## 🔐 User Roles

- **Admin**: Full access to all features and user management
- **Instructor**: Can create courses, content, quizzes
- **Student**: Can enroll in courses, take quizzes, view progress

Custom user model is defined in `accounts.models.User`, extending `AbstractUser` with role support and UUID primary keys.

---

## 📦 Installation

### Prerequisites
- Python 3.10+
- pip
- Redis
- Cloudinary

### Setup Instructions

```bash
# Clone the repo
git clone https://github.com/kimenyu/LearningManagementSystem.git
cd LearningManagementSystem

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Then fill in your DB, secret keys, cloudinary config etc.

# Run migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

---

## 📑 API Documentation

- Swagger/OpenAPI: auto-generated using **drf-spectacular**
- Access it at `/api/schema/`, `api/docs/swagger/` and `api/docs/redoc/` after running the server.


## ☁️ Deployment Notes

- Easily deployable to platforms like **Render**, **Heroku**, or **DigitalOcean**
- Be sure to set production environment variables and switch database to PostgreSQL

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

## 👨‍💻 Author

**Njoroge Joseph**  
Backend Developer | Python | Django | REST APIs  
[GitHub](https://github.com/kimenyu)

---

## 🙌 Contributions

Pull requests and feature suggestions are welcome! Feel free to fork and contribute.