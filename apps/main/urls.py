from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


router = DefaultRouter()
router.register("comments", CommentViewSet)
router.register("favorites", FavoriteViewSet)
router.register('products', ProductViewSet)
router.register("order", OrderViewSet)

urlpatterns = [
	path("", include(router.urls)),
    path('categories/', CategoryListCreateAPIView.as_view()),
    path('categories/<int:pk>/', CategoryDestroyAPIView.as_view()),
    path("rating/", AddRatingAPIView.as_view()),
]