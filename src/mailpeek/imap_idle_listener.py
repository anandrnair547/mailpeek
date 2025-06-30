from imapclient import IMAPClient
import pyzmail
import time
import threading
import io


class IMAPIdleListener:
    def __init__(
        self,
        host,
        email,
        password,
        folder="INBOX",
        ssl=True,
        callback=None,
        on_disconnect=None,
    ):
        self.host = host
        self.email = email
        self.password = password
        self.folder = folder
        self.ssl = ssl
        self.callback = callback or self.default_callback
        self.on_disconnect = on_disconnect or self.default_disconnect_handler
        self._running = False
        self._thread = None

    def default_callback(self, message):
        subject = message.get_subject()
        sender = message.get_addresses("from")
        print(f"\n📧 New Email:\nFrom: {sender}\nSubject: {subject}")

        # Extract attachments
        attachments = []
        for part in message.mailparts:
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

    def default_disconnect_handler(self, error: Exception):
        print(f"❌ IMAP disconnected: {error.__class__.__name__} – {error}")

    def _idle_loop(self):
        print(f"📡 Connecting to {self.host}...")
        try:
            with IMAPClient(self.host, ssl=self.ssl) as client:
                client.login(self.email, self.password)
                client.select_folder(self.folder)
                print(f"✅ IDLE mode active for folder: {self.folder}")

                self._running = True
                while self._running:
                    try:
                        client.idle()
                        responses = client.idle_check(timeout=300)
                        if responses:
                            print("📨 New message received")
                            client.idle_done()
                            messages = client.search(["UNSEEN"])
                            for uid in messages:
                                raw = client.fetch([uid], ["BODY[]"])
                                msg = pyzmail.PyzMessage.factory(raw[uid][b"BODY[]"])
                                self.callback(msg)
                        else:
                            client.idle_done()
                    except Exception as e:
                        self.on_disconnect(e)
                        time.sleep(10)
        except Exception as conn_err:
            self.on_disconnect(conn_err)

    def start(self, use_thread=True):
        if use_thread:
            self._thread = threading.Thread(target=self._idle_loop, daemon=True)
            self._thread.start()
        else:
            self._idle_loop()

    def stop(self):
        self._running = False
        print("🛑 Stopping IMAP IDLE...")
