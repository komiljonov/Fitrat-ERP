import time
from pydoc_data.topics import topics

import firebase_admin
import icecream
from firebase_admin import credentials, messaging, exceptions

cred = credentials.Certificate("data/notifications/send_notif.json")
firebase_admin.initialize_app(cred)


def send_push(title, msg,topics : str,dataObj=None):
    icecream.ic(topics)
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=msg,
        ),
        data=dataObj,
        tokens=list(topics),
    )

    response = messaging.send_multicast(message)

    print(f"Send successfully ... {response}")