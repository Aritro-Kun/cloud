import tkinter as tk
import os
from dotenv import load_dotenv
import mysql.connector as sqlcon
import hashlib
from tkinter import messagebox
import uuid
from datetime import datetime, timedelta
from email_validator import validate_email, EmailNotValidError
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv(dotenv_path="D:/chatspace/resources.env") #future part of work will be to make this path, dynamically added and not hardcoded.

db_user = os.getenv("DB_user")
db_pass = os.getenv("DB_pass")
db_host = os.getenv("DB_host")
db_name = os.getenv("DB_name")
sending_mail = os.getenv("SENDING_mail")
sending_pass = os.getenv("SENDING_pass")

connection = sqlcon.connect(
        host = db_host,
        user = db_user,
        password = db_pass,
        database = db_name,
)

cursor = connection.cursor()

root=tk.Tk()
root.title("Sign-In")
root.geometry("800x600")

def verify_email(mailid):
    try:
        verify_mail = validate_email(mailid)
        mailid = verify_mail.email
        return True
    except EmailNotValidError as e:
        return False

def clear_expired_entries():
    if not connection.is_connected():
        connection.reconnect()
    clear_query="""
    DELETE FROM test_tempo_signin
    WHERE token_expiry < %s
    """
    current_time = datetime.now()
    cursor.execute(clear_query, (current_time,))
    connection.commit()

def clear_verified_entries():
    if not connection.is_connected():
        connection.reconnect()
    clear_query = """
    DELETE FROM test_tempo_signin
    WHERE status = %s
    """
    cursor.execute(clear_query, ('otp_verified',))
    connection.commit()

def limit_entry(*args):
    current_text = name_entry_var.get()
    if not current_text.isalpha():
        current_text = ''.join(filter(str.isalpha, current_text))
    if (len(current_text)>20):
        current_text=current_text[:20]
    name_entry_var.set(current_text)

def send_verification_mail(mail, username, token):
    print("We will work on the mail sending proccess.")
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Sign-In Email Verificitaion for Chatspace!"
    msg['From'] = sending_mail
    msg['To'] = mail
    verification_link = f"http://127.0.0.1:5000/verify_and_register?token={token}&email={mail}&username={username}"
    text = f"""
    Hi, Mr. {username}!

    We are here from Chatspace! We have noticed that you have been trying to sign-in using this email id. To complete the sign-in process, please click the verification link below:
    {verification_link}

    For your concerns, we assure you that your email is stored in hashed form in our database, to secure your protection in case of a database breach. Also, the attached link contains a generated token, that ensures that the sign-in is being done by a geniune user. It is not a phishing attack. Your safety is our concern.

    Happy, Chatspacing! :)
    """
    html = f"""
    <html>
      <head>
        <style>
          .button {{
            display: inline-block;
            padding: 12px 24px;
            font-size: 16px;
            color: #fff;
            background-color: #5ce1e6; /* Default button color */
            text-decoration: none;
            border-radius: 6px;
            transition: all 0.3s ease; /* Smooth transition */
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1); /* Add subtle shadow */
          }}
          .button:hover {{
            background-color: #2fc1c8; /* Lighter, vibrant shade on hover */
            transform: scale(1.05); /* Slight zoom effect */
            box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.2); /* Stronger shadow on hover */
          }}
        </style>
      </head>
      <body>
        <p>Hi, Mr. {username}!</p>
        <p>We are here from Chatspace! We have noticed that you have been trying to sign-in using this email ID. To complete the sign-in process, please click the verification button below:</p>
        <a href="{verification_link}" class="button">Verify Email</a>
        <br><br>
        <p>For your concerns, we assure you that your email is stored in hashed form in our database, ensuring your protection in case of a database breach. Also, the attached link contains a generated token that ensures the sign-in is being done by a genuine user. It is not a phishing attack. Your safety is our concern.</p>
        <br>
        <p>Happy, Chatspacing! :)</p>
      </body>
    </html>
    """

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)

    try:
        server =smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sending_mail, sending_pass)
        server.sendmail(sending_mail, mail, msg.as_string())
        print(f"Verification mail sent to {mail}!")
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()


def validate_mail():
    print("Verify the mail")
    clear_expired_entries()
    clear_verified_entries()
    entered_mail = mail_entry.get()
    entered_username = name_entry.get()
    hashed_mail = hashlib.sha256(entered_mail.encode()).hexdigest()
    entered_name = name_entry.get()
    if(verify_email(entered_mail)):
        if not connection.is_connected():
            connection.reconnect()
        try:
            validating_registered_query = "SELECT COUNT(*) FROM test_registered_users WHERE hashed_mail = %s"
            cursor=connection.cursor()
            cursor.execute(validating_registered_query, (hashed_mail,))
            validating_registered_result=cursor.fetchone()
            validating_temporary_query = "SELECT COUNT(*) FROM test_tempo_signin WHERE hashed_user_mail = %s"
            cursor.execute(validating_temporary_query, (hashed_mail,))
            validating_temporary_result = cursor.fetchone()
            if (validating_registered_result[0]!=0):
                print("The email already exists")
                messagebox.showerror("Validation Error", "The entered email already exists.")
                return
            elif (validating_temporary_result[0]!=0):
                print("This email is being used elsewhere to signin.")
                messagebox.showerror("Validation Error", "There is already an open attempt to login using this mail.")
            else:
                generated_token = str(uuid.uuid4())
                hashed_token = hashlib.sha256(generated_token.encode()).hexdigest()
                expiry_time = datetime.now() + timedelta(hours=1)
                pushing_to_temp_query = "INSERT INTO test_tempo_signin (hashed_user_mail, username, token, token_expiry) VALUES (%s, %s, %s, %s)"
                cursor.execute(pushing_to_temp_query, (hashed_mail, entered_name, hashed_token, expiry_time))
                connection.commit()
                send_verification_mail(entered_mail, entered_username, generated_token)
                messagebox.showinfo("Success", "Check your mail-box, to complete the Registration.")
            print(hashed_mail)
            root.destroy()
        except sqlcon.Error as err:
            print(f"Error during Validation as: {err}")
            messagebox.showerror("Database Error", f"An error occurred.: {err}")
        finally:
            cursor.close()
    else:
        messagebox.showerror("Improper Mail Id", "Please give a proper Mail-Id to proceed!")
#in future, please try to integrate the token into the user's local system in some sort of file, so that breaching is difficult.

label_signin = tk.Label(root, text="Sign In", font=("Arial", 20))
label_signin.pack(pady=30)

initial_space = tk.Frame(root)
initial_space.pack(pady=20)

name_entry_label = tk.Label(initial_space, text="Enter your Username: ", font=("Arial", 10))
name_entry_label.grid(row=0, column=0, pady=5)

name_entry_var = tk.StringVar()
name_entry_var.trace_add("write", limit_entry)

name_entry = tk.Entry(initial_space, width=30, font=("Arial", 10), textvariable=name_entry_var)
name_entry.grid(row=0, column=1, pady=5)

mail_entry_label = tk.Label(initial_space, text="Enter your Mail Id: ", font=("Arial", 10))
mail_entry_label.grid(row=1, column=0, pady=5)

mail_entry = tk.Entry(initial_space, width=45, font=("Arial", 10))
mail_entry.grid(row=1, column=1, pady=5)

validate_frame = tk.Frame(root)
validate_frame.pack(pady=20)

verify_label = tk.Label(validate_frame, text="Click Validate to validate your mail: ", font=("Arial", 10))
verify_label.grid(row=0, column=0, pady=5)

verify_button = tk.Button(validate_frame, width=20, text="Validate Mail", command=validate_mail)
verify_button.grid(row=1, column=0, pady=10)

def on_closing():
    if messagebox.askokcancel("Quit", "Do you really want to quit signing up?"):
        if connection.is_connected():
            connection.close()
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
