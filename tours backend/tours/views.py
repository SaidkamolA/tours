from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser , AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Country, Hotel, Tour, Review, Person, Booking, BookingPerson
from .serializers import (
    CountrySerializer, HotelSerializer, TourSerializer,
    ReviewSerializer, PersonSerializer, BookingSerializer
)

class CountryListCreateView(generics.ListCreateAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [AllowAny]

class CountryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAdminUser ]

class HotelListCreateView(generics.ListCreateAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [AllowAny]

class HotelDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [IsAdminUser ]

class TourListCreateView(generics.ListCreateAPIView):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    permission_classes = [AllowAny]

class TourDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    permission_classes = [AllowAny]

class BookingCreateView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        tour_id = request.data.get("tour")
        people_data = request.data.get("booking_people")
        tour = get_object_or_404(Tour, pk=tour_id)

        if not isinstance(people_data, list) or not people_data:
            return Response({"error": "Invalid people data"}, status=status.HTTP_400_BAD_REQUEST)

        booking = Booking.objects.create(user=request.user, tour=tour)
        total_price = 0
        total_people_count = 0

        for person_data in people_data:
            if not isinstance(person_data, dict):
                return Response({"error": "Invalid person data"}, status=status.HTTP_400_BAD_REQUEST)

            category = person_data.get("person")
            count = person_data.get("count", 0)


            category_instance = get_object_or_404(Person, category=category)
            if count < 1:
                return Response({"error": "Invalid person data"}, status=status.HTTP_400_BAD_REQUEST)

            BookingPerson.objects.create(person=category_instance, booking=booking, count=count)

            total_price += count * category_instance.price
            total_people_count += count

        booking.total_price = total_price
        booking.people_count = total_people_count
        booking.save()

        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class BookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]

class PersonListView(generics.ListAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = [AllowAny]

class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)



