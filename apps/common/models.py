import uuid
from django.db import models

class BaseModel(models.Model):
    """
    Абстрактная модель, добавляющая UUID вместо ID
    и поля created_at/updated_at во все сущности.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True