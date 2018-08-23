from django.shortcuts import render

# Create your views here.
from .models import *
from django.db.models import Q
Book.objects.filter(Q(title="yuan")|Q(price=123))

q = Q()
q.connector = 'or'
q.children.append(('title','yuan'))
q.children.append(('price',123))