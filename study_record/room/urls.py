from django.urls import path
from . import views


app_name = 'room'
urlpatterns = [
    path('', views.RoomTopView.as_view(), name='room_top'),
    path('room-create', views.RoomCreateView.as_view(), name='room_create'),
    path('select-subject/<int:pk>', views.SelectSubjectView.as_view(), name='select_subject'),
    path('<int:pk>', views.RoomView.as_view(), name='room'),
    path('get-room-member/<int:pk>', views.GetRoomMemberView.as_view(), name='get_room_member'),
    path('get-room-message/<int:pk>', views.GetRoomMessageView.as_view(), name='get_room_message'),
]
