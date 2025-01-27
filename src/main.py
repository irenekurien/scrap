import os
import json
import smtplib
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


load_dotenv()


def track_sent_updates():
    sent_file = "sent_updates.json"

    try:
        if os.path.exists(sent_file):
            with open(sent_file, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error reading sent updates: {e}")
        return {}


def update_sent_tracking(updates):
    sent_file = "sent_updates.json"
    today = datetime.now().strftime("%Y-%m-%d")

    sent_updates = track_sent_updates()

    # Initialize today's entries if not exists
    if today not in sent_updates:
        sent_updates[today] = []

    # Add new updates to tracking
    for update in updates:
        update_id = update['title']
        if update_id not in sent_updates[today]:
            sent_updates[today].append(update_id)

    # Save updated tracking
    with open(sent_file, 'w') as f:
        json.dump(sent_updates, f, indent=2)


def scrape_and_notify():
    try:
        today = datetime.now().strftime("%b %d, %Y")

        url = os.getenv('URL')
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        today = datetime.now().strftime("%b %d, %Y")
        sent_updates = track_sent_updates()
        today_date = datetime.now().strftime("%Y-%m-%d")

        updates = []
        rows = soup.find_all('tr', role="row")

        for row in rows:
            date_cell = row.find('td')
            if date_cell and date_cell.text.strip() == today:
                title_cell = date_cell.find_next_sibling('td')
                if title_cell and title_cell.find('a'):
                    link = title_cell.find('a')
                    update = {
                        'title': link.text.strip(),
                        'url': link.get('href')
                    }

                    # Check if already sent
                    update_id = update['title']
                    if today_date not in sent_updates or update_id not in sent_updates[today_date]:
                        updates.append(update)

        if updates:
            send_email(updates)
            update_sent_tracking(updates)
            print(f"Sent {len(updates)} new updates")
        else:
            print("No new updates to send")

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
    msg['Subject'] = f"Updates - {datetime.now().strftime('%b %d, %Y')}"

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
