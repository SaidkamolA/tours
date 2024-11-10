from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import Country, Hotel, Tour, Review, Booking, Person, BookingPerson

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'photo_url']


class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ['id', 'name', 'rating', 'country', 'nutrition', 'info', 'photo_url']


class TourSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tour
        fields = ['id', 'name', 'country', 'hotel', 'date', 'photo_url']

class ReviewSerializer(serializers.ModelSerializer):
    star = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Review
        fields = ['id', 'hotel', 'user', 'star', 'description']

class BookingPersonSerializer(serializers.ModelSerializer):
    person = serializers.CharField(source='person.category')

    class Meta:
        model = BookingPerson
        fields = ['person', 'count']

class BookingSerializer(serializers.ModelSerializer):
    total_price = serializers.ReadOnlyField()
    booking_people = BookingPersonSerializer(many=True)

    class Meta:
        model = Booking
        fields = ['id', 'user', 'tour', 'total_price', 'booking_people', 'is_paid']

    def create(self, validated_data):
        people_data = validated_data.pop('booking_people', [])
        booking = super().create(validated_data)

        total_price = 0
        for person_data in people_data:
            category = person_data.get("category")
            count = person_data.get("count", 0)

            if count < 1 or not category:
                continue

            BookingPerson.objects.create(person=category, booking=booking, count=count)
            total_price += count * category.price

        booking.total_price = total_price
        booking.save()

        return booking

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['id', 'category', 'price']
        read_only_fields = ['id']

