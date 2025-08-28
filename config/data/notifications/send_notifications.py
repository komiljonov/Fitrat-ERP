import firebase_admin
from firebase_admin import credentials, messaging
from icecream import ic

# Avoid re-initialization
firebase_initialized = False


def initialize_firebase():
    global firebase_initialized
    if firebase_initialized:
        return

    try:
        cred = credentials.Certificate("data/notifications/send_notif.json")
        firebase_admin.initialize_app(cred)
        firebase_initialized = True
        ic("✅ Firebase initialized")
    except Exception as e:
        ic("🔥 Firebase init error:", e)


def send_push_notification(
    title: str,
    body: str,
    token: str = None,
    topic: str = None,
    image: str = None,
    data: dict | None = None,
    badge_count: int = 0,
):
    initialize_firebase()

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
            image=image,
        ),
        token=token,
        topic=topic,
        data=data or {},
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(aps=messaging.Aps(badge=badge_count))
        ),
    )

    try:
        response = messaging.send(message)
        ic("✅ Message sent:", response)
        return response
    except Exception as e:
        ic("❌ Error sending push notification:", e)
        return None


def send_reset_message(topic: str, count: int = 0):
    initialize_firebase()

    message = messaging.Message(
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(content_available=True, badge=count)
            )
        ),
        topic=topic,
    )

    try:
        response = messaging.send(message)
        ic("✅ Reset message sent:", response)
        return response
    except Exception as e:
        ic("❌ Error sending reset message:", e)
        return None
