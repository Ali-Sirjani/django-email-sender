from django.urls import path

from . import views

app_name = 'email_sender'

urlpatterns = [
    path('', views.MessagePanelView.as_view(), name='msg_panel'),
    path('send/', views.send_and_save_mgs_view, name='msg_panel_send'),
]
