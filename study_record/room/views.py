from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.views import generic
from .forms import RoomCreateForm, SubjectForm
from .models import Room, RoomMember, RoomMessage
from study.models import Subject, StudyRecord
from django.core import serializers
import json


# Create your views here.
class RoomTopView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'room_top.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['my_room_list'] = Room.objects.select_related().filter(host=self.request.user)
        context['follower_room_list'] = Room.objects.select_related().filter(publication='follower').exclude(host=self.request.user)
        context['public_room_list'] = Room.objects.select_related().filter(publication='public').exclude(host=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        # 学習記録の登録
        record_objects = []
        print(request.POST['records'])
        records = json.loads(request.POST['records'])
        for record in records:
            record_objects.append(
                StudyRecord(
                    user=self.request.user,
                    subject=Subject.objects.get(pk=int(record['subject'])),
                    studied_at=record['studied_at'],
                    minutes=int(record['microseconds'] / 1000 // 60),
                )
            )
        StudyRecord.objects.bulk_create(record_objects)

        # ルームメンバーの削除
        RoomMember.objects.filter(user=self.request.user).delete()

        messages.success(self.request, '学習記録を作成しました。')
        return HttpResponseRedirect(reverse_lazy('room:room_top'))


class RoomCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'room_create.html'
    form_class = RoomCreateForm
    success_url = reverse_lazy('study:home')

    def get_success_url(self):
        return reverse_lazy('room:select_subject', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        # ルームの作成
        room = form.save(commit=False)
        room.host = self.request.user
        room.save()

        messages.success(self.request, 'ルームを作成しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'ルームの作成に失敗しました。')
        return super().form_invalid(form)


class SelectSubjectView(LoginRequiredMixin, generic.FormView):
    template_name = 'select_subject.html'
    form_class = SubjectForm

    def get(self, request, **kwargs):
        if request.COOKIES.get('submit_records'):
            return HttpResponseRedirect(reverse_lazy('room:room_top'))
        return super().get(request, **kwargs)

    # 教科の選択肢を取得するためにSubjectFormにログインユーザーIDを渡す
    def get_form_kwargs(self):
        kwargs = super(SelectSubjectView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        self.request.session['subject'] = self.request.POST.get('subject')
        return reverse_lazy('room:room', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        # ルームメンバーの作成
        if not RoomMember.objects.filter(user=self.request.user).exists():
            RoomMember.objects.create(room=Room.objects.get(pk=self.kwargs['pk']), user=self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        self.request.session['subject'] = self.request.POST.get('subject')
        return reverse_lazy('room:room', kwargs={'pk': self.kwargs['pk']})


class RoomView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'room.html'

    def get(self, request, **kwargs):
        # 教科が選択されていない場合は教科選択画面に遷移
        if 'subject' not in self.request.session:
            return HttpResponseRedirect(reverse_lazy('room:select_subject', kwargs={'pk': self.kwargs['pk']}))
        return super().get(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subject_list'] = Subject.objects.filter(user=self.request.user, is_available=True)
        context['room'] = room = Room.objects.get(pk=self.kwargs['pk'])
        context['room_member'] = RoomMember.objects.filter(room=room)
        context['subject'] = Subject.objects.get(pk=self.request.session['subject'])
        return context

    def post(self, request, *args, **kwargs):
        # 学習記録の登録
        record_objects = []
        print(request.POST['records'])
        records = json.loads(request.POST['records'])
        for record in records:
            record_objects.append(
                StudyRecord(
                    user=self.request.user,
                    subject=Subject.objects.get(pk=int(record['subject'])),
                    studied_at=record['studied_at'],
                    minutes=int(record['microseconds'] / 1000 // 60),
                )
            )
        StudyRecord.objects.bulk_create(record_objects)

        # ルームメンバーの削除
        RoomMember.objects.filter(user=self.request.user).delete()

        messages.success(self.request, '退室しました。')
        return HttpResponseRedirect(reverse_lazy('room:room_top'))


class GetRoomMemberView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        data = {
            'room_member': serializers.serialize('json', RoomMember.objects.filter(room=kwargs['pk'])),
        }
        return JsonResponse(data)


class GetRoomMessageView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        data = {
            'room_message': serializers.serialize('json', RoomMessage.objects.filter(room=kwargs['pk'])),
        }
        return JsonResponse(data)
