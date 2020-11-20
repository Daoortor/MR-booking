from django.db import models
import sys
sys.path.append('C:/Users/katja/PycharmProjects/django/taskmanager')


class BookingModel(models.Model):
    date = models.DateField(default="2020-10-28")

    def __str__(self):
        return str(self.date)

    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = 'Booking'


class MusicRoom(models.Model):
    room_number = models.IntegerField()
    day = models.ForeignKey(BookingModel, default=1, verbose_name="day", on_delete=models.CASCADE)

    def __str__(self):
        return "MR" + str(self.room_number)

    class Meta:
        verbose_name_plural = "MusicRoom"


class Slot(models.Model):
    status = models.CharField(max_length=16)
    user = models.CharField(max_length=32)
    slot_number = models.IntegerField(default=1)
    room = models.ForeignKey(MusicRoom, default=1, verbose_name="room", on_delete=models.CASCADE)

    def __str__(self):
        return "Slot " + str(self.slot_number) + " of " + str(self.room) + " on " + str(self.room.day)


class Code(models.Model):
    code = models.IntegerField(default=0)
