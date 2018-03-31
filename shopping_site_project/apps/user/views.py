import re
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View
from django.conf import settings
from django.http import HttpResponse

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django_redis import get_redis_connection
from user.models import User, Address
from goods.models import GoodsSKU
from order.models import OrderInfo, OrderGoods
# Create your views here.


# /user/register
def register_1(request):
    """显示注册页面"""
    return render(request, 'register.html')

# 在项目开发中视图处理一般流程
# 1.接收参数
# 2.参数校验(后端校验)
# 3.业务处理
# 4.返回应答


# /user/register_handle
def register_handle(request):
    """注册处理"""
    # 1.接收参数
    username = request.POST.get('user_name') # None
    password = request.POST.get('pwd')
    email = request.POST.get('email')

    # 2.参数校验(后端校验)
    # 校验数据的完整性
    if not all([username, password, email]):
        return render(request, 'register.html', {'errmsg': '数据不完整'})

    # 校验邮箱格式
    if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
        return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

    # 校验用户名是否已注册
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None

    if user is not None:
        return render(request, 'register.html', {'errmsg': '用户名已注册'})

    # 校验邮箱是否被注册...

    # 3.业务处理：注册
    user = User.objects.create_user(username, email, password)
    user.is_active = 0
    user.save()

    # 4.返回应答: 跳转到首页
    return redirect(reverse('goods:index'))


# /user/register
# get: 显示注册页面
# post: 进行注册处理
# request.method -> GET POST
def register(request):
    """注册"""
    if request.method == 'GET':
        # 显示注册页面
        return render(request, 'register.html')
    else:
        # 进行注册处理
        # 1.接收参数
        username = request.POST.get('user_name')  # None
        password = request.POST.get('pwd')
        email = request.POST.get('email')

        # 2.参数校验(后端校验)
        # 校验数据的完整性
        if not all([username, password, email]):
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 校验邮箱格式
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        # 校验用户名是否已注册
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user is not None:
            return render(request, 'register.html', {'errmsg': '用户名已注册'})

        # 校验邮箱是否被注册...

        # 3.业务处理：注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        # 4.返回应答: 跳转到首页
        return redirect(reverse('goods:index'))


# /user/register
class RegisterView(View):
    """注册"""
    def get(self, request):
        """显示"""
        print('----get----')
        return render(request, 'register.html')

    def post(self, request):
        """注册处理"""
        print('----post----')
        # 1.接收参数
        username = request.POST.get('user_name')  # None
        password = request.POST.get('pwd')
        email = request.POST.get('email')

        # 2.参数校验(后端校验)
        # 校验数据的完整性
        if not all([username, password, email]):
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 校验邮箱格式
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        # 校验用户名是否已注册
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user is not None:
            return render(request, 'register.html', {'errmsg': '用户名已注册'})

        # 校验邮箱是否被注册...

        # 3.业务处理：注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        # 注册之后，需要给用户的注册邮箱发送激活邮件，在激活邮件中需要包含激活链接
        # 激活链接: /user/active/用户id
        # 存在问题: 其他用户恶意请求网站进行用户激活操作
        # 解决问题: 对用户的信息进行加密，把加密后的信息放在激活链接中，激活的时候在进行解密
        # /user/active/加密后token信息

        # 对用户的身份信息进行加密，生成激活token信息
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        # 返回bytes类型
        token = serializer.dumps(info)
        # str
        token = token.decode()

        # 组织邮件信息
        # subject = '天天生鲜欢迎信息'
        # message = ''
        # sender = settings.EMAIL_FROM
        # receiver = [email]
        # html_message = """
        #     <h1>%s, 欢迎您成为天天生鲜注册会员</h1>
        #     请点击一下链接激活您的账号(1小时之内有效)<br/>
        #     <a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>
        # """ % (username, token, token)

        # 发送激活邮件
        # send_mail(subject='邮件标题',
        #           message='邮件正文',
        #           from_email='发件人',
        #           recipient_list='收件人列表')
        # 模拟send_mail发送邮件时间
        # import time
        # time.sleep(5)
        # send_mail(subject, message, sender, receiver, html_message=html_message)

        # 使用celery发出发送邮件任务
        from celery_tasks.tasks import send_register_active_email
        send_register_active_email.delay(email, username, token)

        # 4.返回应答: 跳转到首页
        return redirect(reverse('goods:index'))


# /user/active/加密token
class ActiveView(View):
    """激活"""
    def get(self, request, token):
        """激活"""
        print('---active---')
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            # 解密
            info = serializer.loads(token)
            # 获取待激活用户id
            user_id = info['confirm']
            # 激活用户
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            # 跳转登录页面
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            # 激活链接已失效
            # 实际开发: 返回页面，让你点击链接再发激活邮件
            return HttpResponse('激活链接已失效')


# /user/login
class LoginView(View):
    """登录"""
    def get(self, request):
        """显示"""
        # 判断用户是否记住用户名
        username = request.COOKIES.get('username')

        checked = 'checked'
        if username is None:
            # 没有记住用户名
            username = ''
            checked = ''

        # 使用模板
        return render(request, 'login.html', {'username': username, 'checked': checked})

    def post(self, request):
        """登录校验"""
        # 1.接收参数
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        remember = request.POST.get('remember') # None

        # 2.参数校验(后端校验)
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '参数不完整'})

        # 3.业务处理：登录校验
        user = authenticate(username=username, password=password)
        if user is not None:
            # 用户名和密码正确
            if user.is_active:
                # 用户已激活
                # 记住用户的登录状态
                login(request, user)

                # 获取用户登录之前访问的url地址，默认跳转到首页
                next_url = request.GET.get('next', reverse('goods:index')) # None
                print(next_url)

                # 跳转到next_url
                response = redirect(next_url)  # HttpResponseRedirect

                # 判断是否需要记住用户名
                if remember == 'on':
                    # 设置cookie username
                    response.set_cookie('username', username, max_age=7*24*3600)
                else:
                    # 删除cookie username
                    response.delete_cookie('username')

                # 跳转到首页
                return response
            else:
                # 用户未激活
                return render(request, 'login.html', {'errmsg': '用户未激活'})
        else:
            # 用户名或密码错误
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})


# request对象有一个属性user, request.user
# 如果用户已登录，request.user是一个认证用户模型类(User)的对象，包含登录用户的信息
# 如果用户未登录，request.user是一个匿名用户类(AnonymousUser)的对象

# is_authenticated
# User类这个方法永远返回的是True
# AnonymousUser类这个方法永远返回的是False

# 在模板文件中可以直接使用一个模板变量user，实际上就是request.user


# /user/logout
class LogoutView(View):
    """退出"""
    def get(self, request):
        """退出"""
        # 清除用户登录状态
        logout(request)

        # 跳转到登录
        return redirect(reverse('user:login'))

# django-redis

# login_required

from django.contrib.auth.decorators import login_required
from utils.mixin import LoginRequiredView, LoginRequiredMixin


# /user/
# class UserInfoView(View):
# class UserInfoView(LoginRequiredView):
class UserInfoView(LoginRequiredMixin, View):
    """用户中心-信息页"""
    def get(self, request):
        """显示"""
        # 获取登录用户
        user = request.user

        # 获取用户的默认收货地址
        address = Address.objects.get_default_address(user)

        # 获取用户的最近浏览商品的信息
        # from redis import StrictRedis
        # conn = StrictRedis(host='172.16.179.142', port=6379, db=5)

        # 返回StrictRedis类的对象
        conn = get_redis_connection('default')
        # 拼接key
        history_key = 'history_%d' % user.id

        # lrange(key, start, stop) 返回是列表
        # 获取用户最新浏览的5个商品的id
        sku_ids = conn.lrange(history_key, 0, 4) # [1, 3, 5, 2]

        skus = []
        for sku_id in sku_ids:
            # 根据商品的id查询商品的信息
            sku = GoodsSKU.objects.get(id=sku_id)
            # 追加到skus列表中
            skus.append(sku)

        # 组织模板上下文
        context = {
            'address': address,
            'skus': skus,
            'page': 'user'
        }

        # 使用模板
        return render(request, 'user_center_info.html', context)


# /user/order/页码
# class UserOrderView(View):
# class UserOrderView(LoginRequiredView):
class UserOrderView(LoginRequiredMixin, View):
    """用户中心-订单页"""
    def get(self, request, page):
        """显示"""
        # 获取登录用户
        user = request.user
        # 获取用户的所有订单信息
        orders = OrderInfo.objects.filter(user=user).order_by('-create_time')

        # 遍历获取每个订单对应的订单商品的信息
        for order in orders:
            # 获取订单商品的信息
            order_skus = OrderGoods.objects.filter(order=order)

            # 遍历order_skus计算订单中每件商品的小计
            for order_sku in order_skus:
                # 计算订单商品的小计
                amount = order_sku.price * order_sku.count

                # 给order_sku增加属性amount, 保存订单中每个商品的小计
                order_sku.amount = amount

            # 获取订单状态名称和计算订单实付款
            order.status_title = OrderInfo.ORDER_STATUS[order.order_status]
            order.total_pay = order.total_price + order.transit_price

            # 给order对象增加属性order_skus，包含订单中订单商品的信息
            order.order_skus = order_skus

        # 分页
        from django.core.paginator import Paginator
        paginator = Paginator(orders, 1)

        # 处理页码
        page = int(page)

        if page > paginator.num_pages:
            page = 1

        # 获取第page页的内容
        order_page = paginator.page(page)

        # 处理页码列表
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(num_pages - 2, num_pages + 3)

        # 组织上下文
        context = {
            'order_page': order_page,
            'pages': pages,
            'page': 'order'
        }

        # 使用模板
        return render(request, 'user_center_order.html', context)


# /user/address
# class AddressView(View):
# class AddressView(LoginRequiredView):
class AddressView(LoginRequiredMixin, View):
    """用户中心-地址页"""
    def get(self, request):
        """显示"""
        # 获取登录用户user
        user = request.user
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     address = None

        address = Address.objects.get_default_address(user)

        # 组织模板上下文
        context = {
            'address': address,
            'page': 'address'
        }

        # 使用模板
        return render(request, 'user_center_site.html', context)

    def post(self, request):
        """地址添加"""
        # 接收参数
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        # 参数校验
        if not all([receiver, addr, phone]):
            return render(request, 'user_center_site.html', {'errmsg': '数据不完整'})

        # 校验手机号

        # 业务处理：添加收货地址
        # 如果用户已经有默认地址，新添加的地址作为非默认地址，否则作为默认地址
        # 获取登录用户user
        user = request.user
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     address = None

        address = Address.objects.get_default_address(user)

        is_default = True
        if address is not None:
            is_default = False

        # 添加收货地址
        Address.objects.create(user=user,
                               receiver=receiver,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=is_default)

        # 返回应答，刷新地址页面
        return redirect(reverse('user:address'))











