from email_reader.imap_idle_listener import IMAPIdleListener
import time
import threading

# --- Configuration ---
IMAP_HOST = "imap.gmail.com"
EMAIL = "dbg.qatesting2@gmail.com"
PASSWORD = "wfvmzrjfitevkktq"  # Use App Password or OAuth2 token if Gmail
FOLDER = "INBOX"

if __name__ == "__main__":
    import sys

    def on_new_mail(msg):
        subject = msg.get_subject()
        sender = msg.get_addresses("from")
        print("\n📥 New Email Received")
        print("From:", sender)
        print("Subject:", subject)

        attachments = []
        for part in msg.mailparts:
            if part.filename:
                attachments.append(
                    {
                        "filename": part.filename,
                        "content_type": part.type,
                        "size": len(part.get_payload()),
                        "stream": io.BytesIO(part.get_payload(decode=True)),
                    }
                )

        if attachments:
            print("📎 Attachments:")
            for att in attachments:
                print(
                    f" - {att['filename']} ({att['content_type']}, {att['size']} bytes)"
                )

    def on_disconnect(error):
        print(f"\n🔌 Disconnected due to: {error.__class__.__name__} – {error}")

    IMAP_HOST = "imap.gmail.com"
    EMAIL = "dbg.qatesting2@gmail.com"
    PASSWORD = "wfvmzrjfitevkktq"
    FOLDER = "INBOX"

    listener = IMAPIdleListener(
        host=IMAP_HOST,
        email=EMAIL,
        password=PASSWORD,
        folder=FOLDER,
        callback=on_new_mail,
        on_disconnect=on_disconnect,
    )

    listener.start()

    try:
        input("\n⏸ Press Enter to stop the listener...\n")
    except KeyboardInterrupt:
        print("🛑 Stopped via KeyboardInterrupt")
    finally:
        listener.stop()
        print("✅ Listener stopped cleanly.")
