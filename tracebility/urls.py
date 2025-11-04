from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('machine/<str:machine_name>/', views.machine_detail_view, name='machine_detail'),
    path('api/machine/<str:machine_name>/', views.machine_data_api, name='machine_data_api'),
    path('api/search/', views.search_qr_code, name='search_qr'),
    
        # Export
    path('export/<str:machine_name>/', views.export_machine_data, name='export_machine_data'),
    
    # Analytics
    path('analytics/', views.analytics_view, name='analytics'),
    path('api/analytics/', views.analytics_api, name='analytics_api'),
    path('api/analytics/export/', views.analytics_export, name='analytics_export'),

    
]