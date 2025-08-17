# Деплой приложения на удалённый сервер.

## Используется проект Django.

Этот проект включает в себя три приложения. 

        - Управление профилем;
        - Авторский блог;
        - Интернет магазин.

Одновременно реализован полностью административный функционал, Django, Django rest_framework/        

### Главная задача - деплой с GitHub на удалённый сервер.
Разные серверные площадки предлагают лёгкий деплой непосредственно с удалённых
репозиториев, но доступные **docker-vps** из недорогих не поддерживают в полном объёме - а
кто-то и вовсе - docker compose. 
Знакомый мне по курсу **timeweb.cloud** уже работает с  docker compose,
но упал с ошибкой при деплое, так как **volumes** попросил его определить место для **Postgres**.

В результате, снова арендовал себе сервер на **timeweb.cloud**.

### Деплой на сервер timeweb.cloud из репозитория на GitHub
Не удержался и зарегистрировал **доменное имя**. По хорошему, надо и **SSL-сертификат** выпустить,
но не стал заморачиваться ради одного дня работы приложения.

**Итак, входим на сервер:**
![image](https://github.com/user-attachments/assets/29c8308c-719c-4f50-ba09-a7bef4401379)

Почему такой вход, вместо, например, bash: **ssh root@194.87.86.200**. Это можно прописать 
в конфиге: bash: **nano ~/.ssh/config**. Тут можно любимые конфиги прописать.

![image](https://github.com/user-attachments/assets/67194519-99a3-448e-a9ff-3dddb7507a1c)

Пароль, который запрошен, это мой внутренний - он для всех ключей и я не стал его исключать,
а вот пароль на сервер не запрашивается, так как сохранил на сервере публичный ключ
![image](https://github.com/user-attachments/assets/2759cd36-ad8d-4848-95fc-a8686e56e3f4)

и конечно не забыть о правах: 
                              
                              chmod 700 ~/.ssh
                               
                              chmod 600 ~/.ssh/authorized_keys



**Первое, что нужно сделать?**

Опять создать **ssh-ключ**, например,
![image](https://github.com/user-attachments/assets/d44bdab9-4fc8-455c-a08c-935954cbbe0c)

**Вставляем публичный ключ на GitHub**
![image](https://github.com/user-attachments/assets/0dd7cc4d-adef-4be2-a153-96a31a77f5ed)

**Делаем проверку связи:**
![image](https://github.com/user-attachments/assets/081f7f94-7ab8-45aa-9aad-aa8cbc665949)

**Штатно клонируем репозиторий**
![image](https://github.com/user-attachments/assets/b0421c9f-7f51-4946-9cbf-77b3356234e8)

В корне сервера создал папку **mkdir projects && cd projects**

Клонировал **git clone git@github.com:Vadim-BAKH/last-django-practice.git**.

Смотрим.
![image](https://github.com/user-attachments/assets/b2f0427e-fb2d-4b0d-8787-5a3b51b11155)

На скане есть **poetry.lock**, но реально его не было после клонирования. Он и не мог быть 
в публичном репозитории. Создать можно двумя способами:

1. Скопировать с локального репозитория (с комп.).

2. Правильнее, на мой взгляд, установить **poetry**, не для этого случая, конечно, а для
   реального приложения, в которое можно будет легко добавлять зависимости.

#### Выполняем на сервере:

**install --upgrade pip**

**curl -sSL https://install.python-poetry.org | python3**

**export PATH="/root/.local/bin:$PATH"**

После этого:  **poetry lock**

#### DOCKER
На сервере нет контейнера, поэтому нужно его установить:

**sudo snap install docker** - это, например, будет последняя версия.

#### Виртуальное окружение
Создаем **.env** 
![image](https://github.com/user-attachments/assets/b147a593-1e40-4d06-a98d-fb79eda8a92f)

В него можно просто скопировать локальный **.env**.

Я оставил **debug=1**. Оставил только для того, что бы видеть картинки. В продакшн, конечно,
всю статику настрою на nginx и сделаю **debug=0**.
Вписал свой хост в **DJANGO_ALLOWED_HOSTS**.

**Вот мои виртуалки:**

DJANGO_SECRET_KEY=

LOGLEVEL=INFO

DJANGO_DEBUG=0

DJANGO_ALLOWED_HOSTS=194.87.86.200,vadimbakh.ru,www.vadimbakh.ru

SENTRY_DSN="https:

REDIS_URL=redis://redis:6379/1

POSTGRES_DB=

POSTGRES_USER=

POSTGRES_PASSWORD=

POSTGRES_HOST=db

POSTGRES_PORT=5432

#### Необходимые изменения.
У меня - в стиле бест практик в **settings.py**:
![image](https://github.com/user-attachments/assets/0a7065e2-1f9f-4a29-9bda-2ca8c5ed0ce5)

Попытка войти на сайт перенаправит на https, а так как нет SSL-ключа - будет ошибка, 
поэтому пока удалил данный скрипт.

В **shop/view.py** изменил адреса ссылок на свой домен.



#### DNS
Попытка собрать контейнер привела к ошибке. 

Отрыл порт 80 в брандмауэре UFW (Uncomplicated Firewall) на сервере: **sudo ufw allow 80**.

Внес изменения в Docker-демон **sudo nano /var/snap/docker/current/config/daemon.json**

в файле были только логи {
    "log-level":        "error",
}

добавил: {
    "log-level":        "error",
    "dns": ["8.8.8.8", "8.8.4.4"]
}

**"dns": ["8.8.8.8", "8.8.4.4"]** - задаёт DNS-серверы, которые будут использоваться контейнерами Docker 
для разрешения доменных имён. В данном случае указаны публичные DNS-серверы Google.

После этого перестартовал docker: **sudo snap start docker**, **sudo snap restart docker**

#### Loki
Так же выдал ошибку.

Решение - установка плагина длинной командой.

**docker plugin install grafana/loki-docker-driver:latest --alias loki --grant-all-permissions**

### Запуск приложения.
Запускаем на сервере
![image](https://github.com/user-attachments/assets/0c76231b-cb4e-40bb-9c6e-d1b491af1ada)

И ... **всё заработало**.
![image](https://github.com/user-attachments/assets/778310bc-4e0d-41de-96d4-37d69fa4c0ac)
![image](https://github.com/user-attachments/assets/190906bd-fa75-4bdb-bb93-8a6fc5f3a31b)

**Миграции** у меня прописаны в docker-compose.yaml.

Дальше, все штатно. Создаю Суперпользователя и можно работать.

**Что не стал уже делать:**

Не стал заморачиваться с **python manage.py makemessages -l ru**/**python manage.py compilemessages**.
Поэтому **локализаций-интернализаций** нет, но **задача то - в деплое**...

Можно посмотреть браузер.
![image](https://github.com/user-attachments/assets/7c16d80c-81ea-4e50-be45-cef5f7346f53)

Регистрация пользователя
![image](https://github.com/user-attachments/assets/c8e621f1-5129-4835-b64a-cc496d9f3638)

Админка для суперпользователя:
![image](https://github.com/user-attachments/assets/928ac589-0665-4cfe-87d8-2a095c0b9e7b)

Shop Index
![image](https://github.com/user-attachments/assets/2add9edc-91e7-4e86-9a03-e95369676ddc)

Product
![image](https://github.com/user-attachments/assets/660a84e6-e0dc-4458-b2db-9d29d5535df6)

Order create
![image](https://github.com/user-attachments/assets/609228fa-f3a6-4778-9a19-75ae47c68239)


В другом приложении блоги.
![image](https://github.com/user-attachments/assets/c5e9f93a-e777-4d53-9376-3e7a8791205b)
![image](https://github.com/user-attachments/assets/9c843c1e-dd18-431a-b017-cd945aae0e17)

### Вывод:  Деплой приложения из GitHab на удалённый сервер выполнен.






























