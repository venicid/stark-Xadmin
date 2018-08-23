# -*- coding: utf-8 -*-
# @Time    : 2018/08/17 0017 14:46
# @Author  : Venicid
from django.conf.urls import url
from django.shortcuts import HttpResponse,render,redirect

from django.utils.safestring import mark_safe
from django.urls import reverse

from stark.utils.page import Pagination
class ShowList(object):
    def __init__(self,config, data_list,request):
        self.config = config  # MOdelStark实例对象
        self.data_list = data_list      # 数据
        self.request =request

        # 分页
        data_count = self.data_list.count()
        current_page = int(self.request.GET.get('page',1))
        base_path = self.request.path
        self.pagination = Pagination(current_page,data_count,base_path,self.request.GET,per_page_num=10, pager_count=11,)

        # 分页后的数据
        self.page_data = self.data_list[self.pagination.start:self.pagination.end]

        # actions 批量初始化，字段
        # self.actions = self.config.actions # [patch_init]
        self.actions = self.config.new_actions() # [pathch_delete,patch_init,]
        # 构建数据[{'name':'path_init',"desc":'xxxxx'}]


    def get_action_list(self):
        """action批量初始化，构架数据"""
        temp = []
        for action in self.actions:
            temp.append(
                {'name':action.__name__,                # class的类名
                 "desc":action.short_description        # class的属性
                 }
            )
        return temp

    def get_header(self):
        # 构建表头
        header_list = []  # # header_list = ['选择'，'pk',...'操作','操作']
        for field in self.config.new_list_play():
            if callable(field):
                # header_list.append(field.__name__)
                val = field(self.config, header=True)
                header_list.append(val)
            else:
                if field == "__str__":
                    header_list.append(self.config.model._meta.model_name.upper())
                else:
                    val = self.config.model._meta.get_field(field).verbose_name    # 中文名称
                    header_list.append(val)

        return header_list

    def get_body(self):
        # 构建表单
        new_data_list = []
        for obj in self.page_data:    #分页后的数据               # Book表模型，Author表模型
            temp = []
            for field in self.config.new_list_play():     # ['name','age']
                if callable(field):                 # edit()  可调用的
                    print(obj,99999999999999999)
                    val = field(self.config,obj)           # 直接调用edit()函数
                    print('val--------->',val)
                else:
                    val = getattr(obj,field)       # 反射  obj是实例对象，name是方法

                    # list_display_links 按钮
                    if field in self.config.list_display_links:
                        model_name = self.config.model._meta.model_name
                        app_label = self.config.model._meta.app_label
                        _url = reverse("%s_%s_change" % (app_label, model_name), args=(obj.pk,))
                        # print(_url)
                        val = mark_safe("<a href='%s'>%s</a>"%(_url,field))

                temp.append(val)

            new_data_list.append(temp)

        print('new_data_list',new_data_list)        # 构造数据  [['jack', 44], ['mark', 33]]

        return new_data_list


class ModelStark(object):
    list_display = ["__str__"]  # 子类中没有，直接用父类自己的
    list_display_links = []
    modelform_class = []
    search_fields = []  # 模糊查询字段
    actions = []

    # 批量删除
    def patch_delete(self,request,queryset):
        queryset.delete()

    patch_delete.short_description = "Delete selected "


    def __init__(self,model, site):
        self.model = model
        self.site = site

    # 增删改查url
    def get_add_url(self):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        _url = reverse("%s_%s_add" %(app_label,model_name))
        return _url

    def get_list_url(self):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        _url = reverse("%s_%s_list" %(app_label,model_name))
        return _url


    # 复选框，编辑，删除
    def checkbox(self,obj=None, header=False):
        if header:
            return mark_safe("<input id='choice' type='checkbox'>")
        return mark_safe("<input class='choice_item' type='checkbox' name='selected_pk' value='%s'>"%obj.pk)


    def edit(self,obj=None, header=False):
        if header:
            return "操作"
        # 方案1：固定url
        # return mark_safe("<a href=/stark/app01/userinfo/%s/change>编辑</a>")
        # 方案2：拼接url
        # return mark_safe("<a href='%s/change'>编辑</a>")

        # 方案3：反向解析
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        _url = reverse("%s_%s_change"%(app_label,model_name),args=(obj.pk,))
        # print("_url",_url)
        return mark_safe("<a href='%s'>编辑</a>"%_url)


    def deletes(self,obj=None, header=False):
        if header:
            return "操作"
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        _url = reverse("%s_%s_delete"%(app_label,model_name),args=(obj.pk,))
        return mark_safe("<a href='%s'>删除</a>"%_url)



    # ModelForm组件渲染  list、增、删、改页面
    def get_modelform_class(self):
        """ModelForm组件"""
        if not self.modelform_class:
            from django.forms import ModelForm
            class ModelFormDemo(ModelForm):
                class Meta:
                    model = self.model
                    fields = "__all__"
            return ModelFormDemo
        else:
            return self.modelform_class

    def new_list_play(self):
        """构建 ['checkbox','pk', 'name', 'age', edit,'delete']"""
        temp = []
        temp.append(ModelStark.checkbox)
        temp.extend(self.list_display)
        if not self.list_display_links:
            temp.append(ModelStark.edit)
        temp.append(ModelStark.deletes)
        return temp

    # action = ['delete',...]
    def new_actions(self):
        temp = []
        temp.append(ModelStark.patch_delete)        # delete添加
        temp.extend(self.actions)   # 如果定义新的，就扩展到temp中
        return temp

    '''
    def list_view(self,request):
        ret1 = self.model.objects.filter(title__startswith='py')
        ret2 = self.model.objects.filter(price__in=[11,22,33,44,55])
        ret3 = self.model.objects.filter(price__range=[10,20])
        ret4 = self.model.objects.filter(title__contains='O')
        ret5 = self.model.objects.filter(title__icontains='O')
        return HttpResponse("过滤成功")
    '''

    def get_search_condition(self,request):
        """search模糊查询"""
        key_word = request.GET.get("q",'')
        self.key_word = key_word
        from django.db.models import Q   # 与或非
        search_connection = Q()
        if key_word:
            search_connection.connector = "or"
            for search_field in self.search_fields:
                search_connection.children.append((search_field+"__contains", key_word))

        return search_connection

    def list_view(self, request):
        if request.method == 'POST':
            print('post',request.POST)
            action = request.POST.get("action")                     # action': ['patch_init'],
            if action:
                selected_pk = request.POST.getlist('selected_pk')       # 'selected_pk': ['5']}>
                action_func = getattr(self,action)  # 反射查询 action       # 取出实例方法

                queryset = self.model.objects.filter(pk__in=selected_pk)        # 查询
                ret = action_func(request,queryset)    # 执行action()     # 执行实例方法()
                # return ret


        # 获取search的Q对象
        search_connection = self.get_search_condition(request)

        # 筛选获取当前表所有数据
        data_list = self.model.objects.all().filter(search_connection)

        #按照showlist展示页面， 构建表头，表单
        show_list = ShowList(self,data_list,request)  # self=ModelSTark实例对象

        # 构建一个查看addurl
        add_url = self.get_add_url()
        return render(request,'list_view.html', locals())


    def add_view(self, request):
        ModelFormDemo=self.get_modelform_class()
        form = ModelFormDemo()
        if request.method == "POST":
            form = ModelFormDemo(request.POST)
            if form.is_valid():
                form.save()
                return redirect(self.get_list_url())

        return render(request, "add_view.html",locals())

    def delete_view(self, request, id):
        url = self.get_list_url()
        if request.method == "POST":
            self.model.objects.filter(pk=id).delete()
            return redirect(url)
        return render(request, "delete_view.html", locals())

    def change_view(self, request, id):
        edit_obj = self.model.objects.filter(pk=id).first()

        ModelFormDemo=self.get_modelform_class()
        form = ModelFormDemo(instance=edit_obj)
        if request.method == "POST":
            form = ModelFormDemo(request.POST,instance=edit_obj)
            if form.is_valid():
                form.save()
                return redirect(self.get_list_url())

        return render(request, "change_view.html",locals())


    #构造 add/delete/change
    def get_urls2(self):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        temp = []
        temp.append(url(r'^$', self.list_view, name='%s_%s_list'%(app_label,model_name)))
        temp.append(url(r'^add/', self.add_view, name='%s_%s_add'%(app_label,model_name)))
        temp.append(url(r'^(\d+)/delete/', self.delete_view, name='%s_%s_delete'%(app_label,model_name)))
        temp.append(url(r'^(\d+)/change/', self.change_view, name='%s_%s_change'%(app_label,model_name)))

        return temp

    @property
    def urls2(self):

        return self.get_urls2(), None, None


class StarkSite(object):
    """site单例类"""
    def __init__(self):
        self._registry = {}

    def register(self,model, stark_class=None):
        """注册"""
        if not stark_class:
            stark_class = ModelStark

        self._registry[model] = stark_class(model,self)

    def get_urls(self):
        """构造一层urls app01/book"""
        temp = []
        for model, stark_class_obj in self._registry.items():
            print(model, 'stark_clas_obj', stark_class_obj)  # 不同的model模型表
            """
             <class 'app01.models.UserInfo'> ----> <app01.starkadmin.UserConfig object at 0x00000072DDB65198>
             <class 'app01.models.Book'> ----> <stark.service.stark.ModelStark object at 0x00000072DDB65240>
             """

            app_label = model._meta.app_label     # app01
            model_name = model._meta.model_name   # book
            # temp.append(url(r'^%s/%s'%(app_label, model_name),([],None,None)))
            temp.append(url(r'^%s/%s/'%(app_label, model_name),stark_class_obj.urls2))
            """
               path('app01/userinfo/',UserConfig(Userinfo,site).urls2),
               path('app01/book/',ModelStark(Book,site).urls2),
            """


        return temp

    @property
    def urls(self):

        # return [],None,None
        return self.get_urls(),None,None

site = StarkSite()   # 单例对象