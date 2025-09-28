from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from api.models import NeetCounsellingSeatAllotment
import pandas as pd

class NeetExcelUploadAPIView(APIView):
    # permission_classes = [permissions.IsAdminUser]  # Only admin users ----- Change this after the admin is created ==Production Test==
    permission_classes = [permissions.AllowAny]  # Only for Testing
    

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(file)
        except Exception as e:
            return Response({"error": f"Error reading Excel: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Deactivate all existing records
        NeetCounsellingSeatAllotment.objects.update(is_active=False)

        created_count = 0
        for _, row in df.iterrows():
            NeetCounsellingSeatAllotment.objects.create(
                allotment_category=row.get("ALLOTMENT_CATEGORY", ""),
                allotment_year=row.get("ALLOTMENT_YEAR", 0),
                rank_no=row.get("RANK_NO", 0),
                allotted_quota=row.get("ALLOTTED_QUOTA", ""),
                allotted_institute=row.get("ALLOTTED_INSTITUTE", ""),
                state=row.get("STATE", ""),
                qualifying_group_or_course=row.get("QUALIFYING_GROUP_OR_COURSE", ""),
                speciality=row.get("SPECIALITY", ""),
                allotted_category=row.get("ALLOTTED_CATEGORY", ""),
                candidate_category=row.get("CANDIDATE_CATEGORY", ""),
                remarks=row.get("REMARKS", ""),
                is_active=row.get("IS_SHOW_YEAR", False)
            )
            created_count += 1

        return Response({"message": f"{created_count} records uploaded successfully."}, status=status.HTTP_201_CREATED)
