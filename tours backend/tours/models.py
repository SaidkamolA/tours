from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.conf import settings


class Country(models.Model):
    name = models.CharField("Country name", max_length=255)
    photo_url = models.CharField("photo_url", default="https://media.worldnomads.com/Explore/middle-east/hagia-sophia-church-istanbul-turkey-gettyimages-skaman306.jpg")

    def __str__(self):
        return self.name


class Hotel(models.Model):
    name = models.CharField("Hotel name", max_length=255)
    rating = models.IntegerField("Rating", validators=[MinValueValidator(1), MaxValueValidator(5)])
    country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name="Country")
    nutrition = models.TextField("Nutrition")
    info = models.TextField("Info")
    photo_url = models.CharField("photo_url", default="https://media.worldnomads.com/Explore/middle-east/hagia-sophia-church-istanbul-turkey-gettyimages-skaman306.jpg")

    def __str__(self):
        return f"{self.name} ({self.country.name})"


class Tour(models.Model):
    name = models.CharField("Tour name", max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name="Country")
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, verbose_name="Hotel")
    date = models.DateField("Date")
    photo_url = models.CharField("photo_url", default="https://media.worldnomads.com/Explore/middle-east/hagia-sophia-church-istanbul-turkey-gettyimages-skaman306.jpg")


    def __str__(self):
        return self.name


class Review(models.Model):
    name = models.CharField("Review name", max_length=255)
    star = models.IntegerField("Star rating", validators=[MinValueValidator(1), MaxValueValidator(5)])
    user = models.ForeignKey('avtorizate.User', on_delete=models.CASCADE, verbose_name="User  ")
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Hotel")
    description = models.TextField("Description")

    def __str__(self):
        return self.name


class Person(models.Model):
    CATEGORY_CHOICES = [
        ('child', "Child"),
        ('adult', "Adult"),
        ('senior', "Senior"),
    ]
    category = models.CharField("Category", max_length=10, choices=CATEGORY_CHOICES, unique=True)
    price = models.DecimalField("Price", max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.category


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="User  ")
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, verbose_name="Tour")
    people_count = models.IntegerField(default=0, editable=False)
    total_price = models.DecimalField("Total Price", max_digits=10, decimal_places=2, editable=False)
    booking_date = models.DateField("Booking Date", auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    def save(self, *args, **kwargs):
        if not self.pk:
            self.total_price = 0
            self.people_count = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking for {self.tour.name} by {self.user.username} on {self.booking_date}"


class BookingPerson(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='booking_people')
    count = models.IntegerField('Number of persons')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
