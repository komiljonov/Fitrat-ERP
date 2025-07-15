from rest_framework import serializers

from .models import Points, Coins, Products, Purchase, Category, CoinsSettings
from ..student.models import Student
from ..student.serializers import StudentSerializer
from ...account.models import CustomUser
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


class CoinsSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinsSettings
        fields = [
            "id",
            "type",
            "from_point",
            "to_point",
            "coin",
            "created_at",
        ]


class CoinsSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), allow_null=True)

    class Meta:
        model = Coins
        fields = [
            "id",
            "student",
            "coin",
            "comment",
            "status",
            "created_at",
        ]

    def create(self, validated_data):
        if validated_data["student"] and validated_data["coin"] < 0:
            raise serializers.ValidationError("Coins cannot be negative")

        return Coins.objects.create(**validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["student"] = StudentSerializer(instance.student).data
        return rep


class CategoriesSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "products",
            "created_at",
        ]

    def get_products(self, instance):
        return Products.objects.filter(category=instance).count()


class ProductsSerializer(serializers.ModelSerializer):
    image = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True, allow_null=True)
    selling_counts = serializers.SerializerMethodField()

    class Meta:
        model = Products
        fields = [
            "id",
            "name",
            "comment",
            "category",
            "coin",
            "image",
            "selling_counts",
            "created_at",
        ]

    def get_selling_counts(self, instance):
        return Purchase.objects.filter(product=instance).count()

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["image"] = FileUploadSerializer(instance.image, many=True, context=self.context).data
        return rep


class PurchaseSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Products.objects.all(), allow_null=True)
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), allow_null=True)
    updater = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), allow_null=True)

    class Meta:
        model = Purchase
        fields = [
            "id",
            "product",
            "student",
            "status",
            "updater",
            "comment",
            "created_at",
        ]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.updater = self.context["request"].user  # FIX HERE
        instance.save()

        return instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["student"] = StudentSerializer(instance.student, context=self.context).data
        rep["product"] = ProductsSerializer(instance.product, context=self.context).data
        rep["updater"] = {
            "id": instance.updater.id,
            "full_name": instance.updater.full_name,
        } if instance.updater is not None else None
        return rep

    def create(self, validated_data):

        user = Student.objects.filter(id=validated_data["student"].get("id")).first()

        if user.coins < validated_data.get("product").coin:
            raise serializers.ValidationError(
                "Student does not have enough coins to purchase product"
            )

        return Purchase.objects.create(**validated_data)


class PointToCoinExchangeSerializer(serializers.Serializer):
    point = serializers.DecimalField(max_digits=10, decimal_places=2)
    student = serializers.CharField()  # or serializers.UUIDField() if ID used

    def validate_point(self, value):
        if value < 10:
            raise serializers.ValidationError("Minimum 10 points required to exchange.")
        return value
