import imaplib
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def connect_to_imap_server(
    server: str,
    username: str,
    password: str
) -> Optional[imaplib.IMAP4_SSL]:
    """
    Establishes a secure IMAP connection to the specified server using the provided credentials.

    Parameters:
    - server (str): The address of the IMAP server to connect to.
    - username (str): The username for authentication.
    - password (str): The password for authentication.

    Returns:
    - imaplib.IMAP4_SSL object if connection and login are successful, None otherwise.
    """
    try:
        imap_session = imaplib.IMAP4_SSL(server)
        typ, account_details = imap_session.login(username, password)
        if typ != 'OK':
            logging.error('Not able to sign in!')
            return None
        logging.info("IMAP connection successful")
        return imap_session
    except imaplib.IMAP4.error as e:
        logging.error(f"IMAP login error: {e}")
        return None


def close_imap_session(
    imap_session: imaplib.IMAP4_SSL
) -> None:
    """
    Closes the IMAP session securely.

    Parameters:
    - imap_session (imaplib.IMAP4_SSL object): The IMAP session to close.
    """
    if imap_session:
        imap_session.logout()
