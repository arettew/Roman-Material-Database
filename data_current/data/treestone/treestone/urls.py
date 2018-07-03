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

from treestone.tree.views import StonesListView
from treestone.tree.views import MapView
from treestone.tree.views import TreeUpdate, StoneUpdate
from treestone.tree.views import TreeEdits
from treestone.tree.views import EditListView, TreeEditApproveView
from treestone.tree import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^csv/mymodel', StonesListView.as_view(), name='mymodel_csv'),
    url(r'^map', MapView.as_view(), name='map'),
    url(r'^get_features', views.get_features, name='get_features'),
    url(r'^result_info', views.result_info, name='result_info'),
    url(r'^tree/edit/(?P<pk>\d+)/$', TreeUpdate.as_view(), name='tree-update'),
    url(r'^stone/edit/(?P<pk>\d+)/$', StoneUpdate.as_view(), name='stone-update'),
    url(r'^edits-list', EditListView.as_view(), name='edits-list'),
    url(r'^tree/approve/(?P<pk>\d+)/$', TreeEditApproveView.as_view(), name='tree-edit-approve')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
