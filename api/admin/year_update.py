from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

from api.models import NeetCounsellingSeatAllotment

@csrf_exempt
@require_POST
def set_active_allotment_year(request: HttpRequest):
    """
    Admin-only endpoint to activate a specific year for a given allotment_category.

    Requires JWT authentication (access token).
    """

    # --- Authenticate using JWT ---
    jwt_auth = JWTAuthentication()
    try:
        user_auth_tuple = jwt_auth.authenticate(request)
        if user_auth_tuple is None:
            return JsonResponse({"detail": "Authentication credentials were not provided."}, status=401)

        user, _ = user_auth_tuple
        if not user.is_staff:
            return JsonResponse({"detail": "You do not have permission to perform this action."}, status=403)
    except AuthenticationFailed as e:
        return JsonResponse({"detail": str(e)}, status=401)

    # --- Parse request body ---
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON body"}, status=400)

    category = payload.get("allotment_category")
    year = payload.get("allotment_year")

    if not category or year is None:
        return JsonResponse({
            "detail": "Missing required fields: allotment_category and allotment_year"
        }, status=400)

    try:
        year = int(year)
    except (TypeError, ValueError):
        return JsonResponse({"detail": "allotment_year must be an integer"}, status=400)

    # --- Update DB ---
    with transaction.atomic():
        deactivated = NeetCounsellingSeatAllotment.objects.filter(
            allotment_category=category
        ).update(is_active=False)

        activated = NeetCounsellingSeatAllotment.objects.filter(
            allotment_category=category,
            allotment_year=year,
        ).update(is_active=True)

    return JsonResponse({
        "status": "ok",
        "allotment_category": category,
        "activated_year": year,
        "counts": {"deactivated_in_category": deactivated, "activated": activated},
    }, status=200)














# from django.http import JsonResponse, HttpRequest
# from django.views.decorators.http import require_POST
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.admin.views.decorators import staff_member_required
# from django.contrib.auth import authenticate
# from django.contrib.auth.decorators import user_passes_test
# from django.db import transaction
# import json
# import base64

# from api.models import NeetCounsellingSeatAllotment

# def check_admin_auth(request):
#     """Check if user is authenticated and is staff/admin"""
#     # Check session authentication first
#     if request.user.is_authenticated and request.user.is_staff:
#         return True
    
#     # Check for basic authentication in headers
#     auth_header = request.META.get('HTTP_AUTHORIZATION')
#     if auth_header and auth_header.startswith('Basic '):
#         try:
#             # Decode basic auth
#             encoded_credentials = auth_header.split(' ')[1]
#             decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
#             username, password = decoded_credentials.split(':', 1)
            
#             # Authenticate user
#             user = authenticate(username=username, password=password)
#             if user and user.is_staff:
#                 return True
#         except (ValueError, TypeError):
#             pass
    
#     return False

# @csrf_exempt
# @require_POST
# def set_active_allotment_year(request: HttpRequest):
#     """
#     Admin-only endpoint to activate a specific year for a given allotment_category.

#     Authentication options:
#     1. Session authentication (login via /admin/ first)
#     2. Basic authentication (add Authorization header)

#     Expected JSON body:
#     {
#         "allotment_category": "NEET_PG",
#         "allotment_year": 2023
#     }

#     Behavior:
#     - Sets is_active = False for all rows with the given allotment_category
#     - Sets is_active = True for rows with the given allotment_category AND allotment_year
#     """
#     # Check authentication
#     if not check_admin_auth(request):
#         return JsonResponse({"detail": "Authentication required. Must be admin/staff user."}, status=401)
    
#     try:
#         payload = json.loads(request.body.decode("utf-8"))
#     except json.JSONDecodeError:
#         return JsonResponse({"detail": "Invalid JSON body"}, status=400)

#     category = payload.get("allotment_category")
#     year = payload.get("allotment_year")

#     if not category or year is None:
#         return JsonResponse({
#             "detail": "Missing required fields: allotment_category and allotment_year"
#         }, status=400)

#     # Validate year is int
#     try:
#         year = int(year)
#     except (TypeError, ValueError):
#         return JsonResponse({"detail": "allotment_year must be an integer"}, status=400)

#     with transaction.atomic():
#         # Deactivate all in this category
#         deactivated = NeetCounsellingSeatAllotment.objects.filter(
#             allotment_category=category
#         ).update(is_active=False)

#         # Activate only the matching year within the category
#         activated = NeetCounsellingSeatAllotment.objects.filter(
#             allotment_category=category,
#             allotment_year=year,
#         ).update(is_active=True)

#     return JsonResponse({
#         "status": "ok",
#         "allotment_category": category,
#         "activated_year": year,
#         "counts": {"deactivated_in_category": deactivated, "activated": activated},
#     }, status=200)