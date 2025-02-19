import time
from pydoc_data.topics import topics
from uuid import UUID

import firebase_admin
import icecream
from firebase_admin import credentials, messaging, exceptions
from icecream import ic

cred = credentials.Certificate("data/notifications/send_notif.json")
firebase_admin.initialize_app(cred)


def send_push(title, msg, topics, dataObj=None):
    ic(topics)

    # Ensure topics is a list of strings
    if isinstance(topics, (str, UUID)):
        topics = [str(topics)]  # Convert UUID to string and wrap it in a list

    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=msg,
        ),
        data=dataObj,
        tokens=topics,  # Now topics is guaranteed to be a list of strings
    )

    response = messaging.send_multicast(message)

    print(f"Send successfully ... {response}")
