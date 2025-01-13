# from django.conf import settings
# from django.core.mail import send_mail
# from django.db.models.signals import post_save,pre_save
# from django.dispatch import Signal
# from django.dispatch import receiver
#
# from .models import CustomUser
#
# registration_confirmation_signal = Signal()
#
# @receiver(pre_save, sender=CustomUser)
# def send_registration_confirmation_email(sender, instance, **kwargs):
#
#         confirmation_code = kwargs.values()
#         email = instance.email
#         print(confirmation_code)
#         print(email)
#         subject = 'Registration Confirmation Code'
#         message = f'Your confirmation code is: {confirmation_code}'
#         send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
#                   [email], fail_silently=False)
#         print(send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
#                         [email],
#                         fail_silently=False))
#
# # def generate_confirmation_code():
# #     # Define your confirmation code generation logic here
# #     pass  # Placeholder for your code
# #
# # # Assuming you have a PasswordResetRequest model for password reset requests
# # from your_app.models import PasswordResetRequest
# #
# # @receiver(post_save, sender=PasswordResetRequest)
# # def send_password_reset_email(sender, instance, created, **kwargs):
# #     if created:
# #         reset_link = f"http://example.com/reset-password/{instance.id}/"  # Generate the reset link here
# #         send_mail(
# #             'Password Reset',
# #             f'Click the following link to reset your password: {reset_link}',
# #             settings.DEFAULT_FROM_EMAIL,
# #             [instance.email],
# #             fail_silently=False,
# #         )
