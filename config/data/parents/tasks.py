from celery import shared_task

from config.data.account.models import CustomUser
from data.student.student.sms import SayqalSms
from data.parents.models import Relatives

sms = SayqalSms()


@shared_task
def send_creds_to_relatives(relative_id: str, password: str):

    relative = CustomUser.objects.filter(id=relative_id).first()

    if relative is None:
        return "Relative not found"

    res = sms.send_sms(
        number=relative.phone,
        message=f"""
                    Fitrat Ota - Onalar uchun ilovasiga muvaffaqiyatli ro‘yxatdan o‘tdingiz!
    
                    Login: {relative.phone}
                    Parol: {password}
    
                    Iltimos, ushbu ma’lumotlarni hech kimga bermang. Ilovaga kirib bolangizning natijalarini kuzatishingiz mumkin.
                    """,
    )

    print(res)
