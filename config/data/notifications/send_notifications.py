import time
from pydoc_data.topics import topics
from uuid import UUID

import firebase_admin
import icecream
from firebase_admin import credentials, messaging, exceptions
from icecream import ic
if not firebase_admin._apps:
    cred = credentials.Certificate("data/notifications/send_notif.json")
    firebase_admin.initialize_app(cred)


def send_push(title, msg, topics, dataObj=None):
    if isinstance(topics, (str, UUID)):
        topics = [str(topics)]  # Convert UUID to string and wrap it in a list

    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=msg,
        ),
        data=dataObj,
        tokens=topics,  # Ensure topics is a list
    )

    try:
        response = messaging.send_multicast(message)
        print(f"Send successfully ... {response}")
        return response
    except Exception as e:
        print(f"Unexpected error: {e}")