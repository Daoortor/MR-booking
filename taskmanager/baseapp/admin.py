from django.contrib import admin
from .models import MusicRoom, Slot, BookingModel, Code


admin.site.register(BookingModel)
admin.site.register(MusicRoom)
admin.site.register(Slot)
admin.site.register(Code)
