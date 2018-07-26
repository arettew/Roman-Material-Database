"""treestone URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings 
from django.conf.urls.static import static 
from django.contrib.auth import views as auth_views

from treestone.tree.views import StonesListView
from treestone.tree.views import MapView, HomeView, RegisterView
from treestone.tree.views import TreeUpdateView, StoneUpdateView, TreeCreateView, StoneCreateView
from treestone.tree.views import EditListView, TreeEditApproveView, StoneEditApproveView
from treestone.tree.views import RejectView
from treestone.tree import views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^accounts/login/$', auth_views.login, name='login'),
    url(r'^accounts/register/$', RegisterView.as_view(), name='register'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^password-reset/$', auth_views.PasswordResetView.as_view(), name='reset'),
    url(r'^password-reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/complete/$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^csv/mymodel', StonesListView.as_view(), name='mymodel_csv'),
    url(r'^map/$', MapView.as_view(), name='map'),
    url(r'^get_features', views.get_features, name='get_features'),
    url(r'^result_info', views.result_info, name='result_info'),
    url(r'^geojson/(?P<type>\w+)/(?P<pk>\d+)/$', views.get_geojson_file, name='get-geojson-file'),
    url(r'^trees/create/$', TreeCreateView.as_view(), name='tree-create'),
    url(r'^stones/create/$', StoneCreateView.as_view(), name='stone-create'),
    url(r'^trees/edit/(?P<pk>\d+)/$', TreeUpdateView.as_view(), name='tree-update'),
    url(r'^stones/edit/(?P<pk>\d+)/$', StoneUpdateView.as_view(), name='stone-update'),
    url(r'^edits-list/$', EditListView.as_view(), name='edits-list'),
    url(r'^trees/approve/(?P<pk>\d+)/$', TreeEditApproveView.as_view(), name='tree-edit-approve'),
    url(r'^stones/approve/(?P<pk>\d+)/$', StoneEditApproveView.as_view(), name='stone-edit-approve'),
    url(r'^approve-geojson', views.approve_geojson, name='get-edit-geojson'),
    url(r'^(?P<type>\w+)/approve/reject/(?P<pk>\d+)/$', RejectView.as_view(), name='tree-reject')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
