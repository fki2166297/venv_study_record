from django.urls import path
from . import views


app_name = 'qa'
urlpatterns = [
    path('', views.QuestionAndAnswerView.as_view(), name='qa'),
    path('question-detail/<int:pk>', views.QuestionDetailView.as_view(), name='question_detail'),
    path('question-create', views.QuestionCreateView.as_view(), name='question_create'),
    path('add-supplement/<int:pk>', views.AddSupplementView.as_view(), name='add_supplement'),
    path('question-delete/<int:pk>', views.question_delete_view, name='question_delete'),
    path('answer-create/<int:pk>', views.AnswerCreateView.as_view(), name='answer_create'),
    path('answer-comment-create/<int:pk>/<int:a_pk>', views.answer_comment_create_view, name='answer_comment_create'),
    path('self-resolution/<int:pk>', views.SelfResolutionView.as_view(), name='self_resolution'),
    path('set-best-answer/<int:pk>/<int:a_pk>', views.set_best_answer_view, name='set_best_answer'),
]
