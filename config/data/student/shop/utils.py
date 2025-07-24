from .models import Coins, CoinsSettings

def give_coin(choice, student, from_point, result_type=None):
    """
    Assign coins to a student based on task and performance.
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

    # ✅ Try Single type: match highest where threshold <= student point
    coin_setting = CoinsSettings.objects.filter(
        choice=choice,
        type="Single",
        from_point_float__lte=from_point
    ).order_by('-from_point_float').first()

    # ✅ Try Double type if no match in Single
    if not coin_setting:
        coin_setting = CoinsSettings.objects.filter(
            choice=choice,
            type="Double",
            from_point_float__lte=from_point,
            to_point_float__gte=from_point
        ).order_by('-from_point_float', '-to_point_float').first()

    if coin_setting:
        Coins.objects.create(
            student=student,
            choice=choice,
            status="Given",
            coin=coin_setting.coin,
            comment=valid_choices[choice].format(choice=choice, coin=coin_setting.coin)
        )
