# -------------------------------------------------------------
# 📱 Streamlit SMS + WhatsApp Reminder App (WITH AUTO SCHEDULER)
# -------------------------------------------------------------

import streamlit as st
import json
from datetime import datetime
from twilio.rest import Client
import time

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
# 💬 Send WhatsApp message
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
# 📱 Send SMS message
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
# 🧠 Load into Session
# -------------------------------------------------------------
if "reminders" not in st.session_state:
    st.session_state["reminders"] = load_reminders()

# -------------------------------------------------------------
# 🌟 App Title
# -------------------------------------------------------------
st.title("📩 SMS + WhatsApp Reminder App (Auto Scheduler)")

# -------------------------------------------------------------
# 📝 User Inputs
# -------------------------------------------------------------
reminder_text = st.text_input("Enter your reminder message:", placeholder="Drink water")
phone_number = st.text_input("Enter phone number with country code:", placeholder="+918888888888")

delivery_method = st.radio("How do you want to send the reminder?", ["WhatsApp", "SMS"])

date_sel = st.date_input("Select reminder date")

time_str = st.text_input("Enter time (24H, HH:MM):", value="09:00")

# -------------------------------------------------------------
# 💾 Save Reminder
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
        st.success("Reminder saved successfully!")

    except:
        st.error("Incorrect time format. Use HH:MM like 14:30.")

# -------------------------------------------------------------
# 📋 Show Saved Reminders
# -------------------------------------------------------------
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
                st.success(f"{r['method']} message sent!")
            else:
                st.error("Failed: " + str(msg))

        st.write("---")

# -------------------------------------------------------------
# ⏰ AUTO-SCHEDULER (Runs every minute)
# -------------------------------------------------------------
st.subheader("⏱ Auto Scheduler Running...")

current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
st.write(f"Current Time: **{current_time}**")

for r in st.session_state["reminders"]:
    if r["datetime"] == current_time and not r.get("sent", False):

        st.warning(f"Sending scheduled message: {r['text']}")

        if r["method"] == "WhatsApp":
            ok, msg = send_whatsapp(r["phone"], r["text"])
        else:
            ok, msg = send_sms(r["phone"], r["text"])

        if ok:
            r["sent"] = True
            save_reminders(st.session_state["reminders"])
            st.success(f"{r['method']} message sent automatically!")
        else:
            st.error("Failed: " + msg)

# Refresh page every 60 seconds
st_autorefresh = st.experimental_rerun()
time.sleep(60)
