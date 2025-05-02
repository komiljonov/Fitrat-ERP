import os

from django.http import HttpResponseForbidden
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from data.department.marketing_channel.models import MarketingChannel
from data.lid.new_lid.models import Lid


class LidWebhook(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        if not data:
            return Response({'error': 'No data provided'}, status=status.HTTP_400_BAD_REQUEST)

        marketing_channel = MarketingChannel.objects.filter(name="Olimpiadalar").first()
        if not marketing_channel:
            return Response({'error': 'Marketing channel not found'}, status=status.HTTP_400_BAD_REQUEST)

        lid = Lid.objects.create(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone_number=data.get('phone_number'),
            marketing_channel=marketing_channel,
            photo=None,
            subject=None,
            filial=None,
            lid_stage_type="NEW_LID",
            lid_stages="YANGI_LEAD",
            call_operator=None,
            service_manager=None,
            sales_manager=None,
            student=None
        )

        # Set many-to-many field AFTER creation
        lid.file.set([])  # empty list, or pass a list of File objects/IDs

        return Response({'status': 'Thank youu mann!'}, status=status.HTTP_201_CREATED)
