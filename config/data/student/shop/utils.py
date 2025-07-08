# from decimal import Decimal
#
#
# from .models import Coins, CoinsSettings
#
# def give_coin(type,choice, student,point,):
#
#     if choice == "Speaking":
#         coin = CoinsSettings.objects.filter(
#             choice=choice,
#             type=type,
#             from_point=from_point,
#             to_point=to_point,
#         ).first()
#         if coin:
#             Coins.objects.create(
#                 student=student,
#                 choice=choice,
#                 status="Given",
#                 coin=coin.coin,
#                 comment=f"Sizning {choice} topshirig'idan {from_point}"
#             )