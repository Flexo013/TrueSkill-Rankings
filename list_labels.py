"""Print all Gmail labels of the authenticated account.

Use this to find the label ID when adding a new game to rankings/games.py.
"""

from googleapiclient.discovery import build

from rankings.auth import load_credentials


def main():
    service = build("gmail", "v1", credentials=load_credentials())
    results = service.users().labels().list(userId="me").execute()
    for label in results.get("labels", []):
        print(f"{label['name']}: {label['id']}")


if __name__ == "__main__":
    main()
