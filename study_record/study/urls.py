from django.urls import path
from . import views


app_name = 'study'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('studyrecord-create', views.StudyRecordCreateView.as_view(), name='studyrecord_create'),
    path('studyrecord-update/<int:pk>', views.StudyRecordUpdateView.as_view(), name='studyrecord_update'),
    path('studyrecord-delete/<int:pk>', views.StudyRecordDeleteView.as_view(), name='studyrecord_delete'),
    path('report', views.ReportView.as_view(), name='report'),
    path('get-bar-chart-data-week', views.GetBarChartDataWeek.as_view(), name='get_bar_chart_data_week'),
    path('get-bar-chart-data-month', views.GetBarChartDataMonth.as_view(), name='get_bar_chart_data_month'),
    path('get-bar-chart-data-year', views.GetBarChartDataYear.as_view(), name='get_bar_chart_data_year'),
    path('subject', views.SubjectView.as_view(), name='subject'),
    path('subject-create', views.SubjectCreateView.as_view(), name='subject_create'),
    path('subject/subject-update/<int:pk>', views.SubjectUpdateView.as_view(), name='subject_update'),
    path('subject/subject-delete/<int:pk>', views.SubjectDeleteView.as_view(), name='subject_delete'),
    path('account-search', views.AccountSearchView.as_view(), name='account_search'),
    path('<int:pk>', views.AccountDetailView.as_view(), name='account_detail'),
    path('<int:pk>/following', views.AccountFollowingView.as_view(), name='account_following'),
    path('<int:pk>/followers', views.AccountFollowersView.as_view(), name='account_followers'),
    path('<int:pk>/follow', views.FollowView.as_view(), name='follow'),
    path('<int:pk>/unfollow', views.UnfollowView.as_view(), name='unfollow'),
    path('<int:pk>/edit', views.AccountUpdateView.as_view(), name='account_update'),
]
