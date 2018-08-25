## stark组件--(Xadmin)
（单例，继承，反射，面向对象，modelform 应用得很好！！）

###1.注册表
    单例模式 site = StarkSite()

###2.生成url
    url(r'^stark/', ([],None,None))

###3.数据列表展示
    可自定义配置显示：
    list_display = ["__str__"]
    list_display_links = []
    modelform_class = []
    search_fields = []
    actions = []
    list_filter = []

###4.增删改页面 modelform

###5.分页
    自定义分页组件 stark/utils/page.py
    class Pagination(object):
        ...
        ...

###6.search模糊查询
    Q查询 or
    search_connection = Q()
    ...
    data_list = self.model.objects.all().filter(search_connection)

###7.action批量处理
    def patch_init(self, request, queryset):
        queryset.update(price=123)
        ...
    patch_init.short_description = "批量初始化"

    actions = [patch_init]

    queryset = self.model.objects.filter(pk__in=selected_pk)

###8.filter过滤
    list_filter = ['title','publish', 'authors']
    eg:{"publish":["<a href=''>全部</a>","<a href=''>南京出版社</a>","<a href=''>上海出版社</a>"]
        "authors":["<a href=''>全部</a>"，"<a href=''>yuan</a>","<a href=''>egon</a>"]
        }

    Q查询 and
    filter_condition = Q()
    data_list = self.model.objects.all().filter(search_connection).filter(filter_condition)

###9.pop弹出
    在一对多和多对多字段后渲染 +
    +对应的跳转路径
    保存添加记录同时，将原页面的对应的下拉菜单中添加该记录