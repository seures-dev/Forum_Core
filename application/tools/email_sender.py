import smtplib
import threading

from config import Config
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(recipient_email, subject, message):
	gmail_user = Config.get_mail()
	gmail_password = Config.get_mail_password()
	msg = MIMEMultipart()
	msg['From'] = gmail_user
	msg['To'] = recipient_email
	msg['Subject'] = subject
	msg.attach(MIMEText(message, 'html'))
	thread = threading.Thread(target=thread_send, args=[gmail_user, gmail_password, recipient_email, msg])
	thread.start()


def thread_send(gmail_user,gmail_password, recipient_email, msg: MIMEMultipart):
	try:
		with smtplib.SMTP('smtp.gmail.com', 587) as server:
			server.starttls()
			server.login(gmail_user, gmail_password)
			server.sendmail(
				from_addr=gmail_user,
				to_addrs=recipient_email,
				msg=msg.as_string()
			)
		print("Message sent successfully")
	except Exception as e:
		print(str(e))


if __name__ == '__main__':
	gmail_user = ""
	send_email(gmail_user, "test", "hello it's test)")