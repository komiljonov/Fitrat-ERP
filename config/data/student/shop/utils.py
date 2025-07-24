from .models import Coins, CoinsSettings

def give_coin(type, choice, student, from_point, to_point=None, result_type=None):
    """
    Assign coins to a student based on task type and performance.
    """

    valid_choices = {
        "Speaking": "Siz {choice} topshirig'ini bajarganingiz uchun {coin} coinlar berildi.",
        "Homework": "Siz Uy ishini bajarganingiz uchun {coin} coinlar berildi.",
        "Mock": "Siz Mock imtihonida qatnashganingiz uchun {coin} coinlar berildi.",
        "Unit": "Siz Unit imtihonida qatnashganingiz uchun {coin} coinlar berildi.",
        "Weekly": "Siz Haftalik imtihonida qatnashganingiz uchun {coin} coinlar berildi.",
        "Monthly": "Siz Oylik imtihonida qatnashganingiz uchun {coin} coinlar berildi.",
    }

    if choice not in valid_choices:
        return "Choice is not valid"

    filters = {
        'choice': choice,
        'type': type,
        'from_point_float__lte': from_point,
    }

    print(filters)

    if type == "Single":
        coin_setting = CoinsSettings.objects.filter(**filters).order_by('-from_point_float').first()

    elif type == "Double" and to_point is not None:
        filters.update({
            'to_point_float__lte': to_point
        })

        coin_setting = CoinsSettings.objects.filter(**filters).order_by('-from_point_float', '-to_point_float').first()

    else:
        coin_setting = None

    if coin_setting:

        print(coin_setting)
        Coins.objects.create(
            student=student,
            choice=choice,
            status="Given",
            coin=coin_setting.coin,
            comment=valid_choices[choice].format(choice=choice, coin=coin_setting.coin)
        )
