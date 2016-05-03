from django.conf.urls import url, include
from entries import views


urlpatterns = [
    url(r'^$', views.EntriesView.as_view(), name="entries"),
    url(r'^add/$', views.AddEntry.as_view(), name='add'),
]
