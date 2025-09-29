from django.urls import path
from .views import AllotmentTrackerAPIView, GroupCategoryListAPIView, admin_register, AdminLoginView, AdminRefreshView
from api.admin.excel_upload import NeetExcelUploadAPIView
from api.admin.group_dropdown import GroupDropdownUploadAPIView
from . import views



urlpatterns = [
    path("allotment_tracker/", AllotmentTrackerAPIView.as_view(), name="allotment-tracker"),
    path('upload-excel/', NeetExcelUploadAPIView.as_view(), name='neet-excel-upload'),
    path('admin/group-dropdown/', GroupDropdownUploadAPIView.as_view(), name='group-dropdown-upload'),
    path('group-categories/', GroupCategoryListAPIView.as_view(), name='group-categories-list'),
    path("send-results-email/", views.send_results_email, name="send_results_email"),
    
    
    path("admin/register/", admin_register, name="admin_register"),
    path("admin/login/", AdminLoginView.as_view(), name="admin_login"),
    path("admin/refresh/", AdminRefreshView.as_view(), name="admin_refresh"),

]
