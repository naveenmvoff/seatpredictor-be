from django.urls import path
from .views import AllotmentTrackerAPIView
from api.admin.excel_upload import NeetExcelUploadAPIView
from api.admin.group_dropdown import GroupDropdownUploadAPIView

urlpatterns = [
    path("allotment_tracker/", AllotmentTrackerAPIView.as_view(), name="allotment-tracker"),
    path('upload-excel/', NeetExcelUploadAPIView.as_view(), name='neet-excel-upload'),
    path('admin/group-dropdown/', GroupDropdownUploadAPIView.as_view(), name='group-dropdown-upload'),

]
