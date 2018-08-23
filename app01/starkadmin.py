from django.shortcuts import HttpResponse
from stark.service import stark
from .models import *
from django.forms import ModelForm

class AuthorConfig(stark.ModelStark):
    list_display = ['nid', 'name', 'age']
    list_display_links = ['name','age']


class BookModelForm(ModelForm):
    class Meta:
        model = Book
        fields = "__all__"

        labels = {
            "authors":"作者",
            "publishDate":"出版日期",
        }

class BookConfig(stark.ModelStark):
    list_display = ['nid', 'title', 'price']
    modelform_class = BookModelForm
    search_fields = ['title','price']


    # 批量修改数据
    def patch_init(self,request,queryset):
        queryset.update(price=111)

        # return HttpResponse("批量初始化OK")

    patch_init.short_description = "批量初始化"

    actions = [patch_init]


stark.site.register(Book,BookConfig)
stark.site.register(Publish)
stark.site.register(Author,AuthorConfig)
stark.site.register(AuthorDetail)

print(stark.site._registry)

"""
{<class 'app01.models.Book'>: <stark.service.stark.ModelStark object at 0x0000003AA7439630>,
<class 'app01.models.Publish'>: <stark.service.stark.ModelStark object at 0x0000003AA7439668>,
<class 'app01.models.Author'>: <stark.service.stark.ModelStark object at 0x0000003AA74396A0>,
<class 'app01.models.AuthorDetail'>: <stark.service.stark.ModelStark object at 0x0000003AA7439940>}
"""