from django.db.models import Sum
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
            "coin",
            "comment",
            "is_exchanged",
            "created_at",
        ]

    # def create(self, validated_data):
    #     if validated_data["student"] and validated_data["coin"] <0:
    #         raise serializers.ValidationError("Coins cannot be negative")
    #
    #     user = Student.objects.get(pk=validated_data["student"])
    #     user.
    #
    #     return Coins.objects.create(**validated_data)


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
            "status",
            "created_at",
        ]

    def create(self, validated_data):
        total = Coins.objects.filter(
            user=self.context["request"].user,
            is_exchanged=False
        ).aggregate(total=Sum("amount"))["total"] or 0

        if total < validated_data.get("product").coin :
            raise serializers.ValidationError(
                "Student does not have enough coins to purchase product"
            )



        return Purchase.objects.create(**validated_data)



    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["student"] = StudentSerializer(instance.student).data
        rep["product"] = ProductsSerializer(instance.product).data
        return rep