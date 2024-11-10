from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from cards.views import  CardViewSet, CategoryViewSet, TransactionViewSet

urlpatterns = [

    path('cards/', CardViewSet.as_view({'get': 'list', 'post': 'create'}), name='card_view'),
    path('cards/<int:pk>/', CardViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='card_detail'),

    path('categories/', CategoryViewSet.as_view({'get': 'list'}), name='category_view'),
    path('categories/<int:pk>/', CategoryViewSet.as_view({'get': 'retrieve'}), name='category_detail'),

    path('transactions/', TransactionViewSet.as_view({'get': 'list', 'post': 'transfer'}), name='transaction_view'),
    path('transactions/<int:pk>/', TransactionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='transaction_detail'),
]
