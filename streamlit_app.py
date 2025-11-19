# -------------------------------------------------------------
# 📱 Streamlit SMS + WhatsApp Reminder App (Auto Scheduler, no extra libs)
# -------------------------------------------------------------

import streamlit as st
import json
from datetime import datetime
from twilio.rest import Client

# --------------------------
# TWILIO - replace with yours
# --------------------------
TWILIO_ACCOUNT_SID = "ACe855d3519d798fdb8d4017b8692f0860"
TWILIO_AUTH_TOKEN = "b28ef14855ce695a499ce9e669578180"
TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"
TWILIO_SMS_FROM = "+18542013278"

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

FILE_NAME = "all_reminders.json"

# --------------------------
# Helpers: load / save
# --------------------------
def load_reminders():
    try:
        with open(FILE_NAME, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_reminders(reminders):
    with open(FILE_NAME, "w") as f:
        json.dump(reminders, f, indent=2)

# --------------------------
# Helpers: send messages
# --------------------------
def send_whatsapp(to_phone, message):
    try:
        msg = client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_FROM,
            to=f"whatsapp:{to_phone}"
        )
        return True, msg.sid
    except Exception as e:
        return False, str(e)

def send_sms(to_phone, message):
    try:
        msg = client.messages.create(
            body=message,
            from_=TWILIO_SMS_FROM,
            to=to_phone
        )
        return True, msg.sid
    except Exception as e:
        return False, str(e)

# --------------------------
# Session state
# --------------------------
if "reminders" not in st.session_state:
    st.session_state["reminders"] = load_reminders()

# --------------------------
# Auto-refresh using meta tag (browser will reload page every 60s)
# --------------------------
# Put this near top so page reload happens automatically in browser.
# 60 seconds -> change content="60" to your preferred interval (in seconds).
st.markdown('<meta http-equiv="refresh" content="60">', unsafe_allow_html=True)

# --------------------------
# UI
# --------------------------
st.title("📩 SMS + WhatsApp Reminder App (Auto Scheduler)")

with st.form("add_reminder_form", clear_on_submit=True):
    reminder_text = st.text_input("Enter reminder message:", placeholder="Drink water")
    phone_number = st.text_input("Enter phone number with country code:", placeholder="+918888888888")
    delivery_method = st.radio("Send using:", ["WhatsApp", "SMS"])
    date_sel = st.date_input("Select reminder date:")
    time_str = st.text_input("Enter time (24H format HH:MM):", value="09:00")
    submitted = st.form_submit_button("Save Reminder")

if submitted:
    try:
        user_time = datetime.strptime(time_str, "%H:%M").time()
        send_datetime = datetime.combine(date_sel, user_time)
        new = {
            "text": reminder_text,
            "phone": phone_number,
            "method": delivery_method,
            "datetime": send_datetime.strftime("%Y-%m-%d %H:%M"),
            "sent": False
        }
        st.session_state["reminders"].append(new)
        save_reminders(st.session_state["reminders"])
        st.success("Reminder saved!")
    except Exception:
        st.error("Invalid time format — use HH:MM (24-hour).")

# --------------------------
# Display saved reminders
# --------------------------
st.subheader("📁 Saved Reminders")
if len(st.session_state["reminders"]) == 0:
    st.info("No reminders saved yet.")
else:
    for i, r in enumerate(st.session_state["reminders"]):
        st.write(f"**Message:** {r['text']}")
        st.write(f"**To:** {r['phone']}")
        st.write(f"**Method:** {r['method']}")
        st.write(f"**When:** {r['datetime']}")
        st.write(f"**Sent:** {'Yes' if r.get('sent', False) else 'No'}")

        if st.button(f"Send Now #{i}"):
            if r["method"] == "WhatsApp":
                ok, msg = send_whatsapp(r["phone"], r["text"])
            else:
                ok, msg = send_sms(r["phone"], r["text"])

            if ok:
                r["sent"] = True
                save_reminders(st.session_state["reminders"])
                st.success("Message sent!")
            else:
                st.error(f"Failed to send: {msg}")

        st.write("---")

# --------------------------
# Auto scheduler check
# --------------------------
st.subheader("⏱ Auto Scheduler Status")

# Use server-local current time. If hosting in different timezone, results follow server time.
current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
st.write(f"Current Time (server): **{current_time}**")
sent_any = False

for r in st.session_state["reminders"]:
    # equality check by minute string to avoid seconds mismatch
    if r["datetime"] == current_time and not r.get("sent", False):
        st.info(f"Sending scheduled message to {r['phone']}: {r['text']}")
        if r["method"] == "WhatsApp":
            ok, msg = send_whatsapp(r["phone"], r["text"])
        else:
            ok, msg = send_sms(r["phone"], r["text"])

        if ok:
            r["sent"] = True
            save_reminders(st.session_state["reminders"])
            st.success(f"{r['method']} message sent automatically!")
            sent_any = True
        else:
            st.error(f"Failed to send scheduled message: {msg}")

if not sent_any:
    st.write("No scheduled messages to send at this minute.")

# --------------------------
# Helpful note
# --------------------------
st.caption("Note: The page reloads every 60 seconds (browser-side). Keep the app open in a tab for automatic sending. "
           "Server time is used to match reminders — if your server is in a different timezone, convert times accordingly.")
