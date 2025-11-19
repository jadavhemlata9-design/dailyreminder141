# -------------------------------------------------------------
# 📱 Streamlit SMS + WhatsApp Reminder App (WORKING AUTO SCHEDULER)
# -------------------------------------------------------------

import streamlit as st
import json
from datetime import datetime
from twilio.rest import Client
from streamlit_autorefresh import st_autorefresh   # <-- AUTO REFRESH

# -------------------------------------------------------------
# 🔑 TWILIO DETAILS
# -------------------------------------------------------------
TWILIO_ACCOUNT_SID = "ACe855d3519d798fdb8d4017b8692f0860"
TWILIO_AUTH_TOKEN = "b28ef14855ce695a499ce9e669578180"

TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"
TWILIO_SMS_FROM = "+18542013278"

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

FILE_NAME = "all_reminders.json"

# -------------------------------------------------------------
# 🗂 Load reminders
# -------------------------------------------------------------
def load_reminders():
    try:
        with open(FILE_NAME, "r") as f:
            return json.load(f)
    except:
        return []

# -------------------------------------------------------------
# 💾 Save reminders
# -------------------------------------------------------------
def save_reminders(reminders):
    with open(FILE_NAME, "w") as f:
        json.dump(reminders, f, indent=2)

# -------------------------------------------------------------
# 💬 Send WhatsApp
# -------------------------------------------------------------
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

# -------------------------------------------------------------
# 📱 Send SMS
# -------------------------------------------------------------
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

# -------------------------------------------------------------
# SESSION STATE
# -------------------------------------------------------------
if "reminders" not in st.session_state:
    st.session_state["reminders"] = load_reminders()

# -------------------------------------------------------------
# AUTO REFRESH EVERY 60 SEC
# -------------------------------------------------------------
st_autorefresh(interval=60000, key="scheduler_refresh")

# -------------------------------------------------------------
# UI
# -------------------------------------------------------------
st.title("📩 SMS + WhatsApp Reminder App (Auto Scheduler)")

reminder_text = st.text_input("Enter your reminder message:")
phone_number = st.text_input("Enter phone number (+91...)")

delivery_method = st.radio("Send Using:", ["WhatsApp", "SMS"])

date_sel = st.date_input("Select reminder date:")
time_str = st.text_input("Enter time (24H format HH:MM)", value="09:00")

# -------------------------------------------------------------
# SAVE REMINDER
# -------------------------------------------------------------
if st.button("Save Reminder"):
    try:
        user_time = datetime.strptime(time_str, "%H:%M").time()
        send_datetime = datetime.combine(date_sel, user_time)

        st.session_state["reminders"].append({
            "text": reminder_text,
            "phone": phone_number,
            "method": delivery_method,
            "datetime": send_datetime.strftime("%Y-%m-%d %H:%M"),
            "sent": False
        })

        save_reminders(st.session_state["reminders"])
        st.success("Reminder saved!")

    except:
        st.error("Invalid time format. Use HH:MM")

# -------------------------------------------------------------
# DISPLAY REMINDERS
# -------------------------------------------------------------
st.subheader("📁 Saved Reminders")

for i, r in enumerate(st.session_state["reminders"]):

    st.write(f"**Message:** {r['text']}")
    st.write(f"**Phone:** {r['phone']}")
    st.write(f"**Method:** {r['method']}")
    st.write(f"**When:** {r['datetime']}")
    st.write(f"**Sent:** {'Yes' if r['sent'] else 'No'}")

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
            st.error(msg)

    st.write("---")

# -------------------------------------------------------------
# AUTO SCHEDULER
# -------------------------------------------------------------
st.subheader("⏱ Auto Scheduler Status:")

current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
st.write(f"Current Time: **{current_time}**")

for r in st.session_state["reminders"]:

    if r["datetime"] == current_time and not r["sent"]:

        st.warning(f"Sending scheduled message: {r['text']}")

        if r["method"] == "WhatsApp":
            ok, msg = send_whatsapp(r["phone"], r["text"])
        else:
            ok, msg = send_sms(r["phone"], r["text"])

        if ok:
            r["sent"] = True
            save_reminders(st.session_state["reminders"])
            st.success("Message sent automatically!")
        else:
            st.error(msg)
