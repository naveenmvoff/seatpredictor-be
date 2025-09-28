from django.urls import path
from .views import create_allotment
from api.admin.excel_upload import NeetExcelUploadAPIView

urlpatterns = [
    path('allotment_tracker/', create_allotment, name='allotment_tracker'),
    path('upload-excel/', NeetExcelUploadAPIView.as_view(), name='neet-excel-upload'),
]
