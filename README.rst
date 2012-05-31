===================
django-mailru-money
===================

django-mailru-money - это приложение для подключения django-сайта
к платежной системе `деньги@mail.ru <http://money.mail.ru/>`_.

Лицензия - MIT.
Поддерживается python 2.6, 2.7 и 3.2; django 1.3 и 1.4.

Установка
=========

::

    $ pip install django-mailru-money

В settings.py пропишите данные своего магазина::

    MAILRU_MONEY_SHOP_ID = 'my_shop_id'
    MAILRU_MONEY_SECRET_KEY = 'my_secret_key'

Подключите обработчик приема платежей в urls.py::

    urlpatterns = patterns('',
        # ...
        url(r'^mailru-money/', include('mailru_money.urls')),
        # ...
    )

ResultURL (который нужно сообщить в money.mail.ru) в этом случае
будет ``http://your-site.com/mailru-money/result/``.

Затем добавьте ``'mailru_money'`` в INSTALLED_APPS и выполните syncdb
(migrate, если используется South).

В INSTALLED_APPS также должны быть ``'django.contrib.auth'``
и ``'django.contrib.contenttypes'``.

Использование
=============

На странице оплаты используйте ``mailru_money.forms.MailruOrderForm``
для вывода формы оплаты и формирования заказа::

    # views.py
    from django.shortcuts import get_object_or_404, render
    from mailru_money.forms import MailruOrderForm
    from myapp.models import Item

    @login_required
    def pay(request, item_id)

        # товар, который будем оплачивать
        item = get_object_or_404(Item, id=item_id)

        # создаем заказ
        form = MailruOrderForm(
            amount = item.price,
            description = item.description,
            user = request.user
            pay_for = item,
        )

        return render(request, 'myapp/pay.html', {'form': form})

В шаблоне требуется сформировать форму оплаты::

    {# myapp/pay.html #}
    {# ... #}

    <form method='post' action='{{ form.ACTION }}'>
        {{ form }}
        <input type='submit' value='Оплатить через Деньги@mail.ru'>
    </form>

    {# ... #}

Обратите внимание, что {% csrf_token %} использовать не нужно.
Форма будет выведена как набор скрытых полей.

Обработку платежей можно осуществлять в сигнале
``mailru_money.signals.order_status_changed``::

    from mailru_money.models import MailruOrder
    from mailru_money.signals import order_status_changed

    from myapp.models import Item

    def mailru_payment_received(sender, order, old_status, **kwargs):
        item = order.pay_for
        if order.state == MailruOrder.PAID:
            item.deliver_to(order.user)
        elif order.state == MailruOrder.REJECTED:
            item.unblock()

    order_status_changed.connect(mailru_payment_received)

Сигнал шлется только когда у заказа изменился статус. Оплаченный заказ при
этом стать неоплаченным не может.

django-mailru-money поддерживает и другую схему работы
(можно не использовать встроенные средства для контроля заказов).
См. исходный код, если описанная выше схема не устраивает.

Разработка
----------

Разработка идет на bitbucket.org и github.com:

* https://bitbucket.org/kmike/django-mailru-money/
* https://github.com/kmike/django-mailru-money/

Баг-трекер - на битбакете: https://bitbucket.org/kmike/django-mailru-money/issues/new

Для запуска тестов склонируйте репозиторий, установите `tox <http://tox.testrun.org>`_
и запустите

::

    $ tox

из корня репозитория.
