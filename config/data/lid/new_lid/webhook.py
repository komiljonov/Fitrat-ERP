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
        marketing_channel_id = MarketingChannel.objects.filter(name="Olimpiadalar").first().id
        lid = Lid.objects.create(
            first_name=data.get('first_name'),
            last_name=data('last_name'),
            marketing_channel_id=marketing_channel_id,
            photo=None,
            language_choise="UZB",
            subject=None,
            filial=None,
            lid_stage_type="NEW_LID",
            lid_stage="YANGI_LEAD",
            call_operator=None,
            service_manager=None,
            sales_manager=None,
            file=None,
            student=None
        )
        if lid:
            return Response({'status': 'Thank youu mann!'}, status=status.HTTP_201_CREATED)