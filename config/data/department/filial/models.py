from django.db import models


class Filial(models.Model):
    name = models.CharField(max_length=100)

    tt_filial = models.CharField(max_length=100,null=True,blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
