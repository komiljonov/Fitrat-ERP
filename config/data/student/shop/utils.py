from decimal import Decimal
from .models import Coins, CoinsSettings

def get_coin(choice: str, type: str = "Single", from_point: str = None, to_point: str = None) -> Decimal | None:
    query = CoinsSettings.objects.filter(type=type, choice=choice)

    if from_point:
        query = query.filter(from_point=from_point)
    if to_point and type == "Double":
        query = query.filter(to_point=to_point)

    point = query.first()
    return point.coin if point and point.coin > 0 else None

def give_coin(
    student,
    choice: str,
    type: str = "Single",
    from_point: str = None,
    to_point: str = None,
    comment: str = ""
) -> Coins | None:
    """
    Create a Coins entry for a student based on coin settings.
    - type: "Single" or "Double"
    - from_point and to_point are used for filtering CoinsSettings
    """
    if not student:
        return None

    coin_value = get_coin(choice=choice, type=type, from_point=from_point, to_point=to_point)

    if not coin_value:
        coin_value = 0

    # Auto-generate comment if not provided
    if not comment:
        if type == "Single":
            comment = f"{choice} uchun {coin_value} coin berildi (daraja: {from_point})."
        else:
            comment = f"{choice} uchun {coin_value} coin berildi (daraja: {from_point} → {to_point})."

    return Coins.objects.create(
        coin=coin_value,
        student=student,
        choice=choice,
        comment=comment
    )
