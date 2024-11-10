from django.urls import path
from .views import (
    CountryListCreateView, CountryDetailView,
    HotelListCreateView, HotelDetailView,
    TourListCreateView, TourDetailView,
    ReviewListCreateView, ReviewDetailView,
    BookingListView, BookingCreateView, BookingDetailView,
    PersonListView
)

urlpatterns = [
    path('countries/', CountryListCreateView.as_view(), name='country-list-create'),
    path('countries/<int:pk>/', CountryDetailView.as_view(), name='country-detail'),

    path('hotels/', HotelListCreateView.as_view(), name='hotel-list-create'),
    path('hotels/<int:pk>/', HotelDetailView.as_view(), name='hotel-detail'),

    path('tours/', TourListCreateView.as_view(), name='tour-list-create'),
    path('tours/<int:pk>/', TourDetailView.as_view(), name='tour-detail'),

    path('reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),

    path('booking/', BookingCreateView.as_view(), name='booking-create'),
    path('tours/booking/<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),
    path('tours/booking/list/', BookingListView.as_view(), name='booking-list'),
    path('people/', PersonListView.as_view(), name='person-list'),
]
