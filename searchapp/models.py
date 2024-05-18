from django.db import models

# Create your models here.

class OrganicResult(models.Model):
    title = models.TextField()
    authors = models.TextField(null=True, blank=True)
    link = models.URLField()
    snippet = models.TextField()
    publication_info = models.TextField()

    def __str__(self):
        return self.title