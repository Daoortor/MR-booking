from django.urls import path
from . import views


urlpatterns = [
    path('', views.root, name='home'),
    path('reg', views.register, name='reg'),
    path('reg/confirm/<str:username>;<str:email>;<str:password>', views.confirm_email,
         name='confirm'),
    path('login', views.login_view, name='login'),
    path('feedback', views.feedback, name='contacts'),
    path('booking/<int:year>-<int:month>-<int:day>', views.booking_monday, name='daily'),
    path('booking/<int:year>-<int:month>-<int:day>/cancel', views.cancel, name='cancel')
]
