from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from .forms import RegisterForm, LoginForm
from django.urls import reverse
from .datebase_func import make_bd, check_car_wash, add_car_wash, time_by_id, update_time_by_id, get_info_about
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import requests
from pprint import pprint
from datetime import datetime


def time_to_seconds(time):
    time = time.split(':')
    hh = 0
    mm = 0
    ss = 0
    if len(time) == 2:
        hh = int(time[0])
        mm = int(time[1])
    if len(time) == 3:
        hh = int(time[0])
        mm = int(time[1])
        ss = int(time[2])
    return hh * 3600 + mm * 60 + ss

def second_to_str(time):
    hh = time // 3600 % 24
    mm = time // 60 % 60
    ss = time % 60
    result = f"{hh}:{mm}:{ss}"
    return result


def fast_search_car_wash(data, u=None):
    data = dict(data)
    current_time = datetime.now()
    cur_pos = data.get('pos')[0]
    count = int(data.get('count')[0])
    make_bd()
    winner_id = wash_id = data.get('0id')[0]
    pohui = 99999999999
    time_to_wash = 15*60
    for i in range(count):

        name = data.get(str(i) + 'name')[0]
        wash_id = data.get(str(i) + 'id')[0]
        wash_cord = data.get(str(i) + 'coords')[0]

        if not check_car_wash(wash_id):
            add_car_wash(wash_id, name, wash_cord)


        request_body = 'https://api.distancematrix.ai/maps/api/distancematrix/json?'
        request_body += f'origins={cur_pos}&'
        request_body += f'destinations={wash_cord}&'
        request_body += 'key=FEn4bf73mLF76mUkqYyaJI5UiDc6g'

        response = requests.get(request_body)
        print(response.text)
        trip_time = response.json()['rows'][0]['elements'][0]['duration']['value']

        trip_minutes = trip_time // 60
        trip_seconds = trip_time % 60
        trip_hours = trip_time // 3600

        #pprint(f'{trip_hours}:{trip_minutes}:{trip_seconds}')

        current_minutes = int(current_time.strftime('%M'))
        current_seconds = int(current_time.strftime('%S'))
        current_hours = int(current_time.strftime('%H'))

        arrive_seconds = trip_seconds + current_seconds
        arrive_minutes = trip_minutes + current_minutes
        arrive_hours = trip_hours + current_hours
        days = 0

        if arrive_seconds // 60 != 0:
            arrive_minutes += arrive_seconds // 60
            arrive_seconds %= 60

        if arrive_minutes // 60 != 0:
            arrive_hours += arrive_minutes // 60 % 60
            arrive_minutes %= 60

        if arrive_hours // 24 != 0:
            days = arrive_hours // 24
            arrive_hours %= 24

        #pprint(f'{days}  {arrive_hours}:{arrive_minutes}:{arrive_seconds}')

        arrive_time = str(arrive_hours) + ':' + str(arrive_minutes) + ':' + str(arrive_seconds)
        open_time, close_time, free_time = time_by_id(wash_id)

        if days == 0:
            if time_to_seconds(arrive_time) + time_to_wash < time_to_seconds(close_time):
                start_time = max(time_to_seconds(arrive_time), time_to_seconds(free_time))
                #pprint(second_to_str(start_time))
                if start_time < pohui:
                    pohui =  start_time
                    winner_id = wash_id

    #pprint(second_to_str(pohui))
    update_time_by_id(winner_id, second_to_str(pohui + time_to_wash))
    result = {}
    response = get_info_about(winner_id)
    coords_xy = response[2].split(',')
    result['coords_x'] = coords_xy[0]
    result['coords_y'] = coords_xy[1]
    pos_xy = cur_pos.split(',')
    result['pos_x'] = pos_xy[0]
    result['pos_y'] = pos_xy[1]
    if u is not None:
        print('NICE')
        u.email_user(subject='Талон на автомойку',
                   message=f'Вы записаны на автомойку, приезжайте к {second_to_str(pohui)}',
                   from_email='car.wash.agrigator@gmail.com'
                   )

    return result

def main_page(request):
    u = request.user
    flag = u.is_authenticated
    data = ''
    if request.method == 'POST' and request.is_ajax:
        if request.POST.get('pos') is not None:
            print("hui")
            u = request.user
            if u.is_authenticated:
                data = fast_search_car_wash(request.POST, u)
                print(data)
                request.session['data'] = data
                return HttpResponseRedirect('/main/road_map')
                #return redirect('mainpages:road_map')

    if flag:
        data = {
            'button_1': 'logout_user',
            'flag': flag,
        }
        return render(
            request,
            'main_page.html',
            context=data
        )
    else:
        data = {
            'button_1': 'auth',
            'flag': flag,
        }
        return render(
            request,
            'main_page.html',
            context=data
        )


def auth_page(request):
    data = {
        'button_1' : 'login',
        'button_2': 'registration'
    }
    return render(
        request,
        'authorization.html',
        context=data
    )

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get("login")
        password = request.POST.get("password")
        pprint(username)
        pprint(password)
        if password is not None:
            username = request.POST.get("login")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/main')
            else:
                form = LoginForm()
                data = {
                            "text": "Неверный логин или пароль",
                        }
                return render(
                    request,
                    'login.html',
                    context=data,
                )
    else:
        return render(
            request,
            'login.html',
        )

def registration_page(request):
    if request.method == 'POST':
        username = request.POST.get("login")
        password = request.POST.get("password")
        re_password = request.POST.get("re_password")
        mail = request.POST.get("mail")
        pprint(username)
        pprint(password)
        if re_password is not None:
            if password != re_password:
                data = {
                    'text': 'Пароли не совпадают',
                }
                return render(
                    request,
                    'registration.html',
                    context=data,
                )
            try:
                validate_email(mail)
            except ValidationError as e:
                data = {
                    'text': 'Неверный формат email' + str(e)
                }
                return render(
                    request,
                    'registration.html',
                    context=data,
                )

            names = get_user_model()
            names = list(names.objects.all())

            for name in names:
                if username in str(name):
                    form = RegisterForm()
                    data = {
                                "text": "Пользователь с таким логином уже существует",
                            }
                    return render(
                        request,
                        'registration.html',
                        context=data,
                    )
            user = User.objects.create_user(
                username=username,
                password=password,
                email=mail
            )
            user.save()
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/main')
    else:
        return render(
            request,
            'registration.html',
        )

def logout_user(request):
    u = request.user
    if u.is_authenticated:
        logout(request)
    return redirect('/')

def road_map(request):
    data = request.session['data']
    print(data)
    print('PIZDA')
    print(request.GET)
    return render(
        request,
        'map.html',
        context=data
    )
