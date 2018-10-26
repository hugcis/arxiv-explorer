import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField

class Author(models.Model):
    aid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    keyname = models.CharField(max_length=50, blank=False)
    forenames = models.TextField(blank=True)
    affiliation = models.TextField(blank=True)

    class Meta:
        unique_together = (('keyname', 'forenames', 'affiliation'),)

    def __str__(self) -> str:
        return self.keyname


class Paper(models.Model):
    pid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.TextField(blank=False)
    abstract = models.TextField(blank=False)
    doi = models.CharField(max_length=30, unique=True, blank=False)
    categories = ArrayField(
        models.CharField(max_length=30),
        blank=True
    )
    date = models.DateField()
    tokens = ArrayField(
        models.TextField(),

    )
    date_index = models.Index(fields=['date'])

    def __str__(self) -> str:
        return self.title + '-' + self.doi

class Authorship(models.Model):
    asid = models.AutoField(primary_key=True)
    aid = models.ForeignKey(Author, on_delete=models.CASCADE)
    pid = models.ForeignKey(Paper, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return str(self.aid) + '-' + str(self.pid)

class Coauthorship(models.Model):
    cid = models.AutoField(primary_key=True)
    aid1 = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='+')
    aid2 = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='+')

    def __str__(self) -> str:
        return str(self.aid1) + '-' + str(self.aid2)
