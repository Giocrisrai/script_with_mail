from typing import List, Tuple, Optional
from email.header import decode_header, make_header
import email
from datetime import datetime, timedelta
import logging
import imaplib

# Logging configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

DATE_FORMAT = "%d-%b-%Y"


def validate_date_range(
    start_date: str,
    end_date: str,
    date_format: str
) -> None:
    """
    Validates that the start_date is before the end_date according to the given date format.
    """
    start = datetime.strptime(start_date, date_format)
    end = datetime.strptime(end_date, date_format)
    if start >= end:
        raise ValueError("start_date must be before end_date")


def search_emails(
    imap_session: imaplib.IMAP4_SSL,
    mailbox: str,
    start_date: str,
    end_date: str
) -> List[str]:
    """
    Searches for emails within a given date range in the specified mailbox.
    """
    validate_date_range(start_date, end_date, DATE_FORMAT)
    imap_session.select(mailbox)

    since_date = datetime.strptime(
        start_date, DATE_FORMAT).strftime(DATE_FORMAT)
    before_date = (datetime.strptime(end_date, DATE_FORMAT) +
                   timedelta(days=1)).strftime(DATE_FORMAT)
    typ, data = imap_session.search(
        None, f'(SINCE "{since_date}" BEFORE "{before_date}")')
    if typ != 'OK':
        logging.error(
            'Error searching Inbox. IMAP search did not return "OK".')
        return []

    # Decoding bytes to str
    email_ids_str = [email_id.decode('utf-8') for email_id in data[0].split()]
    return email_ids_str


def list_mailboxes(
    imap_session: imaplib.IMAP4_SSL
) -> None:
    """
    Lists all mailboxes (folders) available in the email account.
    """
    typ, mailboxes = imap_session.list()
    if typ == 'OK':
        logging.info("Mailboxes available:")
        for mailbox in mailboxes:
            mailbox_name = str(make_header(decode_header(
                mailbox.decode().split(' \"/\" ')[1])))
            logging.info(f"- {mailbox_name}")
    else:
        logging.error("Failed to list mailboxes.")


def decode_text(
    text: Optional[bytes],
    default_charset='utf-8'
) -> str:
    """
    Decodes a text or email header value safely, handling unknown or problematic encodings.

    Parameters:
    - text: The text to decode, possibly in bytes. If None, returns an empty string.
    - default_charset (str): The default charset to use if the text's encoding is unknown or fails.

    Returns:
    - The decoded text as a string.
    """
    if text is None:
        logging.warning("decode_text received None instead of string/bytes.")
        return ""

    decoded_string = ""
    try:
        if isinstance(text, bytes):
            decoded_header = decode_header(text)
            decoded_string = str(make_header(decoded_header))
        else:
            decoded_string = text
    except Exception as e:
        logging.error(
            f"Error decoding text: {e}, using default charset {default_charset}.")
        decoded_string = text.decode(
            default_charset, errors='replace') if isinstance(text, bytes) else text

    return decoded_string


def get_attachments_info(
    imap_session: imaplib.IMAP4_SSL,
    email_ids: List[str],
    file_extension: str
) -> List[Tuple[str, str, str]]:
    """
    Fetches emails by IDs and scans each for attachments of a specific type.
    """
    attachments_info = []
    for email_id in email_ids:
        logging.info(f"Processing email ID: {email_id}")
        typ, data = imap_session.fetch(email_id, '(RFC822)')
        if typ != 'OK':
            logging.error(f"Failed to fetch email ID {email_id}.")
            continue

        email_message = email.message_from_bytes(data[0][1])
        subject = decode_text(email_message["subject"])
        from_ = decode_text(email_message["from"])

        for part in email_message.walk():
            if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
                continue
            file_name = decode_text(part.get_filename())
            if file_name and file_name.endswith(file_extension):
                attachments_info.append((subject, from_, file_name))
                logging.info(f"Found attachment: {file_name}")

    logging.info(
        f"Completed processing emails. Found {len(attachments_info)} attachments.")
    return attachments_info
