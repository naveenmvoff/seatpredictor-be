"""
URL configuration for seatpredictor project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import include, path 

# Admin-only API for updating active year
from api.admin.year_update import set_active_allotment_year
from api.admin.user_data import get_all_tracker_data, get_tracker_stats


urlpatterns = [
    # Custom admin endpoints must come before the default admin URLs
    path("admin/year-update/", set_active_allotment_year, name="admin_set_active_allotment_year"),
    path("admin/user-data/", get_all_tracker_data, name="admin_get_all_tracker_data"),
    path("admin/user-data/stats/", get_tracker_stats, name="admin_get_tracker_stats"),

    path("admin/", admin.site.urls),
    path('api/', include('api.urls')),
]
