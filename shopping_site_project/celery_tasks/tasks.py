# 导入Celery类
from celery import Celery
from django.conf import settings
from django.core.mail import send_mail

# 初始化django运行所依赖的环境变量
# 这两行代码在启动worker一端打开
import os
# import django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
# django.setup()

from goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner


# 创建Celery类的对象
app = Celery('celery_tasks.tasks', broker='redis://172.16.179.142:6379/4')


# 封装任务函数
@app.task
def send_register_active_email(to_email, username, token):
    """发送激活邮件"""
    # 组织邮件信息
    subject = '天天生鲜欢迎信息'
    message = ''
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    html_message = """
        <h1>%s, 欢迎您成为天天生鲜注册会员</h1>
        请点击一下链接激活您的账号(1小时之内有效)<br/>
        <a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>
    """ % (username, token, token)

    # 发送激活邮件
    # send_mail(subject='邮件标题',
    #           message='邮件正文',
    #           from_email='发件人',
    #           recipient_list='收件人列表')
    # 模拟send_mail发送邮件时间
    import time
    time.sleep(5)
    send_mail(subject, message, sender, receiver, html_message=html_message)


@app.task
def generate_static_index_html():
    """生成静态首页文件"""
    # 获取商品的分类信息
    types = GoodsType.objects.all()

    # 获取首页的轮播商品的信息
    index_banner = IndexGoodsBanner.objects.all().order_by('index')

    # 获取首页的促销活动的信息
    promotion_banner = IndexPromotionBanner.objects.all().order_by('index')

    # 获取首页分类商品的展示信息
    for type in types:
        # 获取type种类在首页展示的图片商品的信息和文字商品的信息
        # QuerySet
        image_banner = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1)
        title_banner = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0)

        # 给type对象增加属性title_banner,image_banner
        # 分别保存type种类在首页展示的文字商品和图片商品的信息
        type.title_banner = title_banner
        type.image_banner = image_banner

    # 判断用户用户是否已登录
    cart_count = 0

    # 组织模板上下文
    context = {
        'types': types,
        'index_banner': index_banner,
        'promotion_banner': promotion_banner,
        'cart_count': cart_count
    }

    # 使用模板
    # 1.加载模板文件
    from django.template import loader
    temp = loader.get_template('static_index.html')

    # 2.模板渲染
    static_html = temp.render(context)

    # 生成静态首页文件
    save_path = os.path.join(settings.BASE_DIR, 'static/index.html')
    with open(save_path, 'w') as f:
        f.write(static_html)

