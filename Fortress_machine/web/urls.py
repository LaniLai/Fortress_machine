
from django.conf.urls import url, include
from web.views import account
from web.views import home

urlpatterns = [
    url(r'^login.html$', account.LoginView.as_view()),
    url(r'^logout.html$', account.LogoutView.as_view()),
    url(r'^index.html$', home.IndexView.as_view()),
    url(r'^hosts-cmd.html$', home.HostsCMDView.as_view()),
    url(r'^hosts-file.html$', home.HostsFileView.as_view()),
    url(r'^hosts-log.html$', home.HostsLogView.as_view()),
]
