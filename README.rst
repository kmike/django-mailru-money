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
(migrate, если используется South). В INSTALLED_APPS также должны быть
``'django.contrib.auth'`` и ``'django.contrib.contenttypes'``.

Использование
=============

TODO

Разработка
----------

Разработка идет на bitbucket.org и github.com:

* https://bitbucket.org/kmike/django-mailru-money/
* https://github.com/kmike/django-mailru-money/

Баг-трекер - на битбакете: https://bitbucket.org/kmike/django-mailru-money/issues/new