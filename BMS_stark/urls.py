
from django.contrib import admin
from django.urls import path

from stark.service import stark
urlpatterns = [
    path('admin/', admin.site.urls),
    # path('stark/', ([],None,None)),
    path('stark/', stark.site.urls),
]
