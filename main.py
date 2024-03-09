from connect_to_imap_server import connect_to_imap_server, close_imap_session
from search_emails import search_emails, get_attachments_info, list_mailboxes
import logging
import os
from dotenv import load_dotenv
import imaplib

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
USERNAME = os.environ['EMAIL_USERNAME']
PASSWORD = os.environ['EMAIL_PASSWORD']
IMAP_SERVER = os.environ['IMAP_SERVER']
MAILBOX = "INBOX"  # Specify the mailbox to search in
START_DATE = "01-Mar-2024"  # Define the start date of the email search range
END_DATE = "04-Mar-2024"  # Define the end date of the email search range
FILE_EXTENSION = ".pdf"  # Specify the file extension of attachments to search for


def main():
    """
    Connects to the IMAP server, lists all available mailboxes,
    searches for emails within a specified date range in a specified mailbox,
    retrieves information about attachments with a specified file extension,
    and logs details of found attachments.
    """
    imap_session = None
    try:
        imap_session = connect_to_imap_server(IMAP_SERVER, USERNAME, PASSWORD)
        if not imap_session:
            logging.error("Failed to connect to IMAP server.")
            return

        # Call the list_mailboxes function to list all available mailboxes
        logging.info("Listing all available mailboxes:")
        list_mailboxes(imap_session)

        email_ids = search_emails(imap_session, MAILBOX, START_DATE, END_DATE)
        if not email_ids:
            logging.info("No emails found in the specified date range.")
            return

        attachments_info = get_attachments_info(
            imap_session, email_ids, FILE_EXTENSION)
        if not attachments_info:
            logging.info(
                "No attachments found matching the specified file extension.")
            return

        for subject, from_, file_name in attachments_info:
            logging.info(
                f"Found attachment: {file_name}, From: {from_}, Subject: \"{subject}\"")

    except imaplib.IMAP4.error as imap_error:
        logging.error(f"IMAP error occurred: {imap_error}")
    except Exception as general_error:
        logging.error(f"An unexpected error occurred: {general_error}")
    finally:
        if imap_session:
            close_imap_session(imap_session)


if __name__ == "__main__":
    main()
