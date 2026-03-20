from django.contrib import admin
from django.urls import path, re_path
from Cardiovascular_health_prediction import views as mainView
from admins import views as admins
from users import views as usr

from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),

    # Main pages
    path("", mainView.index, name="index"),
    path("index/", mainView.index, name="index"),
    path("Adminlogin/", mainView.AdminLogin, name="AdminLogin"),
    path("UserLogin/", mainView.UserLogin, name="UserLogin"),

    # Admin views
    path("AdminLogincheck/", admins.AdminLoginCheck, name="AdminLoginCheck"),
    path('userDetails/', admins.RegisterUsersView, name='RegisterUsersView'),
    path('ActivUsers/', admins.ActivaUsers, name='activate_users'),
    path('DeleteUsers/', admins.DeleteUsers, name='delete_users'),
    path('adminhome/', admins.adminhome, name='adminhome'),

    # User views
    path('UserRegisterForm/', usr.UserRegisterActions, name='UserRegisterForm'),
    path("UserLoginCheck/", usr.UserLoginCheck, name="UserLoginCheck"),
    path("UserHome/", usr.UserHome, name="UserHome"),
    path('DatasetView/', usr.DatasetView, name='DatasetView'),
    path('training/', usr.training, name='training'),
    path('prediction/', usr.prediction, name='prediction'),
]

# ✅ Serve media files (IMPORTANT FOR GRAPHS)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]