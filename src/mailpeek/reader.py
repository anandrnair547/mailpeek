from imapclient import IMAPClient
import pyzmail
import io


class EmailReader:
    def __init__(self, host, email, password, folder="INBOX", ssl=True):
        self.host = host
        self.email = email
        self.password = password
        self.folder = folder
        self.ssl = ssl

    def fetch_emails(
        self,
        unread_only=True,
        limit=None,
        attachment_filename_contains: str | None = None,
        attachment_mime_startswith: str | None = None,
    ):
        with IMAPClient(self.host, ssl=self.ssl) as client:
            client.login(self.email, self.password)
            client.select_folder(self.folder, readonly=True)

            search_criteria = ["UNSEEN"] if unread_only else ["ALL"]
            messages = client.search(search_criteria)

            if limit:
                messages = messages[:limit]

            emails = []

            for uid in messages:
                raw_message = client.fetch([uid], ["BODY[]", "FLAGS"])
                message = pyzmail.PyzMessage.factory(raw_message[uid][b"BODY[]"])

                subject = message.get_subject()
                from_email = message.get_addresses("from")
                to_emails = message.get_addresses("to")
                body = ""

                if message.text_part:
                    body = message.text_part.get_payload().decode(
                        message.text_part.charset
                    )
                elif message.html_part:
                    body = message.html_part.get_payload().decode(
                        message.html_part.charset
                    )

                attachments = []
                for part in message.mailparts:
                    if part.filename:
                        if (
                            attachment_filename_contains
                            and attachment_filename_contains not in part.filename
                        ):
                            continue
                        if attachment_mime_startswith and not part.type.startswith(
                            attachment_mime_startswith
                        ):
                            continue

                        attachments.append(
                            {
                                "filename": part.filename,
                                "content_type": part.type,
                                "size": len(part.get_payload()),
                                "part_id": part.part,
                            }
                        )

                emails.append(
                    {
                        "uid": uid,
                        "from": from_email,
                        "to": to_emails,
                        "subject": subject,
                        "body": body,
                        "attachments": attachments,
                    }
                )

            return emails

    def fetch_unread(self, **kwargs):
        return self.fetch_emails(unread_only=True, **kwargs)

    def get_attachment_stream(self, uid: int, part_id: int) -> io.BytesIO:
        with IMAPClient(self.host, ssl=self.ssl) as client:
            client.login(self.email, self.password)
            client.select_folder(self.folder, readonly=True)

            raw_message = client.fetch([uid], ["BODY[]"])
            message = pyzmail.PyzMessage.factory(raw_message[uid][b"BODY[]"])

            for part in message.mailparts:
                if part.part == part_id:
                    return io.BytesIO(part.get_payload(decode=True))

            raise ValueError(f"No attachment found for UID={uid}, part_id={part_id}")
