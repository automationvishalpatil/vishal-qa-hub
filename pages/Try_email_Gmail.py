import streamlit as st
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from io import BytesIO

# --- 1. Utility for Sample CSV ---
#cqacqpclxcgebwki

def generate_sample_csv():
    """Creates a sample DataFrame and returns it as a CSV string."""
    data = {
        'name': ['John Doe', 'Jane Smith', 'Team Lead'],
        'emailid': ['john.doe@example.com', 'jane.smith@example.com', 'team.lead@example.com'],
        'message': [
            'Hi John, please submit your timesheet before EOD.',
            'Jane, friendly reminder about the timesheet deadline today.',
            'Please ensure all team members submit their timesheets promptly.'
        ]
    }
    df = pd.DataFrame(data)
    # Use to_csv to generate the CSV content in memory
    return df.to_csv(index=False).encode('utf-8')

# --- 2. Core Email Sending Logic ---

def send_emails_from_data(csv_data: BytesIO, sender_email: str, app_password: str, smtp_port: int):
    """
    Reads email data from a BytesIO object (uploaded CSV) and sends emails.
    Connects using the specified port (465 or 587).
    Returns a tuple (success_count, fail_messages).
    """
    
    # Read the CSV data from the uploaded file
    try:
        df = pd.read_csv(csv_data)
        required_cols = ["name", "emailid", "message"]
        if not all(col in df.columns for col in required_cols):
            return 0, [f"CSV is missing one or more mandatory columns: {', '.join(required_cols)}."]
    except Exception as e:
        return 0, [f"Error reading CSV file: {e}"]

    success_count = 0
    fail_messages = []
    server = None
    smtp_server = "smtp.gmail.com"
    
    try:
        # --- Connection Logic based on Port Selection ---
        if smtp_port == 465:
            # Use SMTP_SSL for Port 465
            server = smtplib.SMTP_SSL(smtp_server, 465)
        elif smtp_port == 587:
            # Use standard SMTP for Port 587 and then call starttls()
            server = smtplib.SMTP(smtp_server, 587)
            server.ehlo() # Extended Hello
            server.starttls() # Initiate TLS encryption
            server.ehlo()
        
        server.login(sender_email, app_password)

        for index, row in df.iterrows():
            name = row["name"]
            receiver_email = row["emailid"]
            body = row["message"]
            subject = f"Hello {name}, Timesheet reminder"
            
            if not receiver_email or not body:
                fail_messages.append(f"Skipped row {index + 2} (Name: {name}) due to missing email or message content.")
                continue

            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = receiver_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))
            
            try:
                text = msg.as_string()
                server.sendmail(sender_email, receiver_email, text)
                success_count += 1
            except Exception as e:
                fail_messages.append(f"Failed to send to {name} ({receiver_email}): {e}")

    # Catch Authentication Errors (SMTPAuthenticationError is the common one across versions)
    except (smtplib.SMTPAuthenticationError, getattr(smtplib, 'AuthenticationError', smtplib.SMTPAuthenticationError)) as e:
        fail_messages.append("Authentication Error: Failed to login. Check your Sender Email ID and App Password. Error: " + str(e))
    
    # Catch Connection Errors, including the WinError 10054
    except Exception as e:
        fail_messages.append(f"General connection error (Port {smtp_port}): {e}. Try the other port (465/587).")
    finally:
        if server:
            server.quit()

    return success_count, fail_messages

# --- 3. Streamlit UI ---

def main():
    st.set_page_config(page_title="Bulk Email Sender", layout="centered")

    st.title("📧 Automated Bulk Email Sender")
    st.markdown("Use this tool to send personalized emails from a CSV file.")
    st.warning("⚠️ **Crucial Step:** You must use a **Gmail App Password**, not your regular password, to prevent this error.")

    # --- Section 1: Credentials ---
    st.subheader("1. Sender Credentials & Connection")
    
    col_cred, col_port = st.columns([2, 1])
    
    with col_cred:
        sender_email = st.text_input("Sender Email ID (e.g., your_email@gmail.com)")
        app_password = st.text_input("App Password (REQUIRED)", type="password")

    with col_port:
        st.markdown("##### SMTP Port")
        smtp_port_str = st.radio(
            "Select Connection Type:",
            ('465 (SSL)', '587 (TLS)'),
            index=0,
            key='smtp_port_radio',
            help="If one port gives a connection error, try the other."
        )
        smtp_port = 465 if smtp_port_str == '465 (SSL)' else 587


    # --- Section 2: CSV File Management ---
    st.subheader("2. Prepare & Upload Email List")
    
    col_download, col_upload = st.columns([1, 2])
    
    # Download Sample CSV
    sample_csv_data = generate_sample_csv()
    with col_download:
        st.download_button(
            label="⬇️ Download Sample list.csv",
            data=sample_csv_data,
            file_name='sample_list.csv',
            mime='text/csv',
            type="secondary",
            help="Download to see the required columns: 'name', 'emailid', 'message'."
        )

    # Upload CSV File
    with col_upload:
        uploaded_file = st.file_uploader(
            "Upload your updated list.csv",
            type=["csv"],
            help="The CSV must contain 'name', 'emailid', and 'message' columns."
        )

    # --- Section 3: Action Button ---
    st.markdown("---")
    
    can_send = bool(sender_email and app_password and uploaded_file)
    
    if st.button("🚀 Send Emails Now", type="primary", disabled=not can_send):
        
        if not sender_email or not app_password or uploaded_file is None:
            st.error("Please fill in all required fields (Email, App Password, and Upload File).")
            st.stop()
        
        # Read the uploaded file into a BytesIO buffer
        csv_data = BytesIO(uploaded_file.getvalue())
        
        with st.spinner(f"Connecting to SMTP server on port {smtp_port} and sending emails..."):
            success_count, fail_messages = send_emails_from_data(csv_data, sender_email, app_password, smtp_port)
        
        # --- Results Display ---
        st.subheader("Sending Results")
        
        if success_count > 0:
            st.success(f"✅ Successfully sent **{success_count}** emails!")
        
        if fail_messages:
            st.error(f"❌ Failed to send **{len(fail_messages)}** emails. See details below:")
            for msg in fail_messages:
                st.code(msg, language=None)
        
        if success_count == 0 and not fail_messages and uploaded_file:
             st.warning("No emails were processed. Please check if your CSV file contains any rows or if columns are correctly named.")


if __name__ == "__main__":
    main()