from django.db import models
from django.contrib.auth.models import BaseUserManager


class EmployeeManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().exclude(role__in=["Student", "Parents"])

    @classmethod
    def normalize_email(cls, email):
        """
        Normalize the email address by lowercasing the domain part of it.
        """
        email = email or ""
        try:
            email_name, domain_part = email.strip().rsplit("@", 1)
        except ValueError:
            pass
        else:
            email = email_name + "@" + domain_part.lower()
        return email
