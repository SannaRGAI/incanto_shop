from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins
from rest_framework.generics import ListCreateAPIView, DestroyAPIView
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from .models import Order, Category, Product, Comment, Rating, Favorite
from .permissions import IsAuthor, IsAdminOrReadOnly
from .serializers import OrderSerializer, CategorySerializer, ProductSerializer, CommentSerializer, RatingSerializer, FavoriteSerializer
from .tasks import send_successful_payment_message, send_error_payment_message


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filterset_fields = ('category',)
    search_fields = ('title', 'description')


class CategoryListCreateAPIView(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class CategoryDestroyAPIView(DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]


class OrderViewSet(ModelViewSet):
	queryset = Order.objects.all()
	serializer_class = OrderSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		return self.queryset.filter(user=self.request.user)

	@action(["GET"], detail=True)
	def pay(self, request, pk):
		order: Order = self.get_object()
		# order = get_object_or_404(Order, id=pk)
		if order.is_paid:
			return Response("already paid", status=400)
		if order.user.billing.withdraw(order.total_price):
			order.is_paid = True
			order.save()
			send_successful_payment_message.delay(
				email=order.user.email,
				total_price=order.total_price,
				items=[
					{"title": i.product.title, "quantity": i.quantity}
					for i in order.items.all()
				]
			)
			return Response(status=200)
		send_error_payment_message(
			email=order.user.email,
			order=order
		)
		return Response("Not enough money", status=400)


class CommentViewSet(mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsAuthor]


class FavoriteViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      GenericViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated, IsAuthor]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class AddRatingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=RatingSerializer())
    def post(self, request):
        serializer = RatingSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)