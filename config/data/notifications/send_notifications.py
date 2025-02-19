import time
from pydoc_data.topics import topics
from uuid import UUID

import firebase_admin
import icecream
from firebase_admin import credentials, messaging, exceptions
from icecream import ic
def initialize_firebase():
    cred = credentials.Certificate("data/notifications/send_notif.json")
    firebase_admin.initialize_app(cred)



def send_push_notification(
    title,
    body,
    token: str = None,
    topic: str = None,
    image: str = None,
    data: dict | None = None,
    badge_count: int = 0,
):

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
            image=image,
        ),
        token=token,
        topic=topic,
        data=data,
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(aps=messaging.Aps(badge=badge_count))
        ),
    )

    # Send the message
    try:
        response = messaging.send(message)
    except Exception as e:
        print(f"Error sending message: {e}")


def send_reset_message(topic: str, count):
    # print("Send")

    message = messaging.Message(
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    content_available=True, badge=count  # Resetting badge count to 0
                )
            )
        ),
        topic=topic,
    )

    # Send the message
    try:
        response = messaging.send(message)
        # print(f"Successfully sent message: {response}")
    except Exception as e:
        print(f"Error sending message: {e}")