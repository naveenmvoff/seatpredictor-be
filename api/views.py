from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import NeetCounsellingSeatAllotmentTracker, NeetCounsellingSeatAllotment
from .serializers import NeetCounsellingSeatAllotmentTrackerSerializer
from rest_framework.views import APIView
from itertools import groupby
from operator import itemgetter

from .models import GroupCategory

from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json



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
        data = request.data

        # Conditionally save tracker record ONLY if a non-empty name is provided
        name = (data.get("name") or "").strip()
        if name:
            tracker_serializer = NeetCounsellingSeatAllotmentTrackerSerializer(data=data)
            if tracker_serializer.is_valid():
                tracker_serializer.save()  # Save for record-keeping
            # If invalid for other reasons, ignore and continue to filtering

        # Build filter dictionary for NeetCounsellingSeatAllotment
        filters = {"is_active": True}  # Only active records

        rank_no = data.get("rank_no")
        if rank_no not in (None, ""):
            filters["rank_no__gte"] = rank_no

        state = data.get("state")
        if state and str(state).lower() != "all india":
            filters["state__iexact"] = state

        allotment_category = data.get("allotment_category")
        if allotment_category:
            filters["allotment_category__iexact"] = allotment_category

        qualifying_group_or_course = data.get("qualifying_group_or_course")
        if qualifying_group_or_course:
            filters["qualifying_group_or_course__iexact"] = qualifying_group_or_course

        specialization = data.get("specialization")
        if specialization:
            filters["speciality__iexact"] = specialization

        category = data.get("category")
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



class GroupCategoryListAPIView(APIView):
    permission_classes = []  # public endpoint

    def get(self, request):
        """
        Return grouped JSON:
        [
          {"group_name": "...", "category_type": ["a","b", ...]},
          ...
        ]
        """
        # Query only the fields we need, ordered by group_name then category_type
        qs = GroupCategory.objects.all().values("group_name", "category_type").order_by("group_name", "category_type")

        # Transform queryset values() into a list of dicts
        rows = list(qs)  # each row: {'group_name': '...', 'category_type': '...'}

        # Group by group_name (qs is already ordered)
        grouped = []
        for group_name, items in groupby(rows, key=itemgetter("group_name")):
            types = [item["category_type"] for item in items]
            grouped.append({"group_name": group_name, "category_type": types})

        return Response(grouped, status=status.HTTP_200_OK)
    
    
    

@csrf_exempt
def send_results_email(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            recipient = data.get("email")
            results = data.get("results", [])

            # Build HTML table
            body = "<h3>NEET PG Results</h3><table border='1' cellspacing='0' cellpadding='5'>"
            body += "<tr><th>Sr. No</th><th>Rank</th><th>College</th><th>State</th><th>Category</th></tr>"
            for i, r in enumerate(results, 1):
                body += f"""
                <tr>
                  <td>{i}</td>
                  <td>{r.get('rank_no') or r.get('rank')}</td>
                  <td>{r.get('allotted_institute') or r.get('name')}</td>
                  <td>{r.get('state')}</td>
                  <td>{r.get('candidate_category') or r.get('category')}</td>
                </tr>
                """
            body += "</table>"

            # Create email
            msg = EmailMultiAlternatives(
                subject="Your NEET PG Seat Predictor Results",
                body="Please view your results below.",  # fallback text
                from_email=None,
                to=[recipient],
            )
            msg.attach_alternative(body, "text/html")
            msg.send()

            return JsonResponse({"status": "success", "message": "Email sent!"}, status=200)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)