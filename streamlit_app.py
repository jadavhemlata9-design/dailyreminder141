# -------------------------------------------------------------
# 📱 Streamlit SMS + WhatsApp Reminder App
# Every line has simple comments for a 5th class student
# -------------------------------------------------------------

import streamlit as st              # Used to make the web app
import json                         # Used to save reminders as a file
from datetime import datetime       # Used to handle date and time
from twilio.rest import Client      # Used to send messages with Twilio

# -------------------------------------------------------------
# 🔑 TWILIO DETAILS (CHANGE TO YOUR OWN CREDENTIALS)
# -------------------------------------------------------------
TWILIO_ACCOUNT_SID = "ACe855d3519d798fdb8d4017b8692f0860"   # Your Twilio account ID
TWILIO_AUTH_TOKEN = "b28ef14855ce695a499ce9e669578180"      # Your Twilio secret token

# Twilio WhatsApp number (from Sandbox)
TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"

# Twilio SMS number (use your Twilio phone number)
TWILIO_SMS_FROM = "+18542013278"     # Replace with your Twilio SMS number

# Create Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# This file stores all reminders
FILE_NAME = "all_reminders.json"

# -------------------------------------------------------------
# 🗂 Load saved reminders from file
# -------------------------------------------------------------
def load_reminders():
    try:
        with open(FILE_NAME, "r") as f:
            return json.load(f)     # Read all reminders from file
    except:
        return []                   # If file doesn't exist, return empty list

# -------------------------------------------------------------
# 💾 Save reminders to file
# -------------------------------------------------------------
def save_reminders(reminders):
    with open(FILE_NAME, "w") as f:
        json.dump(reminders, f, indent=2)  # Write reminders into file

# -------------------------------------------------------------
# 💬 Send WhatsApp message
# -------------------------------------------------------------
def send_whatsapp(to_phone, message):
    try:
        msg = client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_FROM,
            to=f"whatsapp:{to_phone}"   # WhatsApp requires whatsapp: prefix
        )
        return True, msg.sid           # Return success and message ID
    except Exception as e:
        return False, str(e)           # Return error message

# -------------------------------------------------------------
# 📱 Send SMS message
# -------------------------------------------------------------
def send_sms(to_phone, message):
    try:
        msg = client.messages.create(
            body=message,
            from_=TWILIO_SMS_FROM,
            to=to_phone                # SMS does not need whatsapp: prefix
        )
        return True, msg.sid
    except Exception as e:
        return False, str(e)

# -------------------------------------------------------------
# 🧠 Load reminders into session memory
# -------------------------------------------------------------
if "reminders" not in st.session_state:
    st.session_state["reminders"] = load_reminders()

# -------------------------------------------------------------
# 🌟 App Title
# -------------------------------------------------------------
st.title("📩 SMS + WhatsApp Reminder App")
st.write("Set reminders that can be sent through SMS or WhatsApp!")

# -------------------------------------------------------------
# 📝 User Inputs
# -------------------------------------------------------------

# The message the user wants to be reminded about
reminder_text = st.text_input(
    "Enter your reminder message:",
    placeholder="Drink water"
)

# Where the message will be sent
phone_number = st.text_input(
    "Enter phone number with country code:",
    placeholder="+918888888888"
)

# Choose message method: SMS or WhatsApp
delivery_method = st.radio(
    "How do you want to send the reminder?",
    ["WhatsApp", "SMS"]
)

# The date when the reminder should be sent
date_sel = st.date_input("Select reminder date")

# The time when the reminder should be sent
time_str = st.text_input(
    "Enter time (24H, HH:MM):",
    value="09:00"
)

# -------------------------------------------------------------
# 💾 Save Reminder Button
# -------------------------------------------------------------
if st.button("Save Reminder"):
    try:
        user_time = datetime.strptime(time_str, "%H:%M").time()  # Convert text to time
        send_datetime = datetime.combine(date_sel, user_time)    # Combine with date

        # Add to stored reminders
        st.session_state["reminders"].append({
            "text": reminder_text,
            "phone": phone_number,
            "method": delivery_method,
            "datetime": send_datetime.strftime("%Y-%m-%d %H:%M")
        })

        save_reminders(st.session_state["reminders"])   # Save to file
        st.success("Reminder saved successfully!")

    except:
        st.error("Incorrect time format. Use HH:MM like 14:30.")

# -------------------------------------------------------------
# 📋 Show All Reminders
# -------------------------------------------------------------
st.subheader("📁 Saved Reminders")

# If no reminders, show message
if len(st.session_state["reminders"]) == 0:
    st.info("No reminders saved yet.")
else:
    # Show each saved reminder
    for i, r in enumerate(st.session_state["reminders"]):

        st.write(f"**Message:** {r['text']}")        # Show reminder message
        st.write(f"**To:** {r['phone']}")            # Where message will be sent
        st.write(f"**Method:** {r['method']}")       # SMS or WhatsApp
        st.write(f"**When:** {r['datetime']}")       # Date + time

        # Button to manually send the message now
        if st.button(f"Send Now #{i}"):

            # If WhatsApp selected, call WhatsApp function
            if r["method"] == "WhatsApp":
                ok, msg = send_whatsapp(r["phone"], r["text"])
            else:
                ok, msg = send_sms(r["phone"], r["text"])

            # Show success or error
            if ok:
                st.success(f"{r['method']} message sent!")
            else:
                st.error("Failed: " + str(msg))

        st.write("---")   # Line divider
