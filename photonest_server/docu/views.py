from django.shortcuts import render
from django.utils.timezone import now

def home(request):
    return render(request, 'docu/base.html', {
        'timestamp': now().timestamp(),
    })