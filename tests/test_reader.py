import pytest
from unittest.mock import patch, MagicMock
from src.mailpeek.reader import EmailReader


@pytest.fixture
def mock_imap_client():
    # ✅ Correct patch path based on your structure
    with patch("src.email_reader.reader.IMAPClient") as MockIMAP:
        instance = MagicMock()
        MockIMAP.return_value.__enter__.return_value = instance
        yield instance


@pytest.fixture
def fake_email_bytes():
    from email.message import EmailMessage

    msg = EmailMessage()
    msg["Subject"] = "Test Subject"
    msg["From"] = "test@example.com"
    msg["To"] = "receiver@example.com"
    msg.set_content("Test Body")

    # ✅ Return raw bytes — exactly what IMAPClient would return
    return msg.as_bytes()


def test_fetch_unread_emails(mock_imap_client, fake_email_bytes):
    uid = 123
    mock_imap_client.search.return_value = [uid]
    mock_imap_client.fetch.return_value = {
        uid: {b"BODY[]": fake_email_bytes, b"FLAGS": []}
    }

    reader = EmailReader(
        host="imap.example.com", email="you@example.com", password="secret"
    )

    emails = reader.fetch_unread()

    assert isinstance(emails, list)
    assert len(emails) == 1
    assert emails[0]["uid"] == uid
    assert "subject" in emails[0]
    assert "from" in emails[0]
    assert "body" in emails[0]
