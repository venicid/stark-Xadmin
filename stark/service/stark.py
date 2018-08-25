# -*- coding: utf-8 -*-
# @Time    : 2018/08/17 0017 14:46
# @Author  : Venicid
from django.conf.urls import url
from django.shortcuts import HttpResponse,render,redirect

from django.utils.safestring import mark_safe
from django.urls import reverse
from django.db.models import Q  # 与或非
from django.db.models.fields.related import ForeignKey
from django.db.models.fields.related import ManyToManyField
import copy

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

    # filter的tag如何生成的
    def get_filter_linktags(self):
        link_dic = {}
        for filter_field in self.config.list_filter:        # ['title','publish','authors']
            # 1.获取url中的相关字段，后面比较
            current_id = self.request.GET.get(filter_field,0)
            pararms = copy.deepcopy(self.request.GET)

            # 2 页面生成  各种字段
            filter_field_obj = self.config.model._meta.get_field(filter_field)
            print(filter_field_obj,type(filter_field_obj))
            # app01.Book.publish  < class 'django.db.models.fields.related.ForeignKey'>
            # app01.Book.authors < class 'django.db.models.fields.related.ManyToManyField'>

            # print('rel...',filter_field_obj.re)     # <ManyToOneRel: app01.book>
            # print('rel...',filter_field_obj.re.to.objects.all())  # <QuerySet [<Publish: 南京出版社>, <Publish: 北京出版社>]>

            # 解决步骤
            # print('rel...',filter_field_obj.__dict__)
            # print('rel...',filter_field_obj.remote_field)
            # print('rel...',filter_field_obj.remote_field.__dict__)
            # print("rel...", filter_field_obj.remote_field.model.objects.all())
            # <QuerySet [<Publish: 南京出版社>, <Publish: 北京出版社>]>
            # <QuerySet [<Author: jack>, <Author: tom>]>

            # 一对一字段or一对多字段
            if isinstance(filter_field_obj,ForeignKey) or isinstance(filter_field_obj,ManyToManyField):
                data_list = filter_field_obj.remote_field.model.objects.all()
            else:
                # 普通字段
                data_list = self.config.model.objects.all().values('pk',filter_field)

            # 3、 生成标签的href
            temp = []
            if pararms.get(filter_field):
                del pararms[filter_field]
                temp.append("<a href='?%s'>全部</a>"%pararms.urlencode())
            else:
                temp.append("<a href='#' class='active'>全部</a>")

            # 处理filter字段的href
            for obj in data_list:
                # print(data_list)
                # 一对一，一对多字段
                if isinstance(filter_field_obj, ForeignKey) or isinstance(filter_field_obj, ManyToManyField):
                    pk = obj.pk
                    text = str(obj)
                    pararms[filter_field] = pk
                else:
                    # 普通字段
                    pk = obj.get('pk')
                    text = obj.get(filter_field)
                    pararms[filter_field] = text

                _url = pararms.urlencode()
                # print(type(current_id),type(pk),type(text))
                if str(current_id) == str(pk) or str(current_id) ==str(text):
                    link_tag = "<a href='?%s' class='active'>%s</a>"%(_url,text)
                else:
                    link_tag = "<a href='?%s'>%s</a>"%(_url,text)
                temp.append(link_tag)
            link_dic[filter_field] = temp

        return link_dic

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
            for field in self.config.new_list_play():     #  ["__str__"]  ['name','age']
                if callable(field):                 # edit()  可调用的
                    val = field(self.config,obj)           # 直接调用edit()函数
                else:
                    try:
                        field_obj = self.config.model._meta.get_field(field)
                        if isinstance(field_obj,ManyToManyField):
                            ret = getattr(obj,field).all()       # 反射  obj是实例对象，name是方法
                            t = []
                            for obj in ret:
                                t.append(str(obj))
                            val = ','.join(t)

                        else:
                            val = getattr(obj, field)
                            # list_display_links 按钮
                            if field in self.config.list_display_links:
                                _url = self.config.get_change_url(self,obj)
                                val = mark_safe("<a href='%s'>%s</a>"%(_url,val))

                    # __str__ 的步骤
                    except  Exception as e:
                        val = getattr(obj,field)                #  <bound method Book.__str__ of <Book: php>
                        _url = self.config.get_change_url(obj)   # /app01/book/3/change/
                        val = mark_safe("<a href='%s'> %s </a>" % (_url, val()))

                temp.append(val)

            new_data_list.append(temp)

        # print('new_data_list',new_data_list)        # 构造数据  [['jack', 44], ['mark', 33]]

        return new_data_list


class ModelStark(object):
    list_display = ['__str__',]  # 子类中没有，直接用父类自己的
    list_display_links = []
    modelform_class = []
    search_fields = []  # 模糊查询字段
    actions = []
    list_filter = []        # 过滤字段


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

    def get_change_url(self,obj):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        _url = reverse("%s_%s_change" %(app_label,model_name),args=(obj.pk,))
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

        search_connection = Q()
        if key_word:
            search_connection.connector = "or"
            for search_field in self.search_fields:
                search_connection.children.append((search_field+"__contains", key_word))

        return search_connection


    def get_filter_condition(self,request):
        """filter过滤处理"""
        filter_condition = Q()      # 并且
        for filter_field,val in request.GET.items():
            if filter_field in self.list_filter:        # list_filter = ['publish','authors']
                filter_condition.children.append((filter_field,val))
        return filter_condition


    def list_view(self, request):
        if request.method == 'POST':
            # print('post',request.POST)
            action = request.POST.get("action")                     # action': ['patch_init'],
            if action:
                selected_pk = request.POST.getlist('selected_pk')       # 'selected_pk': ['5']}>
                action_func = getattr(self,action)  # 反射查询 action       # 取出实例方法

                queryset = self.model.objects.filter(pk__in=selected_pk)        # 查询
                ret = action_func(request,queryset)    # 执行action()     # 执行实例方法()
                # return ret

        # 获取search的Q对象
        search_connection = self.get_search_condition(request)

        # 获取filter构建Q对象
        filter_condition = self.get_filter_condition(request)

        # 筛选获取当前表所有数据
        # data_list = self.model.objects.all().filter(search_connection)
        data_list = self.model.objects.all().filter(search_connection).filter(filter_condition)

        #按照showlist展示页面， 构建表头，表单
        show_list = ShowList(self,data_list,request)  # self=ModelSTark实例对象

        # 构建一个查看addurl
        add_url = self.get_add_url()
        return render(request,'list_view.html', locals())

    def add_view(self, request):
        ModelFormDemo=self.get_modelform_class()
        form = ModelFormDemo()

        # 打印form的每个字段
        from django.forms.boundfield import BoundField
        from django.forms.models import ModelChoiceField
        from django.forms.models import ModelMultipleChoiceField

        for bfield in form:
            # print(type(bfield))  # <class 'django.forms.boundfield.BoundField'>
            # print('field',bfield.field)   # <django.forms.models.ModelChoiceField object at 0x000000F2C0DEDC50>
            # print('name',bfield.name)    # publish

            if isinstance(bfield.field,ModelChoiceField):
                bfield.is_pop = True
                # print(bfield.field.queryset.model)     # 一对多或多对多字段的关联模型
                # <class 'app01.models.Publish'>  <class 'app01.models.Author'>

                # print(bfield.field.queryset.model._meta)  # app01.author
                related_app_name = bfield.field.queryset.model._meta.app_label  # app01
                related_model_name = bfield.field.queryset.model._meta.model_name # author

                _url = reverse("%s_%s_add"%(related_app_name,related_model_name))
                bfield.url = _url+"?pop_res_id=id_%s"%bfield.name

        if request.method == "POST":
            form = ModelFormDemo(request.POST)
            if form.is_valid():
                obj = form.save()

                # window.open添加页面 要返回的数据
                pop_res_id = request.GET.get('pop_res_id')
                if pop_res_id:
                    res = {"pk":obj.pk,'text':str(obj),'pop_res_id':pop_res_id}
                    return render(request,'pop_view.html',locals())
                else:
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
            # print(model, 'stark_clas_obj', stark_class_obj)  # 不同的model模型表
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