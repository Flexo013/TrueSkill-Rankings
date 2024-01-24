import os.path
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import google_auth

# Path to the file where the OAuth2 token will be stored
TOKEN_PATH = "token.json"

# Label to filter emails
TARGET_LABEL = 'Foosball'


def get_gmail_credentials():
    # Load or create OAuth2 token
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",  # Path to the file containing your client secrets
                scopes=['https://www.googleapis.com/auth/gmail.readonly']
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    return creds


def check_email(credentials):
    # Connect to Gmail server using OAuth2 credentials
    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=credentials)
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])

        if not labels:
            print("No labels found.")
            return
        print("Labels:")
        for i, label in enumerate(labels):
            print("{0}, {1}".format(label["name"], label["id"]))

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")

    exit()
    # Select the 'Foosball' label
    status, messages = mail.select(TARGET_LABEL)
    if status == 'OK':
        # Search for all emails in the selected label
        status, messages = mail.search(None, 'ALL')
        if status == 'OK':
            # Get the list of email IDs
            email_ids = messages[0].split()

            for email_id in email_ids:
                # Fetch the email by ID
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                if status == 'OK':
                    # Parse the email
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)

                    # Check if the 'Foosball' label is present
                    labels = msg.get('X-Gmail-Labels', '').split(',')
                    if TARGET_LABEL in labels:
                        print('Mail received')

    # Logout and close the connection
    mail.logout()


def get_access_token(creds):
    return creds.token


if __name__ == "__main__":
    # creds = get_gmail_credentials()
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", google_auth.SCOPES)
    else:
        print("No token found!")
        exit()

    while True:
        check_email(creds)
        # Sleep for 30 seconds before checking again
        time.sleep(30)
