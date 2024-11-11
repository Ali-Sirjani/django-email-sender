from django.urls import path

from . import views

app_name = 'email_sender'

urlpatterns = [
    path('', views.MessagePanelView.as_view(), name='msg_panel'),
    path('<int:pk>/', views.MessageDetailView.as_view(), name='msg_detail'),
    path('send/', views.send_and_save_mgs_view, name='msg_panel_send'),
    path('filter-recipients/', views.filter_recipients_view, name='filter_recipients'),
]
