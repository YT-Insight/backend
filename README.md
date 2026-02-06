yt_insight/
├── manage.py
├── pyproject.toml / requirements.txt
├── .env
├── docker-compose.yml
├── Dockerfile
├── README.md

├── yt_insight/                 # Django project
│   ├── __init__.py
│   ├── asgi.py
│   ├── wsgi.py
│   ├── urls.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py             # общие настройки
│   │   ├── local.py            # dev
│   │   └── prod.py             # prod
│   └── celery.py

├── apps/
│   ├── __init__.py
│
│   ├── accounts/               # пользователи и auth
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py           # User
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── permissions.py
│   │   ├── urls.py
│   │   └── migrations/
│
│   ├── billing/                # подписки / Stripe
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py           # Plan, Subscription
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── webhooks.py
│   │   ├── services/
│   │   │   └── stripe.py
│   │   └── migrations/
│
│   ├── youtube/                # YouTube API
│   │   ├── services/
│   │   │   └── youtube_api.py
│   │   └── __init__.py
│
│   ├── analyses/               # ядро продукта
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py           # YouTubeAnalysis, AnalysisQuestion
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── permissions.py
│   │   ├── tasks.py            # Celery
│   │   ├── services/
│   │   │   ├── analyzer.py
│   │   │   └── summarizer.py
│   │   └── migrations/
│
│   ├── usage/                  # лимиты и квоты
│   │   ├── models.py           # UsageLimit, UsageHistory
│   │   ├── services/
│   │   │   └── limiter.py
│   │   └── migrations/
│
│   ├── ai/                     # AI abstraction
│   │   ├── providers/
│   │   │   ├── openai.py
│   │   │   └── local_llm.py
│   │   ├── prompts/
│   │   │   └── summary.txt
│   │   └── __init__.py
│
│   └── core/                   # общее
│       ├── models.py           # BaseModel (created_at, etc)
│       ├── permissions.py
│       ├── constants.py
│       └── utils.py
│
├── tests/
│   ├── accounts/
│   ├── billing/
│   ├── analyses/
│   └── usage/
│
└── scripts/
    ├── seed_plans.py
    └── reset_usage.py
