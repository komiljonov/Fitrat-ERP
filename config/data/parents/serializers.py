from rest_framework import serializers

from data.parents.models import Relatives


class RelativesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relatives
        fields = ['id',
                  'name',
                  'phone',
                  'who',
                  ]
