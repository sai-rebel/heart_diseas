from django.contrib import admin
from django.urls import path, re_path
from Cardiovascular_health_prediction import views as mainView
from admins import views as admins
from users import views as usr

from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ Main pages (handle both with and without slash)
    path("", mainView.index, name="index"),
    path("index/", mainView.index),
    path("index", mainView.index),

    path("Adminlogin/", mainView.AdminLogin),
    path("Adminlogin", mainView.AdminLogin),

    path("UserLogin/", mainView.UserLogin),
    path("UserLogin", mainView.UserLogin),

    # ✅ Admin views
    path("AdminLogincheck/", admins.AdminLoginCheck),
    path("AdminLogincheck", admins.AdminLoginCheck),

    path('userDetails/', admins.RegisterUsersView),
    path('userDetails', admins.RegisterUsersView),

    path('ActivUsers/', admins.ActivaUsers),
    path('ActivUsers', admins.ActivaUsers),

    path('DeleteUsers/', admins.DeleteUsers),
    path('DeleteUsers', admins.DeleteUsers),

    path('adminhome/', admins.adminhome),
    path('adminhome', admins.adminhome),

    # ✅ User views
    path('UserRegisterForm/', usr.UserRegisterActions),
    path('UserRegisterForm', usr.UserRegisterActions),

    path("UserLoginCheck/", usr.UserLoginCheck),
    path("UserLoginCheck", usr.UserLoginCheck),

    path("UserHome/", usr.UserHome),
    path("UserHome", usr.UserHome),

    path('DatasetView/', usr.DatasetView),
    path('DatasetView', usr.DatasetView),

    path('training/', usr.training),
    path('training', usr.training),

    path('prediction/', usr.prediction),
    path('prediction', usr.prediction),
]

# ✅ Serve media files (FIX GRAPH ISSUE)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]