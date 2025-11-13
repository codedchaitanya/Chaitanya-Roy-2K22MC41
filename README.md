# 🚀 Boostly - Student Recognition System

A Django-based recognition and credit management platform for students.

## Demo
<img width="1440" height="900" alt="Screenshot 2025-11-13 at 9 43 59 AM" src="https://github.com/user-attachments/assets/7243b7fa-a865-4390-9a9a-8df63d74b7b4" />
<img width="1440" height="900" alt="Screenshot 2025-11-13 at 9 44 12 AM" src="https://github.com/user-attachments/assets/8921bafc-b1c3-477a-a64d-a8959d91e91b" />
<img width="1440" height="900" alt="Screenshot 2025-11-13 at 9 44 20 AM" src="https://github.com/user-attachments/assets/b7c5def2-df96-4f57-8064-6dcf919bb6cf" />
<img width="1440" height="900" alt="Screenshot 2025-11-13 at 9 44 28 AM" src="https://github.com/user-attachments/assets/bcdd8a64-07bc-4d60-93fa-4c4d7c01ea98" />
<img width="1440" height="900" alt="Screenshot 2025-11-13 at 9 41 04 AM" src="https://github.com/user-attachments/assets/66845a67-019e-4486-898f-7c963315ba5b" />


##  Quick Start

### Prerequisites
- Python 3.9+
- pip (Python package manager)

### Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd boostly

# 2. Install Django
pip install django==4.2.26

# 3. Run database migrations
python manage.py migrate

# 4. Start the development server
python manage.py runserver 
```

### Access the Application
Open your browser and navigate to: **http://localhost:8001/**

### Test Credentials

**Students** (Password: `test123`)
- `alice_smith`
- `bob_jones`
- `carol_williams`
- `david_brown`
- `Chaitanya`

**Admin** (Password: `admin123`)
- `admin` - Access admin panel at http://localhost:8001/admin/

---

## ✨ Features

- **🎓 Recognition System** - Send credits (1-100) to fellow students with personalized messages
- **📊 Leaderboard** - Track top performers ranked by credits received and recognition count
- **💰 Credit Redemption** - Convert credits to vouchers (₹5 per credit)
- **👍 Endorsements** - Endorse recognitions from other students
- **📅 Monthly Limits** - 100 credits per month with automatic reset
- **🔐 Secure Authentication** - Custom student login with session management

---

## 📡 API Endpoints

### Public Routes
```
GET  /                    # Home page
GET  /login/              # Login page
POST /login/              # Login submission
```

### Authenticated Routes
```
GET  /dashboard/          # User dashboard with balance & activity
GET  /recognize/          # Recognition form
POST /recognize/          # Send recognition
GET  /leaderboard/        # Student rankings
GET  /redeem/             # Redemption form
POST /redeem/             # Redeem credits
GET  /<recognition_id>/   # Recognition detail page
GET  /logout/             # Logout
```

### Admin Routes
```
GET  /admin/              # Django admin panel
```

---

## 🗄️ Database Schema

### Models Overview

**User** (Django built-in)
- Standard Django authentication model
- Fields: username, first_name, last_name, password

**CreditBalance**
- `student` - ForeignKey to User
- `available_credits` - IntegerField (default: 100)
- `monthly_sent` - IntegerField (default: 0, max: 100)

**Recognition**
- `from_student` - ForeignKey to User (sender)
- `to_student` - ForeignKey to User (recipient)
- `credits` - IntegerField (1-100)
- `message` - CharField (max 500 chars)
- `created_at` - DateTimeField (auto)

**Redemption**
- `student` - ForeignKey to User
- `credits_redeemed` - IntegerField
- `rupees_value` - DecimalField (credits × ₹5)
- `status` - CharField (default: "completed")
- `created_at` - DateTimeField (auto)

**Endorsement**
- `recognition` - ForeignKey to Recognition
- `endorsed_by` - ForeignKey to User
- `created_at` - DateTimeField (auto)
- Constraint: Unique per (recognition, user)

---

## 📂 Project Structure

```
boostly/
├── manage.py                 # Django CLI
├── db.sqlite3               # Database
├── myproject/               # Project settings
│   ├── settings.py          # Configuration
│   ├── urls.py              # Root URL routing
│   └── wsgi.py              # WSGI config
└── base/                    # Main app
    ├── models.py            # Database models
    ├── views.py             # Business logic
    ├── forms.py             # Form definitions
    ├── urls.py              # App routing
    ├── admin.py             # Admin config
    ├── templates/base/      # HTML templates
    │   ├── base.html
    │   ├── home.html
    │   ├── login.html
    │   ├── dashboard.html
    │   ├── recognize.html
    │   ├── leaderboard.html
    │   ├── redeem.html
    │   └── detail.html
    └── migrations/          # DB migrations
```

---

## 🔧 Business Rules

### Recognition
- Cannot recognize yourself
- Max 100 credits per transaction
- Max 100 credits sent per month
- Must have sufficient balance
- Message required (max 500 characters)

### Leaderboard
- Ranked by: Credits received → Recognition count → Name
- Shows all active students
- Real-time updates

### Redemption
- Conversion: ₹5 per credit
- Instant balance deduction
- History tracked permanently

### Monthly Reset
```bash
python manage.py reset_monthly_credits
```
- Resets `monthly_sent` to 0 for all users
- Carries forward up to 50 unused credits
- Formula: `new_balance = 100 + min(50, current_balance - 100)`

---

## 🛠️ Common Commands

### Create a New Student
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User
from base.models import CreditBalance

user = User.objects.create_user(
    username='newstudent',
    first_name='New',
    last_name='Student',
    password='test123'
)

CreditBalance.objects.create(student=user, available_credits=100, monthly_sent=0)
```

### Check Balances
```bash
python manage.py shell
```
```python
from base.models import CreditBalance
for cb in CreditBalance.objects.all():
    print(f"{cb.student.username}: {cb.available_credits} credits")
```

### View Recognition History
```bash
python manage.py shell
```
```python
from base.models import Recognition
for r in Recognition.objects.all():
    print(f"{r.from_student.username} → {r.to_student.username}: {r.credits} credits")
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find and kill process
lsof -i :8001
kill -9 <PID>

# Or use different port
python manage.py runserver 8002
```

### Database Issues
```bash
# Remove lock files
rm db.sqlite3-wal db.sqlite3-shm

# Reset migrations (if needed)
python manage.py migrate --run-syncdb
```

### Static Files Not Loading
```bash
python manage.py collectstatic
```
✅ Production Ready  
**Version:** 1.0  
**Last Updated:** November 13, 2025
