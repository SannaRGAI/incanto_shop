from rest_framework.serializers import ModelSerializer, BooleanField, ValidationError
from drf_writable_nested import WritableNestedModelSerializer

from .helpers import send_spam
from .models import *


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def to_representation(self, instance: Product):
        rep = super().to_representation(instance)
        rep["rating"] = instance.average_rating
        rep["comments"] = CommentSerializer(
                                instance.comments.all(),
                                many=True,
                                context=self.context
                            ).data
        return rep

    def create(self, validated_data):
        product = super().create(validated_data)
        send_spam(product)
        return product


class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        exclude = ("user",)

    def validate(self, attrs):
        super().validate(attrs)
        attrs["user"] = self.context["request"].user
        return attrs

    def to_representation(self, instance: Comment):
        rep = super().to_representation(instance)
        rep["user"] = {
            "id": instance.user.id,
            "email": instance.user.email
        }
        return rep


class RatingSerializer(ModelSerializer):
    class Meta:
        model = Rating
        exclude = ("user",)

    def validate(self, attrs):
        super().validate(attrs)
        attrs["user"] = self.context["request"].user
        return attrs

    def create(self, validated_data):
        value = validated_data.pop("value")
        obj, created = Rating.objects.update_or_create(
            **validated_data,
            defaults={"value": value}
        )
        return obj


class FavoriteSerializer(ModelSerializer):
    class Meta:
        model = Favorite
        exclude = ("user",)

    def validate(self, attrs):
        super().validate(attrs)
        attrs["user"] = self.context["request"].user
        return attrs

    def to_representation(self, instance: Favorite):
        rep = super().to_representation(instance)
        rep["product"] = ProductSerializer(instance.product).data
        return rep
    

class OrderItemSerializer(ModelSerializer):
	class Meta:
		model = OrderItem
		exclude = ("order",)


class OrderSerializer(WritableNestedModelSerializer, ModelSerializer):
	items = OrderItemSerializer(many=True)
	is_paid = BooleanField(read_only=True)

	class Meta:
		model = Order
		fields = ("id", "is_paid", "created_at", "total_price", "items")

	def create(self, validated_data):
		validated_data["user"] = self.context.get("request").user
		for item in validated_data["items"]:
			item["product"].quantity -= item["quantity"]
			item["product"].save()
		return super().create(validated_data)

	def validate_items(self, items):
		for item in items:
			if item["quantity"] > item["product"].quantity:
				raise ValidationError("not enough products")
		return items