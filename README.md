# Django SMS Web Application (`sms_project`)

**Course:** IT 120 – Integrative Programming and Technologies  
**Institution:** Caraga State University (CSU) – College of Computing and Information Sciences  
**Program:** Bachelor of Science in Information Technology (BSIT)  
**Academic Year / Term:** 2026–2027  
**Activity:** Group Laboratory Assignment – Build a Django Application for Sending SMS  
**SMS Gateway Provider:** [Textlink SMS](https://textlinksms.com/)  
**Database Engine:** PostgreSQL 18.x (Managed via pgAdmin 4)  

---

## 📖 Table of Contents
1. [Project Overview](#-project-overview)
2. [Key Features & Capabilities](#-key-features--capabilities)
3. [System Architecture & Data Flow](#-system-architecture--data-flow)
4. [Technology Stack](#-technology-stack)
5. [Group Members & Role Distribution](#-group-members--role-distribution)
6. [Prerequisites & System Requirements](#-prerequisites--system-requirements)
7. [PostgreSQL & pgAdmin 4 Setup Guide](#-postgresql--pgadmin-4-setup-guide)
8. [Textlink SMS Gateway Configuration](#-textlink-sms-gateway-configuration)
9. [Step-by-Step Installation & Local Run Guide](#-step-by-step-installation--local-run-guide)
10. [Database Schema (`SMSLog`)](#-database-schema-smslog)
11. [Testing Scenarios & Quality Assurance](#-testing-scenarios--quality-assurance)
12. [Video Demonstration Guide & Checklist (3–10 Minutes)](#-video-demonstration-guide--checklist-310-minutes)
13. [Security & Best Practices](#-security--best-practices)

---

## 🌟 Project Overview

This web application is developed to fulfill the core requirements of **IT 120 (Integrative Programming and Technologies)**. It provides a secure, robust, and responsive web portal that allows users to compose and dispatch real SMS messages to cellular mobile phones via the **Textlink SMS REST API** (`https://textlinksms.com/`).

Unlike mock or ephemeral systems, all outbound SMS attempts—both successful deliveries and gateway rejections—are persistently audited and logged into a relational **PostgreSQL** database. The system adheres to enterprise Django architectural patterns: separation of concerns between views, forms, and service layers (`services.py`), strict security isolation for credentials via `.env`, and an interactive user experience using **Bootstrap 5** and real-time JavaScript utilities.

---

## ⚡ Key Features & Capabilities

### Core Requirements
- **SMS Composition Portal:** Responsive form with dedicated inputs for the destination phone number and message text body.
- **Strict Input Sanitization & Validation:**
  - Validates Philippine local numbers (`09XXXXXXXXX`), international formats (`+639XXXXXXXXX`), and global E.164 numbers.
  - Automatically strips hyphens, parentheses, and spaces.
  - Rejects blank, whitespace-only, or empty submissions.
  - Enforces standard SMS character boundaries.
- **Textlink REST Gateway Service:** Modular client layer (`sms_app/services.py`) handling JSON payloads, Bearer authorization, connection timeouts, and HTTP status code classification.
- **Comprehensive Error Handling:** User-friendly flash banners for missing credentials, provider authentication errors (401/403), insufficient account credits (402), bad parameters (400), or server timeouts (504).
- **Secure Environment Management:** Sensitive keys and database passwords are kept strictly in `.env` (ignored by Git) and loaded via `python-dotenv`.

### Bonus / Enhanced Features
- **PostgreSQL Audit Log Dashboard:** Complete history table with timestamp, recipient, message excerpt, color-coded status badges (`SENT` / `FAILED`), gateway HTTP response codes, and modal popups showing raw JSON responses.
- **Search, Filter & Pagination:** Filter history records by status (`SENT` vs. `FAILED`), search by recipient phone number or message keywords, and navigate through paginated results (10 per page).
- **Real-Time Interactive Character Counter:** Live JavaScript counter calculating character count and SMS segment credit consumption (`1 credit` for $\le 160$ chars; `2 credits` for $161-320$ chars; `3 credits` for $321-480$ chars).
- **Live Smartphone UI Preview:** Real-time visual message bubble synchronizing with keystrokes as the user composes the SMS.
- **Automated Test Suite:** 20 comprehensive unit tests covering forms, service mock calls, models, views, and edge cases.

---

## 🏗️ System Architecture & Data Flow

```text
[ Web Browser (Bootstrap 5 + JS) ]
              │
              │  1. HTTP POST (CSRF Token, Recipient, Message)
              ▼
[ Django View (SendSMSView) ]
              │
              │  2. Execute Clean & Validation Rules
              ▼
[ Django Form (SMSForm) ]
              │
         Valid? ───► No ───► Re-render form with inline field errors
              │ Yes
              ▼
[ Service Layer (TextlinkSMSService) ]
              │
              │  3. Formulate Bearer Auth Header & JSON Payload
              ▼
[ External Gateway: Textlink SMS REST API ]
              │
              │  4. Returns HTTP 200/201 (Success) OR 400/401/402/500 (Error)
              ▼
[ Database Layer: PostgreSQL (sms_db) ]
              │
              │  5. Save SMSLog (recipient, message, status, response_code, timestamp)
              ▼
[ Feedback & UI Render ]
   ├── If Success: Flash success alert & redirect to SMS History Dashboard
   └── If Error: Flash error banner with diagnostic provider message
```

---

## 🛠️ Technology Stack

| Layer | Technology | Details |
| :--- | :--- | :--- |
| **Backend Framework** | Python 3.10+ / Django 5.x–6.x | High-level Python web framework |
| **Database Engine** | PostgreSQL 16+ / 18.x | Enterprise Object-Relational Database |
| **Database GUI** | pgAdmin 4 | Database administration and query tool |
| **Database Adapter** | `psycopg2-binary` | Python-to-PostgreSQL connection engine |
| **SMS Gateway API** | Textlink SMS REST API | Cellular message delivery gateway |
| **HTTP Client** | `requests` | Synchronous REST client with timeouts |
| **Configuration** | `python-dotenv` | Twelve-factor `.env` credential management |
| **Frontend Framework** | Bootstrap 5.3.3 + Bootstrap Icons | Modern, mobile-first responsive UI |
| **Client Scripting** | Vanilla JavaScript (ES6) | Real-time counter and live phone preview |

---

## 👥 Group Members & Role Distribution

| Member Name | Student ID | Designated Project Role | Assigned Key Responsibilities |
| :--- | :--- | :--- | :--- |
| **Member 1 (Lead)** | `Jembo Magbanua` | **Full-Stack Lead & Gateway Architect** | Django architecture, `settings.py` integration, `TextlinkSMSService` client, REST API payload handling, and `.env` security management. |
| **Member 2** | `Jherzell Jane Sayahan` | **Database Engineer & Backend Developer** | PostgreSQL / pgAdmin database modeling, `SMSLog` schema, migrations, Django Admin customization, and audit dashboard pagination/filtering. |
| **Member 3** | `Regine Paclibar` | **Frontend Designer & QA Documentation Lead** | Bootstrap 5 UI, live JavaScript character counter, smartphone mock-up preview, unit test execution, and demonstration video production. |

---

## 📋 Prerequisites & System Requirements

Ensure the following tools are installed on your workstation:
1. **Python 3.10 or higher** (Verify: `python --version`)
2. **PostgreSQL Server & pgAdmin 4** (Verify: `psql --version` or launch pgAdmin 4 from Start Menu)
3. **Git** (Verify: `git --version`)
4. **Internet connection** for downloading Python packages and communicating with the Textlink REST API.

---

## 🐘 PostgreSQL & pgAdmin 4 Setup Guide

### Step 1: Open pgAdmin 4
1. Launch **pgAdmin 4** from your Windows Start Menu.
2. Enter your master master password to unlock pgAdmin.

### Step 2: Connect to Your PostgreSQL Server
1. In the left sidebar (**Servers Browser**), expand **Servers**.
2. Click on **PostgreSQL 16** (or **PostgreSQL 18**).
3. If prompted, input the password for the default `postgres` user (e.g., `postgres` or the password you set during installation).

### Step 3: Create the Application Database (`sms_db`)
1. Right-click on **Databases** $\rightarrow$ **Create** $\rightarrow$ **Database...**
2. In the dialog:
   - **Database:** `sms_db`
   - **Owner:** `postgres`
3. Click **Save**.
4. You will now see `sms_db` listed in pgAdmin under Databases.

*(Optional SQL Command via pgAdmin Query Tool):*
```sql
CREATE DATABASE sms_db WITH OWNER postgres ENCODING 'UTF8';
```

---

## 🔑 Textlink SMS Gateway Configuration

1. Create or log in to your account at **[Textlink SMS](https://textlinksms.com/)**.
2. Navigate to your **Dashboard / API Settings**.
3. Copy your unique **API Key** (e.g., `tl_live_xxxxxxxxxxxxxxxx`).
4. Note your **Sender ID** (e.g., `IT120SMS` or default Textlink sender identifier).
5. Open your project `.env` file and insert these credentials:
   ```ini
   TEXTLINK_API_KEY=your_actual_textlink_api_key_here
   TEXTLINK_API_URL=https://textlinksms.com/api/send
   TEXTLINK_SENDER_ID=IT120SMS
   ```

> 💡 **Instructor / Sandbox Testing Note:**  
> If testing in an offline classroom environment or without active cellular credits, leaving `TEXTLINK_API_KEY=test_api_key_placeholder` automatically triggers the built-in **Gateway Simulation Engine**, allowing full functional verification and PostgreSQL logging without incurring real cellular fees.

---

## 🚀 Step-by-Step Installation & Local Run Guide

### 1. Clone or Open the Repository
```powershell
cd "D:\College_folder\BSIT4_CSU\IT_120\Group Assignment Build a Django Application for Sending SMS\project_file"
```

### 2. Set Up the Python Virtual Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate the virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1
# OR (Windows Command Prompt)
.\venv\Scripts\activate.bat
```

### 3. Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Create and Configure Environment Variables (`.env`)
Copy `.env.example` to `.env`:
```powershell
copy .env.example .env
```
Open `.env` in VS Code or Notepad and verify your PostgreSQL credentials:
```ini
SECRET_KEY=django-insecure-textlink-sms-project-key-bsit4-csu-2026
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL Database Configuration
DB_NAME=sms_db
DB_USER=postgres
DB_PASSWORD=your_actual_postgres_password
DB_HOST=localhost
DB_PORT=5432

# Textlink SMS Gateway
TEXTLINK_API_KEY=your_actual_textlink_api_key_here
TEXTLINK_API_URL=https://textlinksms.com/api/send
TEXTLINK_SENDER_ID=IT120SMS
```

### 5. Apply Database Migrations to PostgreSQL
```powershell
python manage.py makemigrations
python manage.py migrate
```
*This command connects to PostgreSQL and generates the `sms_app_smslog` table.*

### 6. Create an Administrative Superuser (Optional for Django Admin)
```powershell
python manage.py createsuperuser
```
Follow the interactive prompt to specify a username, email, and password.

### 7. Launch the Django Development Server
```powershell
python manage.py runserver
```

### 8. Access the Application in Your Web Browser
- **SMS Composition Portal:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **SMS Transmission History & Logs:** [http://127.0.0.1:8000/history/](http://127.0.0.1:8000/history/)
- **Django Admin Console:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🗄️ Database Schema (`SMSLog`)

The table `sms_app_smslog` stores persistent records for every outgoing message attempt:

| Field Name | Type | Key / Constraint | Description |
| :--- | :--- | :--- | :--- |
| `id` | `BIGSERIAL` | Primary Key | Unique autoincrement ID |
| `recipient` | `VARCHAR(20)` | Indexed, Not Null | Cleaned mobile number (e.g. `+639123456789`) |
| `message` | `TEXT` | Not Null | Complete message body |
| `status` | `VARCHAR(10)` | Indexed, Choices: `SENT`, `FAILED` | Delivery outcome |
| `response_code` | `INTEGER` | Nullable | Gateway HTTP code (e.g. `200`, `400`, `401`, `402`) |
| `gateway_response`| `TEXT` | Nullable | Raw JSON payload or diagnostic error details |
| `timestamp` | `TIMESTAMPTZ`| Indexed, Auto Now | Exact timestamp of dispatch |

---

## 🧪 Testing Scenarios & Quality Assurance

Run the automated test suite with:
```powershell
python manage.py test
```

### Manual Testing Scenarios Matrix

| Scenario # | Test Description | Input Data | Expected System Behavior |
| :---: | :--- | :--- | :--- |
| **TC-01** | Valid Philippine Local Number | `09171234567`, "Test message" | Normalizes to `+639171234567`, dispatches to Textlink, logs `SENT`, redirects with success banner. |
| **TC-02** | Valid International Number | `+639189876543`, "Hello IT 120" | Dispatches to Textlink, returns success, logs to DB. |
| **TC-03** | Phone Number Formatting | `0912-345-6789` (with dashes) | Sanitizer strips dashes to `09123456789` $\rightarrow$ `+639123456789`, validates successfully. |
| **TC-04** | Invalid Alphabetic Phone | `0912ABC4567` | Form rejects submission: *"Invalid phone number format."* Does not call gateway. |
| **TC-05** | Incomplete / Short Phone | `091234` | Form rejects submission due to insufficient length. |
| **TC-06** | Empty Message Body | Message: `   ` (spaces only) | Form rejects submission: *"SMS message body cannot be empty."* |
| **TC-07** | Character Counter Calculation | Type 175 characters | Badge changes to warning, displays `175 / 160 chars (2 credits)`. Real-time phone bubble updates. |
| **TC-08** | Message Limit Boundary | Type 481+ characters | Form rejects submission: *"Message length exceeds maximum limit of 480 characters."* |
| **TC-09** | Missing / Empty API Key | Remove `TEXTLINK_API_KEY` from `.env` | Gateway returns HTTP 401: *"Missing or unconfigured TEXTLINK_API_KEY."* Logged as `FAILED`. |
| **TC-10** | Database Audit Inspection | Visit `/history/` | Shows total stats, filtered status views, and modal details of the raw response. |

---

## 📹 Video Demonstration Guide & Checklist (3–10 Minutes)

As required by Section VII (Submission and Demonstration Guidelines) of the assignment, the video must be **between 3 and 10 minutes** long. Use this suggested script:

- [ ] **Part 1: Introduction (0:00 – 1:00)**
  - Introduce the course: IT 120 (Integrative Programming and Technologies).
  - Introduce group members and state each person's role.
  - State project objective: A Django SMS dispatch web application integrated with the Textlink REST API and PostgreSQL.
- [ ] **Part 2: Code Architecture & Security (1:00 – 2:30)**
  - Show `.env` and `.env.example` to demonstrate secure API key handling.
  - Walk through `sms_app/services.py` explaining how the Textlink REST API is called and how HTTP response codes are handled.
  - Show `sms_app/models.py` and `SMSLog` database schema.
- [ ] **Part 3: PostgreSQL & pgAdmin Demonstration (2:30 – 3:30)**
  - Open **pgAdmin 4**, show the `sms_db` database, and display the `sms_app_smslog` table.
- [ ] **Part 4: Live SMS Dispatch Walkthrough (3:30 – 5:30)**
  - Navigate to `http://127.0.0.1:8000/`.
  - Type a valid Philippine number (`09XXXXXXXXX`).
  - Demonstrate the **live JavaScript character counter** and **smartphone preview bubble** updating in real time.
  - Click **Send SMS Message**, observe the loading spinner, and show the success banner.
- [ ] **Part 5: Input Validation & Error Handling (5:30 – 7:00)**
  - Demonstrate form validation: enter an invalid phone number (`abc`), leave the message blank, and demonstrate inline validation error alerts.
  - Trigger an intentional error (e.g., empty API key) to show that the system logs `FAILED` with status code without crashing.
- [ ] **Part 6: History Dashboard & Django Admin (7:00 – 8:30)**
  - Open `http://127.0.0.1:8000/history/`. Show filters (`SENT`, `FAILED`) and modal popups with raw gateway responses.
  - Open `/admin/` to show Django's built-in administration interface for logs.
- [ ] **Part 7: Summary & Conclusion (8:30 – 9:30)**
  - Conclude by summarizing each member's contributions and what was learned regarding Django, REST API integration, and database management.

---

## 🔒 Security & Best Practices

1. **Never Commit Secrets:** The `.env` file is explicitly included in `.gitignore` so API keys, database passwords, and the Django secret key are never exposed to public GitHub repositories.
2. **Input Sanitization:** All user inputs pass through Django's validation engine before any external network requests or database writes are executed.
3. **Cross-Site Request Forgery (CSRF):** All POST forms include Django's secure `{% csrf_token %}` to prevent unauthorized cross-site request attacks.
4. **Resilient HTTP Communication:** REST requests to Textlink use explicit 10-second timeouts to protect application workers from hanging during network degradation.

---

*Submitted in partial fulfillment of the requirements for IT 120 – Integrative Programming and Technologies, Caraga State University.*

