from rest_framework import serializers

from .models import Points,Coins,Products,Purchase

from ..student.models import Student
from ..student.serializers import StudentSerializer
from ...upload.models import File
from ...upload.serializers import FileUploadSerializer


class PointsSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), allow_null=True)
    class Meta:
        model = Points
        fields = [
            "id",
            "student",
            "point",
            "comment",
            "from_test",
            "from_homework",
            "is_exchanged",
            "created_at",
        ]
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["student"] = StudentSerializer(instance.student).data
        if instance.from_test:
            rep["from_test"] = FileUploadSerializer(instance.from_test, context=self.context).data
        if instance.from_homework:
            rep["from_homework"] = FileUploadSerializer(instance.from_homework, context=self.context).data
        return rep


class CoinsSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), allow_null=True)
    class Meta:
        model = Coins
        fields = [
            "id",
            "student",
            "comment",
            "is_exchanged",
            "created_at",
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["student"] = StudentSerializer(instance.student).data
        return rep


class ProductsSerializer(serializers.ModelSerializer):
    image = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), allow_null=True)
    class Meta:
        model = Products
        fields = [
            "id",
            "category",
            "coin",
            "image",
            "created_at",
        ]
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["image"] = FileUploadSerializer(instance.image).data
        return rep


class PurchaseSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Products.objects.all(), allow_null=True)
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), allow_null=True)
    class Meta:
        model = Purchase
        fields = [
            "id",
            "product",
            "student",
            "created_at",
        ]
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["student"] = StudentSerializer(instance.student).data
        rep["product"] = ProductsSerializer(instance.product).data
        return rep