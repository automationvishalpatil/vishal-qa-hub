import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os



os.environ['SENDER_EMAIL'] = "Vishal.Patil8@cognizant.com"
os.environ['APP_PASSWORD'] = "asdadsasd"

sender_email = os.environ.get("SENDER_EMAIL")
app_password = os.environ.get("APP_PASSWORD")

if not sender_email or not app_password:
    print("Error: SENDER_EMAIL or APP_PASSWORD environment variables are not set.")
    exit()


csv_file = "C:\\Users\\433657\\pySelenium\\list.csv"

def send_emails_from_csv(csv_file, sender_email, app_password):
    try:
        server = smtplib.SMTP_SSL("smtp.office365.com", 587)
        server.login(sender_email, app_password)

        df = pd.read_csv(csv_file)

        for index, row in df.iterrows():
            name = row["name"]
            receiver_email = row["emailid"]
            body = row["message"]
            subject = f"Hello {name}, Timesheet reminder"

            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = receiver_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))
            
            try:
                text = msg.as_string()
                server.sendmail(sender_email, receiver_email, text)
                print(f"Email sent successfully to {name} at {receiver_email}!")
            except Exception as e:
                print(f"Failed to send email to {name} at {receiver_email}: {e}")

    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'server' in locals():
            server.quit()

send_emails_from_csv(csv_file, sender_email, app_password)