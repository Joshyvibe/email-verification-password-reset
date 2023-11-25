
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views



urlpatterns = [ 
    path('', index, name='index'),
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('logout/', custom_logout, name='logout'),
    path('activate/<uidb64>/<token>', activate, name='activate'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='core/password_reset_done.html'),
          name='password_reset_done'),
    path('password_reset_complete', auth_views.PasswordResetCompleteView.as_view(template_name='core/password_reset_complete.html'),
          name='password_reset_complete'),
]

