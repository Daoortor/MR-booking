from django.shortcuts import render
from django.utils.dateparse import parse_date
from django.http.response import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
import datetime
import random
from itertools import chain
from django.conf import settings
from .models import BookingModel, MusicRoom, Slot, Code
from .forms import SlotForm, AuthForm, RegForm, CodeForm


def add_rooms(date):
    new_models = []
    for i in range(7):
        new_model = MusicRoom(room_number=i+1, day=date)
        new_model.save()
        new_models.append(new_model)
    return new_models


def add_slots(room):
    for j in range(5):
        new_model = Slot(status='available', user='.', slot_number=j+1, room=room)
        new_model.save()


def init_date(date):
    parent_model = BookingModel(date=parse_date(date))
    parent_model.save()
    for i in add_rooms(parent_model):
        print("New room:", i)
        add_slots(i)
    return parent_model


def check_email(address):
    return address.endswith('@student.letovo.ru')


def root(request):
    return HttpResponseRedirect('/login')


def register(request):
    year = datetime.date.today().year
    month = datetime.date.today().month
    day = datetime.date.today().day
    error = (False, '')
    if request.method == 'POST':
        form = RegForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            if not check_email(email):
                error = (True, 'Введите корректную почту student.letovo.ru')
            elif User.objects.filter(username=username):
                error = (True, 'Это имя пользователя уже занято')
            elif User.objects.filter(email=email):
                error = (True, 'Эта электронная почта уже используется')
            else:
                return HttpResponseRedirect('/reg/confirm/{};{};{}'.format(username, email, password))
    form = RegForm()
    return render(request, 'baseapp/register.html', {'year': year, 'month': month, 'day': day, 'form': form,
                                                     'error': error})


def login_view(request):
    year = datetime.date.today().year
    month = datetime.date.today().month
    day = datetime.date.today().day
    error = (False, '')
    if request.method == 'POST':
        form = AuthForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/booking/' + str(year) + '-' + str(month) + '-' + str(day))
            else:
                error = (True, 'Неправильный логин или пароль')
    else:
        form = AuthForm()
    return render(request, 'baseapp/login.html', {'year': year, 'month': month, 'day': day, 'error': error,
                                                  'form': form})


def booking_monday(request, year, month, day):
    # Day of booking
    date = str(year) + '-' + str(month) + '-' + str(day)
    formatted_date = datetime.date(year, month, day)
    current_date = str(datetime.date.today().year) + '-' + str(datetime.date.today().month) + '-' + str(
        datetime.date.today().day)

    # Create yesterday and tomorrow links
    yesterday_date = formatted_date - datetime.timedelta(1)
    tomorrow_date = formatted_date + datetime.timedelta(1)
    yesterday = '/booking/{}-{}-{}'.format(yesterday_date.year, yesterday_date.month,
                                                                   yesterday_date.day)
    tomorrow = '/booking/{}-{}-{}'.format(tomorrow_date.year, tomorrow_date.month,
                                                                   tomorrow_date.day)
    go_back = date != str(datetime.date.today()) # Check if we can go back (false if we are at today's page)
    message = ('Выберите время и комнату.', '#000')

    if parse_date(date) < parse_date(current_date):
        slots = None
        invalid = True
    else:
        invalid = False
        data = BookingModel.objects.filter(date=parse_date(date))
        if len(data) == 0:
                table = init_date(date)
        else:
            table = data[0]
        rooms = MusicRoom.objects.filter(day=table).order_by('room_number')
        slots = [Slot.objects.filter(room=i).order_by('slot_number') for i in rooms]
        if request.method == 'POST':
            form = SlotForm(request.POST)
            if form.is_valid():
                changing_room = MusicRoom.objects.filter(day=table, room_number=form.cleaned_data['room'])
                slot_number = form.cleaned_data['slot']
                changing_slot = Slot.objects.filter(room__in=changing_room, slot_number__in=slot_number)[0]
                if changing_slot.status == 'available':
                    today_rooms = MusicRoom.objects.filter(day=table)
                    today_slots = [Slot.objects.filter(room=i) for i in today_rooms]
                    today_slots_list = list(today_slots[0])
                    for i in range(1, len(today_slots)):
                        today_slots_list = list(chain(today_slots_list, today_slots[i]))
                    n_booked_today = 0
                    for i in today_slots_list:
                        if i.user == request.user.username:
                            n_booked_today += 1
                            if i.slot_number == int(form.cleaned_data['slot']):
                                message = ('Вы уже забронировали комнату в это время.', '#E8A200')
                                break
                    if n_booked_today >= 2:
                        message = ('Вы не можете бронировать больше 2 слотов в один день.', '#FF5555')
                    if message == ('Выберите время и комнату.', '#000'):
                        changing_slot.status = 'reserved'
                        changing_slot.user = request.user.username
                        changing_slot.save()
                elif changing_slot.status == 'reserved' and changing_slot.user == request.user.username:
                    message = ('Вы уже забронировали этот слот.', '#008080')
                elif changing_slot.status == 'reserved' and changing_slot.user != request.user.username:
                    message = ('Этот слот уже занят.', '#FF5555')
                elif changing_slot.status == 'lesson':
                    message = ('В это время здесь проходит занятие.', '#FF5555')
        else:
            form = SlotForm()
    return render(request, 'baseapp/daily.html', {'user': request.user, 'slots': slots, 'year': year, 'month': month,
                                                  'day': day, 'invalid': invalid, 'form': form, 'message': message,
                                                  'yesterday': yesterday, 'tomorrow': tomorrow, 'go_back': go_back})


def cancel(request, year, month, day):
    booking_data = BookingModel.objects.filter(date=datetime.date(year, month, day))[0]
    rooms = MusicRoom.objects.filter(day=booking_data).order_by('room_number')
    slots = [Slot.objects.filter(room=i) for i in rooms]
    slot_list = list(slots[0])
    for i in range(1, len(slots)):
        slot_list = list(chain(slot_list, slots[i]))
    for i in slot_list:
        if i.user == request.user.username:
            i.status = 'available'
            i.user = '.'
            i.save()
    return HttpResponseRedirect('/booking/' + str(year) + '-' + str(month) + '-' + str(day))


def confirm_email(request, username, email, password):
    error = (False, '')
    key = None
    if request.method == 'POST':
        form = CodeForm(request.POST)
        if form.is_valid():
            answer = form.cleaned_data['code']
            code_model = Code.objects.all()[0]
            if answer == code_model.code:
                User.objects.create_user(username=username, email=email, password=password)
                return HttpResponseRedirect('/login')
            else:
                print('False code', key)
                error = (True, 'Неверный код')
    else:
        form = CodeForm()
        key = random.randrange(1, 999999)
        code_model = Code.objects.all()[0]
        code_model.code = key
        code_model.save()
        send_mail(subject='Подтверждение электронной почты', message='Ваш код регистрации - ' + str(key) + '.',
                  from_email=settings.EMAIL_FROM, recipient_list=[email])
    return render(request, 'baseapp/confirm.html', {'error': error, 'key': key, 'form': form})


def feedback(request):
    year = datetime.date.today().year
    month = datetime.date.today().month
    day = datetime.date.today().day
    return render(request, 'baseapp/feedback.html', {'year': year, 'month': month, 'day': day})
