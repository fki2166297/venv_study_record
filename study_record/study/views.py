from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.db.models import Q
from .models import StudyRecord, Subject
from accounts.models import CustomUser, Connection
from .forms import StudyRecordForm, SubjectCreateForm
import datetime as dt
from .helpers import *


class HomeView(LoginRequiredMixin, generic.ListView):
    template_name = 'home.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = StudyRecord.objects.select_related().filter(user=self.request.user).order_by('-studied_at')
        for row in queryset:
            row.minutes = to_time_str(row.minutes)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        following = Connection.objects.filter(follower=self.request.user).values_list('following', flat=True)
        following_records = StudyRecord.objects.select_related().filter(user__in=following, publication='follow').order_by('-studied_at')
        for row in following_records:
            row.minutes = to_time_str(row.minutes)
        context['following_records'] = following_records

        return context


class StudyRecordCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'studyrecord_create.html'
    form_class = StudyRecordForm
    success_url = reverse_lazy('study:home')

    # 教科の選択肢を取得するためにStudyRecordFormにログインユーザーIDを渡す
    def get_form_kwargs(self):
        kwargs = super(StudyRecordCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    # StudyRecordモデルのuserフィールドにログインユーザーのIDを保存する
    def form_valid(self, form):
        studyrecord = form.save(commit=False)
        studyrecord.user = self.request.user
        studyrecord.save()

        messages.success(self.request, '記録を作成しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '記録の作成に失敗しました。')
        return super().form_invalid(form)


class StudyRecordUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'studyrecord_update.html'
    model = StudyRecord
    form_class = StudyRecordForm
    success_url = reverse_lazy('study:home')

    # 教科の選択肢を取得するためにStudyRecordFormにログインユーザーIDを渡す
    def get_form_kwargs(self):
        kwargs = super(StudyRecordUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['study_record_pk'] = self.kwargs['pk']
        return context

    def form_valid(self, form):
        messages.success(self.request, '記録を更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "記録の更新に失敗しました。")
        return super().form_invalid(form)


class StudyRecordDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = StudyRecord
    success_url = reverse_lazy('study:home')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '記録を削除しました。')
        return super().delete(request, *args, **kwargs)


class ReportView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        studyrecord = StudyRecord.objects.filter(user=self.request.user).order_by('studied_at').select_related()

        now = dt.datetime.now().astimezone()

        t_start, t_end = day_start_end(now)
        w_start, w_end = week_start_end(now)
        m_start, m_end = month_start_end(now)

        context['pie_chart'] = pie_chart_data(studyrecord)

        context['today_sum'] = to_time_str(minutes_sum(studyrecord, t_start, t_end))
        context['week_sum'] = to_time_str(minutes_sum(studyrecord, w_start, w_end))
        context['month_sum'] = to_time_str(minutes_sum(studyrecord, m_start, m_end))
        context['total'] = to_time_str(minutes_sum(studyrecord))

        return context


class GetBarChartDataWeek(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        now = dt.datetime.now().astimezone()
        w_start, w_end = week_start_end(now)

        # 1週間分のデータを取得する
        queryset = StudyRecord.objects.filter(user=request.user, studied_at__range=(w_start, w_end)).order_by('studied_at').select_related()

        # 横軸ラベルを作る
        labels = []
        for i in range(7):
            date = w_start + dt.timedelta(days=i)
            weekday = ('日', '月', '火', '水', '木', '金', '土')[i]
            date_str = f'{date.month}/{date.day} ({weekday})'
            labels.append(date_str)

        data = {
            'labels': labels,
            'datasets': barchart_datasets(queryset, w_start, w_end)
        }

        return JsonResponse(data)


class GetBarChartDataMonth(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        now = dt.datetime.now().astimezone()
        m_start, m_end = month_start_end(now)

        # 1か月分のデータを取得する
        studyrecord = StudyRecord.objects.filter(user=request.user, studied_at__range=(m_start, m_end)).order_by('studied_at').select_related()

        data = {
            'labels': [i + 1 for i in range((m_end - m_start).days + 1)],
            'datasets': barchart_datasets(studyrecord, m_start, m_end)
        }

        return JsonResponse(data)


class GetBarChartDataYear(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        now = dt.datetime.now().astimezone()
        y_start, y_end = year_start_end(now)

        # 1年分のデータを取得する
        queryset = StudyRecord.objects.filter(user=request.user, studied_at__range=(y_start, y_end)).order_by('studied_at').select_related()

        data = {
            'labels': ('1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'),
            'datasets': barchart_datasets_year(queryset, y_start, y_end)
        }

        return JsonResponse(data)


class SubjectView(LoginRequiredMixin, generic.ListView):
    template_name = 'subject.html'

    def get_queryset(self):
        queryset = Subject.objects.filter(user=self.request.user, is_available=True).order_by('created_at')
        return queryset


class SubjectCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'subject_create.html'
    form_class = SubjectCreateForm

    def get_success_url(self):
        via = self.request.GET.get('via')
        if via == 'studyrecord-create':
            return reverse_lazy('study:studyrecord_create')
        else:
            return reverse_lazy('study:subject')

    def form_valid(self, form):
        subject = form.save(commit=False)
        subject.user = self.request.user
        subject.save()

        messages.success(self.request, '教科を作成しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '教科の作成に失敗しました。')
        return super().form_invalid(form)


class SubjectUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'subject_update.html'
    model = Subject
    fields = ('name', 'color')
    success_url = reverse_lazy('study:subject')

    def form_valid(self, form):
        messages.success(self.request, '教科を更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '教科の更新に失敗しました。')
        return super().form_invalid(form)



class SubjectDeleteView(LoginRequiredMixin, generic.View):
    def post(self, request, *args, **kwargs):
        subject = Subject.objects.get(pk=kwargs['pk'])
        # StudyRecordのsubjectフィールドはSubjectモデルを外部キーに設定しているため、
        # Subjectのレコードを削除するのではなく、使用不可（is_availavle = False）に設定する
        subject.is_available = False
        subject.save()

        messages.success(request, '教科を削除しました。')
        return HttpResponseRedirect(reverse_lazy('study:subject'))


class AccountSearchView(LoginRequiredMixin, generic.ListView):
    template_name = 'accout_search.html'

    def get_queryset(self):
        queryset = CustomUser.objects.none()
        query = self.request.GET.get('query')
        if query:
            queryset = CustomUser.objects.filter(Q(username__icontains=query) | Q(introduce__icontains=query)).exclude(username=self.request.user.username)
        return queryset


class AccountDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'account_detail.html'
    model = CustomUser
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['account'] = CustomUser.objects.get(pk=self.kwargs['pk'])
        context['following'] = Connection.objects.filter(follower=self.kwargs['pk']).count()
        context['follower'] = Connection.objects.filter(following=self.kwargs['pk']).count()

        if self.kwargs['pk'] is not self.request.user:
            result = Connection.objects.filter(follower=self.request.user).filter(following=self.kwargs['pk'])
            context['connected'] = True if result else False

        return context


class AccountUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'account_update.html'
    model = CustomUser
    fields = ('username', 'introduce', 'icon')

    def get_success_url(self):
        return reverse_lazy('study:account_detail', kwargs={'pk': self.request.user.pk })

    def form_valid(self, form):
        account = form.save(commit=False)
        self.request.user.username = account.username

        messages.success(self.request, 'プロフィールを更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'プロフィールの更新に失敗しました。')
        return super().form_invalid(form)


class AccountFollowingView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'account_following.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['account'] = CustomUser.objects.get(pk=self.kwargs['pk'])
        context['connection_list'] = Connection.objects.select_related().filter(follower=self.kwargs['pk'])
        return context


class AccountFollowersView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'account_followers.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['account'] = CustomUser.objects.get(pk=self.kwargs['pk'])
        context['connection_list'] = Connection.objects.select_related().filter(following=self.kwargs['pk'])
        return context


class FollowView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        try:
            follower = CustomUser.objects.get(pk=request.user.pk)
            following = CustomUser.objects.get(pk=kwargs['pk'])
        except CustomUser.DoesNotExist:
            messages.warning(request, f'ユーザーが存在しません')
            return HttpResponseRedirect(reverse_lazy('study:home'))
        else:
            if follower.pk == following.pk:
                messages.warning(request, '自分自身はフォローできません')
            else:
                _, created = Connection.objects.get_or_create(follower=follower, following=following)
                if (created):
                    messages.success(request, f'{following.username}をフォローしました')
                else:
                    messages.warning(request, f'あなたはすでに{following.username}をフォローしています')
            return HttpResponseRedirect(reverse_lazy('study:account_detail', kwargs={'pk': following.pk}))


class UnfollowView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        try:
            follower = CustomUser.objects.get(pk=request.user.pk)
            following = CustomUser.objects.get(pk=kwargs['pk'])
            if follower.pk == following.pk:
                messages.warning(request, '自分自身のフォローは外すことができません')
            else:
                unfollow = Connection.objects.get(follower=follower, following=following)
                unfollow.delete()
                messages.success(request, f'あなたは{following.username}のフォローを解除しました')
        except CustomUser.DoesNotExist:
            messages.warning(request, f'ユーザーが存在しません')
            return HttpResponseRedirect(reverse_lazy('study:home'))
        else:
            return HttpResponseRedirect(reverse_lazy('study:account_detail', kwargs={'pk': following.pk}))
