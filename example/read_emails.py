from mailpeek.reader import EmailReader
import os

# --- Configuration ---
IMAP_HOST = "imap.your-provider.com"
EMAIL = "your-email@example.com"
PASSWORD = "your-app-password"  # Use an App Password or OAuth2 token
FOLDER = "INBOX"


def save_attachment_to_disk(stream, filename, download_dir="downloads"):
    os.makedirs(download_dir, exist_ok=True)
    filepath = os.path.join(download_dir, filename)
    with open(filepath, "wb") as f:
        f.write(stream.read())
    print(f"✅ Saved: {filepath}")


# --- Setup reader ---
reader = EmailReader(
    host=IMAP_HOST,
    email=EMAIL,
    password=PASSWORD,
    folder=FOLDER,
    ssl=True,
)

# --- Fetch unread emails with only PDF attachments ---
emails = reader.fetch_unread(attachment_filename_contains=".pdf")

for email in emails:
    print(f"\nFrom: {email['from']}")
    print(f"To: {email['to']}")
    print(f"Subject: {email['subject']}")
    print(f"Body: {email['body']}")
    print(f"Attachments: {len(email['attachments'])}")

    for att in email["attachments"]:
        stream = reader.get_attachment_stream(email["uid"], att["part_id"])
        save_attachment_to_disk(stream, att["filename"])
