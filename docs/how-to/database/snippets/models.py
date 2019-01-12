# models.py

from tortoise.models import Model
from tortoise import fields


class Post(Model):
    title = fields.CharField(max_length=80)
    content = fields.TextField()
    category = fields.ForeignKeyField("models.Category", related_name="posts")

    def __str__(self):
        return self.title


class Category(Model):
    name = fields.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name
