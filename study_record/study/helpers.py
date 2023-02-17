from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import timedelta
import calendar
from dateutil.relativedelta import relativedelta
from django.db.models import Sum


# 分（数値）から〇時間〇分の文字列を返す
def to_time_str(minutes):
    if minutes == 0:
        return '0分'
    h, m = divmod(minutes, 60)
    return (f'{h}時間' if h else '') + (f'{m}分' if m else '')


def day_start_end(dt_val):
    start = dt_val.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1, microseconds=-1)
    return start, end

def week_start_end(dt_val):
    dt_val = dt_val.replace(hour=0, minute=0, second=0, microsecond=0)
    start = dt_val + timedelta(days=-(dt_val.weekday() + 1))
    end = start + timedelta(days=7, microseconds=-1)
    return start, end

def month_start_end(dt_val):
    dt_val = dt_val.replace(hour=0, minute=0, second=0, microsecond=0)
    start = dt_val + relativedelta(day=1)
    end = dt_val + relativedelta(months=+1, day=1) + timedelta(microseconds=-1)
    return start, end

def year_start_end(dt_val):
    dt_val = dt_val.replace(hour=0, minute=0, second=0, microsecond=0)
    start = dt_val + relativedelta(month=1, day=1)
    end = start + relativedelta(years=+1) + timedelta(microseconds=-1)
    return start, end


# start <= studied_at <= endのminutesの合計を求める
def minutes_sum(queryset, start=None, end=None):
    if start and end:
        sum = queryset.filter(studied_at__range=(start, end)).aggregate(Sum('minutes'))['minutes__sum']
    else:
        sum = queryset.aggregate(Sum('minutes'))['minutes__sum']
    return sum if sum else 0


def barchart_datasets(queryset, start, end):
    datasets = []

    DAYS = (end - start).days + 1

    # データに含まれる教科ID、教科名、教科の色をタプルのリストで取得する
    subject_list = queryset.select_related().values_list('subject', 'subject__name', 'subject__color').order_by('subject').distinct()

    for subject_id, subject_name, subject_color in subject_list:
        dataset = {
            'label': subject_name,
            'backgroundColor': subject_color,
            'data': [],
        }

        for i in range(DAYS):
            dt_val = start + timedelta(days=i)
            d_start, d_end = day_start_end(dt_val)

            # 教科、日付ごとの学習時間の合計をdataに追加する
            dataset['data'].append(
                minutes_sum(queryset.filter(subject=subject_id), d_start, d_end)
            )

        datasets.append(dataset)
    return datasets


def barchart_datasets_year(queryset, start, end):
    datasets = []

    # startからendまでのデータを取得する
    queryset = queryset.filter(studied_at__range=(start, end))

    # データに含まれる教科ID、教科名、教科の色をタプルのリストで取得する
    subject_list = queryset.select_related().values_list('subject', 'subject__name', 'subject__color').order_by('subject').distinct()

    for subject_id, subject_name, subject_color in subject_list:
        dataset = {
            'label': subject_name,
            'backgroundColor': subject_color,
            'data': [],
        }

        for i in range(12):
            dt_val = start + relativedelta(months=+i)
            m_start, m_end = month_start_end(dt_val)

            # 教科、日付ごとの学習時間の合計をdataに追加する
            dataset['data'].append(
                minutes_sum(queryset.filter(subject=subject_id), m_start, m_end)
            )

        datasets.append(dataset)
    return datasets


def pie_chart_data(queryset):
    data = {'labels': [], 'datasets': []}
    dataset = {'data': [], 'backgroundColor': []}
    results = queryset.select_related().values('subject__name', 'subject__color').annotate(sum=Sum('minutes')).order_by('sum').reverse()
    for result in results:
        data['labels'].append(result['subject__name'])
        dataset['data'].append(result['sum'])
        dataset['backgroundColor'].append(result['subject__color'])
    data['datasets'].append(dataset)
    return data
