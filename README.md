# email-reader

A lightweight Python library for reading unread emails via IMAP, with support for on-demand attachment streaming and real-time inbox monitoring using IMAP IDLE.

## Installation

```bash
poetry add email-reader
```

## Basic Usage

```python
from email_reader.reader import EmailReader

reader = EmailReader(
    host="imap.gmail.com",
    email="your-email@gmail.com",
    password="your-app-password"
)

emails = reader.fetch_unread()
for mail in emails:
    print(mail["subject"], mail["from"])
```

## Fetch All Emails with Limit

```python
emails = reader.fetch_emails(unread_only=False, limit=10)
```

## Filter Attachments

### Only PDFs:

```python
emails = reader.fetch_unread(attachment_filename_contains=".pdf")
```

### Only images:

```python
emails = reader.fetch_unread(attachment_mime_startswith="image/")
```

## Fetch Attachments On-Demand

```python
for mail in emails:
    for att in mail["attachments"]:
        stream = reader.get_attachment_stream(mail["uid"], att["part_id"])
        with open(att["filename"], "wb") as f:
            f.write(stream.read())
```

## Use with IMAP IDLE (Real-Time Mail Listener)

```python
from email_reader.imap_idle_listener import IMAPIdleListener

# Callback on new mail
def on_new_mail(msg):
    subject = msg.get_subject()
    sender = msg.get_addresses("from")
    print("\n📥 New Email Received")
    print("From:", sender)
    print("Subject:", subject)

    attachments = []
    for part in msg.mailparts:
        if part.filename:
            attachments.append({
                "filename": part.filename,
                "content_type": part.type,
                "size": len(part.get_payload()),
                "stream": io.BytesIO(part.get_payload(decode=True)),
            })

    if attachments:
        print("📎 Attachments:")
        for att in attachments:
            print(f" - {att['filename']} ({att['content_type']}, {att['size']} bytes)")

# Callback on disconnect
def on_disconnect(error):
    print(f"\n🔌 Disconnected due to: {error.__class__.__name__} – {error}")

listener = IMAPIdleListener(
    host="imap.gmail.com",
    email="your-email@gmail.com",
    password="your-app-password",
    folder="INBOX",
    callback=on_new_mail,
    on_disconnect=on_disconnect,
)

print("▶️ Starting IMAP IDLE listener. Press Enter to stop...")
listener.start()

try:
    input("\n⏸ Press Enter to stop the listener...\n")
except KeyboardInterrupt:
    print("🛑 Stopped via KeyboardInterrupt")
finally:
    listener.stop()
    print("✅ Listener stopped cleanly.")
```

## Django Integration

* Create a `management/commands/read_emails.py` command that calls `fetch_unread()`
* Use `get_attachment_stream()` to save files into `FileField`
* Run via cron or Celery for periodic polling

## CLI Usage

Add this to `pyproject.toml`:

```toml
[tool.poetry.scripts]
email-reader = "email_reader.cli:main"
```

### CLI File: `src/email_reader/cli.py`

```python
import argparse
from email_reader.reader import EmailReader

def main():
    parser = argparse.ArgumentParser(description="Read emails via IMAP")
    parser.add_argument("--host", default="imap.gmail.com", help="IMAP server host")
    parser.add_argument("--email", required=True, help="Email address")
    parser.add_argument("--password", required=True, help="Email password or app password")
    parser.add_argument("--folder", default="INBOX", help="Folder to read from")
    parser.add_argument("--all", action="store_true", help="Fetch all emails (read + unread)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of emails fetched")
    args = parser.parse_args()

    reader = EmailReader(
        host=args.host,
        email=args.email,
        password=args.password,
        folder=args.folder
    )

    emails = reader.fetch_emails(unread_only=not args.all, limit=args.limit)
    for mail in emails:
        print(f"From: {mail['from']}, Subject: {mail['subject']}")

if __name__ == "__main__":
    main()
```

Run with:

```bash
poetry run email-reader --email your-email@gmail.com --password your-app-password
```

Optional:

```bash
--all        # Fetch read + unread
--limit 20   # Only get 20 emails
```

Or directly:

```bash
python src/email_reader/cli.py --email your-email@gmail.com --password your-app-password
```

## PyPI Packaging

Make sure your `pyproject.toml` includes:

```toml
[tool.poetry]
name = "email-reader"
version = "0.1.0"
description = "A Python IMAP email reader"
authors = ["Your Name <you@example.com>"]
license = "MIT"
packages = [{ include = "email_reader" }]

[tool.poetry.dependencies]
python = ">=3.8"
imapclient = "^3.0.1"
pyzmail36 = "^1.0.5"
```

Then:

```bash
poetry build
poetry publish --username __token__ --password <pypi-token>
```

Let us know if you'd like a Django, CLI, or Celery integration example in more detail.
