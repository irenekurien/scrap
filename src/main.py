from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


def scrape_and_notify():
    try:
        # Get today's date
        today = datetime.now().strftime("%b %d, %Y")

        # Make request
        url = os.getenv('URL')
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find today's updates
        rows = soup.find_all('tr', role="row")
        updates = []

        for row in rows:
            date_cell = row.find('td')
            if date_cell and date_cell.text.strip() == today:
                title_cell = date_cell.find_next_sibling('td')
                if title_cell and title_cell.find('a'):
                    link = title_cell.find('a')
                    updates.append({
                        'title': link.text.strip(),
                        'url': link.get('href')
                    })

        if updates:
            send_email(updates)

    except Exception as e:
        print(f"Error: {str(e)}")


def send_email(updates):
    sender_email = os.getenv('GMAIL_USER')
    app_password = os.getenv('GMAIL_APP_PASSWORD')
    receiver_email = os.getenv('RECEIVER_EMAIL')

    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"Updates - {
        datetime.datetime.now().strftime('%b %d, %Y')}"

    # Create email body
    body = "New updates found:\n\n"
    for update in updates:
        body += f"Title: {update['title']}\n"
        body += f"URL: {update['url']}\n\n"

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Create SMTP session
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, app_password)

        # Send email
        server.send_message(msg)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")


if __name__ == "__main__":
    scrape_and_notify()
