# -------------------------------------------------------------
# 📱 Streamlit SMS + WhatsApp Reminder App (Auto Scheduler, IST Time)
# -------------------------------------------------------------

# These lines bring in ready-made tools so our program can work
import streamlit as st          # Helps us create the webpage/app
import json                     # Helps us save and load data
from datetime import datetime, timedelta   # Helps us work with dates & time
from twilio.rest import Client  # Helps us send WhatsApp/SMS messages

# --------------------------
# TWILIO - replace with yours
# --------------------------

# These are secret keys given by Twilio so the app can send messages
TWILIO_ACCOUNT_SID = "ACe855d3519d798fdb8d4017b8692f0860"
TWILIO_AUTH_TOKEN = "b28ef14855ce695a499ce9e669578180"

# Twilio numbers used to send WhatsApp and SMS
TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"
TWILIO_SMS_FROM = "+18542013278"

# This makes a Twilio helper object that can send messages
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# This is the name of the file where we save all reminders
FILE_NAME = "all_reminders.json"

# -----------------------------------------------------
# IST TIME FUNCTION  (MAIN FIX YOU ASKED FOR)
# -----------------------------------------------------
def get_ist_now():
    utc_now = datetime.utcnow()                    # Gets current time in UTC (global time)
    ist_now = utc_now + timedelta(hours=5, minutes=30)  # Adds 5:30 to make it IST
    return ist_now                                 # Gives back the IST time

# --------------------------
# Helpers: load / save
# --------------------------

# This function reads reminders from the file
def load_reminders():
    try:
        with open(FILE_NAME, "r") as f:   # Open file to read
            return json.load(f)           # Return list of saved reminders
    except Exception:
        return []                         # If file not found, start with empty list

# This function saves reminders to the file
def save_reminders(reminders):
    with open(FILE_NAME, "w") as f:         # Open file to write
        json.dump(reminders, f, indent=2)   # Save reminders nicely in the file

# --------------------------
# Helpers: send messages
# --------------------------

# Sends WhatsApp message using Twilio
def send_whatsapp(to_phone, message):
    try:
        msg = client.messages.create(   # Create and send WhatsApp message
            body=message,               # Message text
            from_=TWILIO_WHATSAPP_FROM,
            to=f"whatsapp:{to_phone}"
        )
        return True, msg.sid            # Return "sent" status and message ID
    except Exception as e:
        return False, str(e)            # If error, tell what went wrong

# Sends SMS message using Twilio
def send_sms(to_phone, message):
    try:
        msg = client.messages.create(   # Send SMS message
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

# If reminders are not already loaded, load them now
if "reminders" not in st.session_state:
    st.session_state["reminders"] = load_reminders()

# --------------------------
# Auto-refresh: reload page every 60 seconds
# --------------------------

# This refreshes the page every 60 seconds so the scheduler can run
st.markdown('<meta http-equiv="refresh" content="60">', unsafe_allow_html=True)

# --------------------------
# UI
# --------------------------

st.title("📩 SMS + WhatsApp Reminder App (IST Auto Scheduler)")  # Title on top of the app

# A form where users can add a new reminder
with st.form("add_reminder_form", clear_on_submit=True):
    reminder_text = st.text_input("Enter reminder message:", placeholder="Drink water")  # Message text
    phone_number = st.text_input("Enter phone number with country code:", placeholder="+918888888888")  # Phone number
    delivery_method = st.radio("Send using:", ["WhatsApp", "SMS"])  # Choose WhatsApp or SMS
    date_sel = st.date_input("Select reminder date (IST):")          # Date pick
    time_str = st.text_input("Enter time (24H format HH:MM IST):", value="09:00")  # Time pick
    submitted = st.form_submit_button("Save Reminder")               # Button to save reminder

# When user submits the form
if submitted:
    try:
        user_time = datetime.strptime(time_str, "%H:%M").time()  # Convert time text into time object

        # COMBINE WITH IST DATE
        send_datetime = datetime.combine(date_sel, user_time)  # Combine date + time

        # Save the new reminder
        new = {
            "text": reminder_text,
            "phone": phone_number,
            "method": delivery_method,
            "datetime": send_datetime.strftime("%Y-%m-%d %H:%M"),  # Save date/time as text
            "sent": False                                          # Not sent yet
        }
        st.session_state["reminders"].append(new)   # Add to list
        save_reminders(st.session_state["reminders"])  # Save to file
        st.success("Reminder saved using IST!")     # Show success message
    except Exception:
        st.error("Invalid time format — use HH:MM (24-hour).")

# --------------------------
# Display saved reminders
# --------------------------

st.subheader("📁 Saved Reminders (IST)")  # Heading for saved reminders

if len(st.session_state["reminders"]) == 0:
    st.info("No reminders saved yet.")    # Show if empty
else:
    # Show each reminder one by one
    for i, r in enumerate(st.session_state["reminders"]):
        st.write(f"**Message:** {r['text']}")       # Show text
        st.write(f"**To:** {r['phone']}")           # Show phone
        st.write(f"**Method:** {r['method']}")      # WhatsApp / SMS
        st.write(f"**When (IST):** {r['datetime']}")# When to send
        st.write(f"**Sent:** {'Yes' if r.get('sent', False) else 'No'}")  # Sent or not

        # Button to send the message immediately
        if st.button(f"Send Now #{i}"):
            if r["method"] == "WhatsApp":
                ok, msg = send_whatsapp(r["phone"], r["text"])  # Send WhatsApp
            else:
                ok, msg = send_sms(r["phone"], r["text"])        # Send SMS

            if ok:
                r["sent"] = True                                  # Mark as sent
                save_reminders(st.session_state["reminders"])     # Save update
                st.success("Message sent manually!")              # Success message
            else:
                st.error(f"Failed to send: {msg}")                # Error message

        st.write("---")  # Just a line for separation

# --------------------------
# Auto Scheduler (IST)
# --------------------------

st.subheader("⏱ Auto Scheduler (IST)")  # Heading for scheduler

current_ist = get_ist_now().strftime("%Y-%m-%d %H:%M")  # Get current IST time
st.write(f"Current IST Time: **{current_ist}**")        # Show it on screen

sent_any = False  # To check if anything was sent this minute

# Go through each reminder
for r in st.session_state["reminders"]:
    # If time matches AND reminder not already sent
    if r["datetime"] == current_ist and not r.get("sent", False):

        st.info(f"Sending scheduled message to {r['phone']}: {r['text']}")  # Show info

        if r["method"] == "WhatsApp":
            ok, msg = send_whatsapp(r["phone"], r["text"])  # Auto-send WhatsApp
        else:
            ok, msg = send_sms(r["phone"], r["text"])        # Auto-send SMS

        if ok:
            r["sent"] = True                                     # Mark sent
            save_reminders(st.session_state["reminders"])        # Save file
            sent_any = True
            st.success(f"{r['method']} message sent automatically (IST)!")  # Show success
        else:
            st.error(f"Failed to send scheduled message: {msg}")            # Show error

# If nothing was scheduled at this minute
if not sent_any:
    st.write("No scheduled messages at this IST minute.")

# --------------------------
# Helpful note
# --------------------------

st.caption(
    "This app runs entirely in IST (Indian Standard Time). "
    "Keep the tab open; the scheduler checks every 60 seconds automatically."
)
