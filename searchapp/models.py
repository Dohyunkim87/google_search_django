from django.db import models

# Create your models here.

class OrganicResult(models.Model):
    title = models.TextField(null=True, blank=True)
    authors = models.TextField(null=True, blank=True)
    link = models.URLField(null=True, blank=True)
    snippet = models.TextField(null=True, blank=True)
    publication_info = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title