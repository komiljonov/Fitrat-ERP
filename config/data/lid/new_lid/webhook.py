import os

from django.http import HttpResponseForbidden
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from data.lid.new_lid.models import Lid


class WebhookView(APIView):
    def post(self, request, *args, **kwargs):
        secret = request.headers.get("X-Webhook-Secret")
        expected_secret = os.getenv("WEBHOOK_SECRET")

        if secret != expected_secret:
            return HttpResponseForbidden("Invalid webhook secret")

        data = request.data
        if data:
            lid = Lid.objects.create(
                phone=data["phone"] or "",
                first_name=data["first_name"] or "",
                marketing_channel=data["marketing_channel"] or "",
                lid_stage_type="NEW_LID",
                lid_stages="YANGI_LEAD"
            )
            if lid:
                return Response({"id": lid.id},
                                status=status.HTTP_200_OK)

        return Response({"message": "Webhook received"}, status=status.HTTP_200_OK)