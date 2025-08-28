from celery import shared_task
import requests

from data.account.models import CustomUser
from data.student.student.sms import SayqalSms

sms = SayqalSms()


@shared_task(
    bind=True,
    autoretry_for=(requests.exceptions.ConnectTimeout,),
    retry_kwargs={"max_retries": 3, "countdown": 5},
)
def send_creds_to_relatives(self, relative_id: str, password: str):

    relative = CustomUser.objects.filter(id=relative_id).first()
    if relative is None:
        return "Relative not found"

    res = sms.send_sms(
        number=relative.phone,
        message=f"""
            Fitrat Ota - Onalar uchun ilovasiga muvaffaqiyatli ro‘yxatdan o‘tdingiz!

            Login: {relative.phone}
            Parol: {password}

            Iltimos, ushbu ma’lumotlarni hech kimga bermang. 
            Ilovaga kirib bolangizning natijalarini kuzatishingiz mumkin.
        """,
    )
    return res
