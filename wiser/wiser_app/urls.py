from django.conf.urls import url
from . import views
urlpatterns = [
    # url(r'^hello/', views., name='helloWordView'),
    url(r'^GetRepoList/', views.GetRepoList().as_view()),
    url(r'^GetTopContributors/', views.GetTopContributors().as_view()),
]