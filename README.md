# mailpeek

A lightweight Python library for reading unread emails via IMAP.

## Installation

```bash
poetry add mailpeek
```

## Basic Usage

```python
from mailpeek.reader import EmailReader

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
from mailpeek.imap_idle_listener import IMAPIdleListener

def on_new_mail(msg):
    print("\n📥 New email:", msg.get_subject())

def on_disconnect(error):
    print(f"🔌 Disconnected: {error}")

listener = IMAPIdleListener(
    host="imap.gmail.com",
    email="your-email@gmail.com",
    password="your-app-password",
    callback=on_new_mail,
    on_disconnect=on_disconnect,
)

listener.start()
```

To stop listening:

```python
listener.stop()
```

## Django Integration

* Create a `management/commands/read_emails.py` command that calls `fetch_unread()`
* Use `get_attachment_stream()` to save files into `FileField`
* Run via cron or Celery

## CLI Usage

Install with:

```bash
poetry add mailpeek
```

Run with:

```bash
poetry run mailpeek --email your-email@gmail.com --password your-app-password
```

Optional:

```bash
--all              # Fetch read + unread
--limit 20         # Only get 20 emails
--filename .pdf    # Only attachments with .pdf in name
--mime image/      # Only attachments starting with MIME image/
```

Or directly:

```bash
python src/mailpeek/cli.py --email your-email@gmail.com --password your-app-password
```

## PyPI Packaging

Make sure your `pyproject.toml` includes:

```toml
[project]
name = "mailpeek"
version = "0.1.0"
description = "A lightweight IMAP-based email reader for Python/Django"
readme = "README.md"
license = "MIT"
authors = ["Anand R Nair <anand547@outlook.com>"]
dependencies = ["imapclient >=3.0.1", "pyzmail36 >=1.0.5"]
requires-python = ">=3.9"

[project.scripts]
mailpeek = "mailpeek.cli:main"

[tool.poetry]
packages = [{ include = "mailpeek", from = "src" }]

[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"
```

Then:

```bash
poetry build
poetry publish --username __token__ --password <pypi-token>
```
