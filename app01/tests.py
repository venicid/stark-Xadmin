from django.test import TestCase

# Create your tests here.
from.models import *

from django.db import models

class Book(models.Model):
    title = models.CharField(verbose_name='名称', max_length=32)
    price = models.DecimalField(verbose_name='价格', max_digits=5,decimal_places=2)

    publish = models.ForeignKey("Publish")
    authors = models.ManyToManyField("Author")



from django import forms
class BookForm(forms.Form):
    title = forms.CharField(max_length=32)
    price = forms.IntegerField()

    publish = forms.ModelChoiceField("Publish")
    authors = forms.MultipleChoiceField("Author")


"""
ChoiceField
ModelChoiuceFiled ---- select(单选)
MultipleChoiceField ---- select(多选)
"""