from django.urls import path
from . import views
from . import rework_views
from . import monitoring_views
app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('machine/<str:machine_name>/', views.machine_detail_view, name='machine_detail'),
    path('api/machine/<str:machine_name>/', views.machine_data_api, name='machine_data_api'),
    path('api/search/', views.search_qr_code, name='search_qr'),

    # Real-time SSE endpoints
    path('stream/dashboard/', views.sse_dashboard_stream, name='sse_dashboard'),
    path('stream/machine/<str:machine_name>/', views.sse_machine_stream, name='sse_machine'),

    # Export
    path('export/<str:machine_name>/', views.export_machine_data, name='export_machine_data'),

    # Analytics
    path('analytics/', views.analytics_view, name='analytics'),
    path('api/analytics/', views.analytics_api, name='analytics_api'),
    # Export URLs
    path('api/analytics/export/', views.analytics_export, name='analytics_export'),
    path('api/analytics/export/excel/', views.analytics_export_excel, name='analytics_export_excel'),  # NEW



    # 🔧 Rework
    path('rework/', rework_views.rework_page, name='rework_page'),
    path('rework/api/search/', rework_views.rework_search_api, name='rework_search_api'),
    path('rework/api/update/', rework_views.rework_update_api, name='rework_update_api'),
    
    path(
        'rework/api/record/<str:machine_name>/<int:prep_id>/',
        rework_views.rework_get_record_api,
        name='rework_get_record_api'
    ),
    
    
    
    path('monitoring/', monitoring_views.monitoring_page, name='monitoring_page'),
    
    # API endpoints
    path('monitoring/search/', monitoring_views.monitoring_search_api, name='monitoring_search_api'),
    path('monitoring/export-excel/', monitoring_views.monitoring_export_excel, name='monitoring_export_excel'),
    path('monitoring/chart-data/', monitoring_views.monitoring_chart_data_api, name='monitoring_chart_data_api'),

]
