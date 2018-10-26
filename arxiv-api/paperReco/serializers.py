import uuid
from rest_framework import serializers
from .models import Author, Paper


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('aid', 'keyname', 'forenames', 'affiliation')


class PaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paper
        fields = ('pid', 'doi', 'title', 'abstract', 'categories', 'tokens', 'date')

class PaperWithAuthors(object):
    def __init__(self, paper, authors):
        self.title = paper.title
        self.abstract = paper.abstract
        self.doi = paper.doi
        self.categories = paper.categories
        self.date = paper.date
        self.authors = AuthorSerializer([auth.aid for auth in authors], many=True).data

class PaperWithAuthorsSerializer(serializers.Serializer):
    title = serializers.CharField()
    abstract = serializers.CharField()
    doi = serializers.CharField(max_length=30)
    categories = serializers.ListField(
        child=serializers.CharField(max_length=30)
    )
    date = serializers.DateField()
    authors = serializers.ListField(
        child=serializers.DictField()
    )
