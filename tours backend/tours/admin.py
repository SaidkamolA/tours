from django.contrib import admin

from avtorizate.models import User, VerificationCode
from tours.models import Tour, Country, Hotel, Review, Person, BookingPerson, Booking

# Register your models here.
admin.site.register(Tour)
admin.site.register(Country)

admin.site.register(Hotel)
admin.site.register(Review)
admin.site.register(Person)
admin.site.register(BookingPerson)
admin.site.register(Booking)

admin.site.register(User)
admin.site.register(VerificationCode)
