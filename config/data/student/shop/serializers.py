from django.db.models import Sum
from rest_framework import serializers

from .models import Points, Coins, Products, Purchase, Category

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
            "created_at",
        ]

    def create(self, validated_data):
        if validated_data["student"] and validated_data["coin"] <0:
            raise serializers.ValidationError("Coins cannot be negative")

        return Coins.objects.create(**validated_data)


    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["student"] = StudentSerializer(instance.student).data
        return rep

class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "created_at",
        ]

class ProductsSerializer(serializers.ModelSerializer):
    image = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(),many=True ,allow_null=True)
    class Meta:
        model = Products
        fields = [
            "id",
            "name",
            "category",
            "coin",
            "image",
            "created_at",
        ]
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["image"] = FileUploadSerializer(instance.image,many=True ,context=self.context).data
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

        user = Student.objects.get(pk=validated_data["student"])

        if user.coins < validated_data.get("product").coin :
            raise serializers.ValidationError(
                "Student does not have enough coins to purchase product"
            )

        return Purchase.objects.create(**validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["student"] = StudentSerializer(instance.student).data
        rep["product"] = ProductsSerializer(instance.product).data
        return rep


class PointToCoinExchangeSerializer(serializers.Serializer):
    point = serializers.DecimalField(max_digits=10, decimal_places=2)
    student = serializers.CharField()  # or serializers.UUIDField() if ID used

    def validate_point(self, value):
        if value < 10:
            raise serializers.ValidationError("Minimum 10 points required to exchange.")
        return value

