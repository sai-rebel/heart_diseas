import matplotlib.pyplot as plt
import os
from django.conf import settings
from django.shortcuts import render
import matplotlib
matplotlib.use('Agg')

def index(request):
    return render(request, 'index.html')

def AdminLogin(request):
    print("ADMIN LOGIN PAGE LOADED")
    return render(request, 'AdminLogin.html')

def UserLogin(request):
    return render(request, 'UserLogin.html')

def UserRegistrations(request):
    return render(request, 'UserRegistrations.html')
def train_model(request):
    # sample graph
    x = [1,2,3,4]
    y = [10,20,25,30]

    plt.figure()
    plt.plot(x, y)

    graph_path = os.path.join(settings.MEDIA_ROOT, 'graph.png')
    plt.savefig(graph_path)
    plt.close()

    return render(request, 'result.html', {
        'graph_url': settings.MEDIA_URL + 'graph.png'
    })