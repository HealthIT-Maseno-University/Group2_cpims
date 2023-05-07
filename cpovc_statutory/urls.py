from django.urls import path, re_path
from . import views

# This should contain urls related to registry ONLY

urlpatterns = [

    path('', views.stat_home, name='statutory'),
    path('remand/',views.remand, name='remand'),
    path('rescue/',views.rescue, name='rescue'),
   
       # Case Record Sheet Urls
    path('crs/', views.case_record_sheet,
         name='case_record_sheet')   
]