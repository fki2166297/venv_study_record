from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views import generic
from django.db.models import Prefetch, Q
from .models import Question, Answer, Comment
from .forms import QuestionCreateForm, AnswerCreateForm
import datetime as dt


class QuestionAndAnswerView(LoginRequiredMixin, generic.ListView):
    template_name = 'qa.html'
    paginate_by = 30

    def get_queryset(self):
        query = self.request.GET.get('query')
        tab = self.request.GET.get('tab')
        sort = self.request.GET.get('sort')

        queryset = Question.objects.order_by('-created_at')
        if query:
            queryset = queryset.filter(Q(text__icontains=query) | Q(title__icontains=query))

        if tab == 'resolved':
            queryset = queryset.filter(is_resolved=True)
        elif tab == 'unresolved':
            queryset = queryset.filter(is_resolved=False)

        if sort == 'old':
            queryset = queryset.order_by('created_at')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('query')
        context['tab'] = self.request.GET.get('tab') or 'all'
        context['sort'] = self.request.GET.get('sort') or 'new'
        return context


class QuestionDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'question_detail.html'
    model = Question

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        answer_list = Answer.objects.select_related('user').prefetch_related(
            Prefetch(
                'comments',
                queryset=Comment.objects.select_related('user').order_by('created_at')
            )
        ).filter(question=self.kwargs['pk']).order_by('-created_at').order_by('-self_resolution').order_by('-is_best')

        is_user_answered = answer_list.filter(user=self.request.user).exists()
        context['answer_list'] = answer_list
        context['answer_count'] = answer_list.count()
        context['is_user_answered'] = is_user_answered
        return context


class CommentCreateView(LoginRequiredMixin, generic.View):
    def post(self, request, *args, **kwargs):
        comment = Comment.objects.create(
            user=request.user,
            text=request.POST['text'],
            answer=Answer.objects.get(pk=kwargs['a_pk'])
        )
        comment.save()
        messages.success(request, '????????????????????????????????????')
        return HttpResponseRedirect(reverse_lazy('qa:question_detail', kwargs={'pk': kwargs['pk']}))


class QuestionCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'question_create.html'
    form_class = QuestionCreateForm
    success_url = reverse_lazy('qa:qa')

    def form_valid(self, form):
        question = form.save(commit=False)
        # ???????????????????????????ID?????????
        question.user = self.request.user
        # ????????????????????????????????????
        deadline = dt.datetime.now().astimezone().replace(hour=0, minute=0, second=0, microsecond=0) + dt.timedelta(days=8)
        question.deadline = deadline
        question.save()

        messages.success(self.request, '??????????????????????????????')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '???????????????????????????????????????')
        return super().form_invalid(form)


class AddSupplementView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'add_supplement.html'
    model = Question
    fields = ('supplement', )

    def get_success_url(self):
        return reverse_lazy('qa:question_detail', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question'] = Question.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        messages.success(self.request, '????????????????????????????????????')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '?????????????????????????????????????????????')
        return super().form_invalid(form)


class QuestionDeleteView(LoginRequiredMixin, generic.View):
    def post(self, request, *args, **kwargs):
        question = Question.objects.get(pk=kwargs['pk'])
        question.delete()
        messages.success(request, '??????????????????????????????')
        return HttpResponseRedirect(reverse_lazy('qa:qa'))


class AnswerCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'answer_create.html'
    form_class = AnswerCreateForm

    def get_success_url(self):
        return reverse_lazy('qa:question_detail', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question'] = Question.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        answer = form.save(commit=False)
        question = Question.objects.get(pk=self.kwargs['pk'])

        answer.user = self.request.user
        answer.question = Question.objects.get(pk=self.kwargs['pk'])
        answer.save()

        messages.success(self.request, '??????????????????????????????')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '???????????????????????????????????????')
        return super().form_invalid(form)


class SelfResolutionView(LoginRequiredMixin, generic.CreateView):
    template_name = 'self_resolution.html'
    form_class = AnswerCreateForm

    def get_success_url(self):
        return reverse_lazy('qa:question_detail', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question'] = Question.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        answer = form.save(commit=False)
        question = Question.objects.get(pk=self.kwargs['pk'])

        answer.user = self.request.user
        answer.question = question
        answer.self_resolution = True
        answer.save()

        question.is_resolved = True
        question.save()

        messages.success(self.request, '?????????????????????????????????????????????')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '?????????????????????????????????????????????')
        return super().form_invalid(form)


class SetBestAnswerView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'set_best_answer.html'

    def post(self, request, *args, **kwargs):
        answer = Answer.objects.get(pk=kwargs['a_pk'])
        answer.is_best = True
        answer.save()

        question = Question.objects.get(pk=kwargs['pk'])
        question.is_resolved = True
        question.save()

        messages.success(request, '?????????????????????????????????????????????')
        return HttpResponseRedirect(reverse_lazy('qa:question_detail', kwargs={'pk': kwargs['pk']}))
