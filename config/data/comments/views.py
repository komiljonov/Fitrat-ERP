from django.db.models import Q
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
)
from rest_framework.permissions import IsAuthenticated

from .models import Comment, StuffComments
from .serializers import CommentSerializer, CommentStuffSerializer


class CommentListCreateAPIView(ListCreateAPIView):
    queryset = Comment.objects.filter()
    serializer_class = CommentSerializer
    # permission_classes = (IsAuthenticated,)


class CommentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)


class CommentLidRetrieveListAPIView(ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        id = self.kwargs.get("pk")
        creator = self.request.query_params.get("creator")
        if id:
            return Comment.objects.filter(Q(lid__id=id) | Q(student__id=id))

        if creator:
            return Comment.objects.filter(
                (Q(lid__id=id) | Q(student__id=id)), creator__id=creator
            )
        return Comment.objects.none()


class CommentAppRead(ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        id = self.kwargs.get("pk")
        creator = self.request.query_params.get("creator")
        if id:
            return Comment.objects.filter(Q(lid__id=id) | Q(student__id=id)).order_by(
                "-created_at"
            )

        if creator:
            return Comment.objects.filter(
                (Q(lid__id=id) | Q(student__id=id)), creator__id=creator
            ).order_by("-created_at")
        return Comment.objects.none()


class CommentStuff(ListCreateAPIView):
    serializer_class = CommentStuffSerializer
    permission_classes = (IsAuthenticated,)
    queryset = StuffComments.objects.all()

    def get_queryset(self):
        id = self.request.query_params.get("id")
        creator = self.request.query_params.get("creator")

        if id:
            return StuffComments.objects.filter(stuff__id=id).order_by("-created_at")

        if creator:
            return StuffComments.objects.filter(
                stuff__id=id, creator__id=creator
            ).order_by("-created_at")

        return StuffComments.objects.none()


class CommentLid(RetrieveUpdateDestroyAPIView):
    queryset = StuffComments.objects.all()
    serializer_class = CommentStuffSerializer
    permission_classes = (IsAuthenticated,)
