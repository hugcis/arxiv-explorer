from django.urls import path
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path('dbfill/', views.DBFill),
    path('authors/', views.AuthorsList.as_view()),
    path('authors/<uuid:pk>', views.AuthorsDetails.as_view()),
    path('papers/', views.PapersList.as_view()),
    path('papers/latest', views.LatestPapersDetails.as_view()),
    path('papers/<str:doi>', views.PapersDetailsByDOI.as_view()),
    path('papers/<uuid:pk>', views.PapersDetails.as_view()),
    path('closestNeighbors/<str:doi>', views.PaperNeighbors.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)

