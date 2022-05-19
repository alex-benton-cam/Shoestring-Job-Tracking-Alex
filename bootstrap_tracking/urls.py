"""Alex_Tracking URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core import views
from core.models import Operation, Job, Worker ,Location

urlpatterns = [
    # Infrastructural
    path('admin/', admin.site.urls),
    path('', views.Index.as_view(), name='index'),
    
    # Main
    path('upload/', views.uploadOps, name='upload'),
    path('uploadlocs/', views.uploadLocs, name='uploadlocs'),
      
    # Model-based
    path('jobs/', views.ModelView.as_view(model=Job), name='jobs'),
    path('locations/', views.ModelView.as_view(model=Location), name='locations'),
    path('workers/', views.ModelView.as_view(model=Worker), name='workers'),    
    path('operations/', views.ModelView.as_view(model=Operation), name='operations'),
    
    # Detail Views
    path('operation/<slug:op>', views.OpDetail.as_view(), name='opdetail'),
    
    # Templates/ Placeholders
    path('operator/', views.OperatorDash.as_view(), name='operator'),
    path('cards/', views.Cards.as_view(), name='cards'),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),   
]
