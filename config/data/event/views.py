from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

# Create your views here.
from .models import Event
from .serializers import EventSerializer

class EventListCreate(ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = Event.objects.all()

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset


class EventDetail(RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
