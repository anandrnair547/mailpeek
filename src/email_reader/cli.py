import argparse
from email_reader.reader import EmailReader


def main():
    parser = argparse.ArgumentParser(description="Read emails via IMAP")
    parser.add_argument("--host", default="imap.gmail.com", help="IMAP server host")
    parser.add_argument("--email", required=True, help="Email address")
    parser.add_argument(
        "--password", required=True, help="Email password or app password"
    )
    parser.add_argument("--folder", default="INBOX", help="Folder to read from")
    parser.add_argument(
        "--all", action="store_true", help="Fetch all emails (read + unread)"
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="Limit number of emails fetched"
    )
    parser.add_argument(
        "--filename", type=str, default=None, help="Filter attachments by filename"
    )
    parser.add_argument(
        "--mime", type=str, default=None, help="Filter attachments by MIME type prefix"
    )
    args = parser.parse_args()

    reader = EmailReader(
        host=args.host, email=args.email, password=args.password, folder=args.folder
    )

    emails = reader.fetch_emails(
        unread_only=not args.all,
        limit=args.limit,
        attachment_filename_contains=args.filename,
        attachment_mime_startswith=args.mime,
    )

    for mail in emails:
        print(f"From: {mail['from']} | Subject: {mail['subject']}")


if __name__ == "__main__":
    main()
