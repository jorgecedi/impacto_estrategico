# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import CsvForm

import csv
import time

# Create your views here.

STATUS_CHOICES = {
    "1": "UP",
    "2": "DOWN",
}

DATE_PATTERN = "%d/%m/%Y %H:%M:%S"

def impport_from_csv(request):
    if request.method == 'POST':
        form = CsvForm(request.POST, request.FILES)
        if form.is_valid():
            reader = csv.reader(request.FILES['csv_file'])
            info = []

            start_date = time.mktime(
                time.strptime(
                    request.POST['start_date'], DATE_PATTERN)
            ) if request.POST['start_date'] else None

            end_date = time.mktime(
                time.strptime(
                    request.POST['end_date'], DATE_PATTERN)
            ) if request.POST['end_date'] else None

            status = request.POST['status']
            url = request.POST['url']
            for row in reader:
                ts = float(row[0])
                row[0] = time.strftime(DATE_PATTERN, time.localtime(ts))
                if url and url != row[2]:
                    continue
                if start_date and start_date > ts:
                    continue

                if end_date and end_date < ts:
                    continue

                if status != "0":
                    if row[1] == STATUS_CHOICES[status]:
                        info.append(row)
                else:
                    info.append(row)
            return render(request, 'tabla.html',{
                'info': info,
            })
    else:
        form = CsvForm()

    return render(request, 'csv_form.html',{
        'form': form,
    })

def index(request):
    return redirect('import_from_csv')

def download_csv_from_monitor(request):
    file_path = "datos-recopilados.csv"
    with open(file_path, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="application/force-download")
        response['Content-Disposition'] = 'inline; filename=datos-recopilados.csv'
        return response
    raise Http404
