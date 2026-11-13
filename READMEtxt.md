# 📱 How to Register and Use Your Phone Number for SMS

This guide explains **exactly where to put your mobile number** in the project files and how to connect it with **Textlink SMS** to send and receive text messages.

---

## 1. 📁 Where to Put Your Number in the Files (`.env`)

You can set your number inside the **[`.env`](file:///d:/College_folder/BSIT4_CSU/IT_120/Group%20Assignment%20Build%20a%20Django%20Application%20for%20Sending%20SMS/project_file/.env)** file on line **23**:

```ini
# Open project_file\.env and find this line:
DEFAULT_RECIPIENT_PHONE=09123456789
```

### Why put it here?
- Whenever you open or refresh the web page (**`http://127.0.0.1:8000/`**), the **Recipient Mobile Number** box will **automatically be pre-filled with your phone number**!
- You can change it at any time, or type a different classmate's/instructor's number directly in the web form.

### Supported Phone Number Formats:
- **Local Philippine format (11 digits):** `09123456789` or `09XXXXXXXXX`
- **International format (E.164):** `+639123456789` or `+639XXXXXXXXX`
- *(Dashes and spaces like `0912-345-6789` are also automatically cleaned and accepted).*

---

## 2. 🌐 Where to Put Your Number in the Web App

You do **not** need to restart the server every time you want to send a text to a different number!

1. Start your server (if not already running):
   ```powershell
   .\venv\Scripts\python.exe manage.py runserver
   ```
2. Open your browser: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**
3. On the left side of the screen, you will see the form:
   - **Recipient Mobile Number:** Type your number here (e.g., `09XXXXXXXXX`).
   - **Message Content:** Type your SMS text.
4. As you type, look at the **Live Smartphone Preview** on the right side — your number and message will appear live on the screen!
5. Click **Send SMS Message**.

---

## 3. 📡 How to Register Your Number on Textlink SMS (https://textlinksms.com/)

Textlink allows you to send real cellular SMS messages via their REST API or using an Android phone with your SIM card.

### Step 1: Create an Account
1. Visit **[https://textlinksms.com/](https://textlinksms.com/)** and Sign Up or Log In.

### Step 2: Register Your Device / Sender Number
1. In the Textlink Dashboard, go to **Devices** (or **Phone Numbers**).
2. If using your Android phone as the gateway:
   - Download the **Textlink Android APK / App** onto your phone.
   - Log into the app with your Textlink credentials.
   - Your Android phone's SIM card is now registered to dispatch and route SMS!

### Step 3: Get Your API Key
1. In the Textlink dashboard, navigate to **API Settings** or **Developer API**.
2. Generate and copy your **API Key** (e.g. `tl_live_xxxxxxxxxxxxxxxx`).
3. Paste it into your **[`.env`](file:///d:/College_folder/BSIT4_CSU/IT_120/Group%20Assignment%20Build%20a%20Django%20Application%20for%20Sending%20SMS/project_file/.env#L17)** file:
   ```ini
   TEXTLINK_API_KEY=your_actual_textlink_api_key_here
   ```
4. Save the `.env` file (`Ctrl + S`).

---

## 4. 🎮 Simulator / Demo Mode (No Registration or Balance Required)

If you don't have a paid Textlink balance or just want to test and record your demonstration video right now:

- Keep `TEXTLINK_API_KEY=test_api_key_placeholder` in `.env`.
- Any phone number you type will be:
  - Formatted and validated.
  - Successfully dispatched via the built-in **Simulator Engine**.
  - Logged into your **PostgreSQL** database (`sms_db`) under the **`SMSLog`** table.
  - Displayed on the **SMS History Dashboard** (`http://127.0.0.1:8000/history/`).

---

## 🎯 Quick Summary

| What you want to do | Where to do it |
| :--- | :--- |
| **Auto-fill your number for testing** | Add `DEFAULT_RECIPIENT_PHONE=09XXXXXXXXX` in [`.env`](file:///d:/College_folder/BSIT4_CSU/IT_120/Group%20Assignment%20Build%20a%20Django%20Application%20for%20Sending%20SMS/project_file/.env) |
| **Send SMS to any number** | Type it directly into the web form at [http://127.0.0.1:8000/](http://127.0.0.1:8000/) |
| **Register for live real cellular texts** | Set up device and get API key at [https://textlinksms.com/](https://textlinksms.com/) |
| **Check delivery history & PostgreSQL logs** | Visit [http://127.0.0.1:8000/history/](http://127.0.0.1:8000/history/) |

