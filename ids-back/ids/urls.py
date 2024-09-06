from django.contrib import admin
from django.urls import path

from ids import views

urlpatterns = [
    path('hello/', views.hello_world, name='hello_world'),
    # 数据包相关模块
    path('get_data_packets/', views.get_data_packets, name='data_packets'),
    path('add_data_packet/', views.add_data_packet, name='add_data_packet'),
    path('delete_data_packet/<int:packet_id>/', views.delete_data_packet, name='delete_data_packet'),
    # 用户相关模块
    path('get_users/', views.get_users, name='get_users'),
    path('update_users/', views.update_users, name='update_users'),
    path('delete_users/<int:user_id>/', views.delete_users, name='delete_users'),
    path('login/', views.users_login, name='login'),
    path('register/', views.users_register, name='register'),
    path('get_logged_in_user/', views.get_logged_in_user, name='get_logged_in_user'),
    # 预测管理相关模块
    path('get_prediction_results/', views.get_prediction_results, name='prediction_results'),
    path('delete_prediction_result/<int:predict_id>/', views.delete_prediction_result, name='delete_prediction_result'),
    path('get_prediction_table/', views.get_prediction_table, name='get_prediction_table'),
    path('get_prediction_chart/', views.get_prediction_chart, name='get_prediction_chart'),
    # django自带admin管理模块
    path('admin/', admin.site.urls),
]
