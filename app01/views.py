from django.shortcuts import render

# Create your views here.
from .models import *
from django.db.models import Q
Book.objects.filter(Q(title="yuan")|Q(price=123))

q = Q()
q.connector = 'or'
q.children.append(('title','yuan'))
q.children.append(('price',123))



def index(request):

    return render(request,'index.html')


def add(request):
    if request.method == "POST":
        tel = request.POST.get('tel')
        addr = request.POST.get('addr')
        AuthorDetail.objects.create(birthday='2012-12-12',telephone=tel,addr=addr)

        return render(request,"pop.html",locals())

    return render(request,'add.html')