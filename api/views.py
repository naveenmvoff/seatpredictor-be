from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import NeetCounsellingSeatAllotmentTracker, NeetCounsellingSeatAllotment
from .serializers import NeetCounsellingSeatAllotmentTrackerSerializer
from rest_framework.views import APIView


@api_view(['POST'])         ####### ============ For Testing Only ============
def create_allotment(request):
    serializer = NeetCounsellingSeatAllotmentTrackerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Record created successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AllotmentTrackerAPIView(APIView):
    permission_classes = []  # Public endpoint (no authentication)

    def post(self, request):
        # Save request data into tracker table (for record-keeping)
        serializer = NeetCounsellingSeatAllotmentTrackerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # We save it, but don't use the ID

            # Build filter dictionary for NeetCounsellingSeatAllotment
            filters = {"is_active": True}  # Only active records

            rank_no = request.data.get("rank_no")
            if rank_no is not None:
                filters["rank_no__gte"] = rank_no

            state = request.data.get("state")
            if state and state.lower() != "all india":
                filters["state__iexact"] = state

            allotment_category = request.data.get("allotment_category")
            if allotment_category:
                filters["allotment_category__iexact"] = allotment_category

            qualifying_group_or_course = request.data.get("qualifying_group_or_course")
            if qualifying_group_or_course:
                filters["qualifying_group_or_course__iexact"] = qualifying_group_or_course

            specialization = request.data.get("specialization")
            if specialization:
                filters["speciality__iexact"] = specialization

            category = request.data.get("category")
            if category:
                filters["allotted_category__iexact"] = category

            # Fetch filtered results
            results = NeetCounsellingSeatAllotment.objects.filter(**filters).values(
                "allotment_category",
                "allotment_year",
                "rank_no",
                "allotted_quota",
                "allotted_institute",
                "state",
                "qualifying_group_or_course",
                "speciality",
                "allotted_category",
                "candidate_category",
                "remarks"
            )

            # Return only filtered results
            return Response({
                "filtered_results_count": results.count(),
                "filtered_results": list(results)
            }, status=status.HTTP_200_OK)

        # Invalid serializer
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)