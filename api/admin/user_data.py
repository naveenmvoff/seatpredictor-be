from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers import serialize
import json
import base64

from api.models import NeetCounsellingSeatAllotmentTracker


def check_admin_auth(request):
    """Check if user is authenticated and is staff/admin"""
    # Check session authentication first
    if request.user.is_authenticated and request.user.is_staff:
        return True
    
    # Check for basic authentication in headers
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if auth_header and auth_header.startswith('Basic '):
        try:
            # Decode basic auth
            encoded_credentials = auth_header.split(' ')[1]
            decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
            username, password = decoded_credentials.split(':', 1)
            
            # Authenticate user
            user = authenticate(username=username, password=password)
            if user and user.is_staff:
                return True
        except (ValueError, TypeError):
            pass
    
    return False


@csrf_exempt
@require_GET
def get_all_tracker_data(request: HttpRequest):
    """
    Admin-only endpoint to get all data from NeetCounsellingSeatAllotmentTracker table.

    Authentication options:
    1. Session authentication (login via /admin/ first)
    2. Basic authentication (add Authorization header)

    Query parameters:
    - page: Page number for pagination (optional, default=1)
    - page_size: Number of records per page (optional, default=100, max=1000)
    - search: Search term to filter by name, email, or phone_number (optional)
    - allotment_category: Filter by allotment category (optional)
    - state: Filter by state (optional)

    Response format:
    {
        "status": "ok",
        "data": [...],
        "pagination": {
            "current_page": 1,
            "total_pages": 10,
            "total_records": 1000,
            "page_size": 100,
            "has_next": true,
            "has_previous": false
        }
    }
    """
    # Check authentication
    if not check_admin_auth(request):
        return JsonResponse({"detail": "Authentication required. Must be admin/staff user."}, status=401)
    
    try:
        # Get query parameters
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 100)), 1000)  # Max 1000 records per page
        search_term = request.GET.get('search', '').strip()
        allotment_category_filter = request.GET.get('allotment_category', '').strip()
        state_filter = request.GET.get('state', '').strip()
        
        # Start with all records
        queryset = NeetCounsellingSeatAllotmentTracker.objects.all()
        
        # Apply filters
        if search_term:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(name__icontains=search_term) | 
                Q(email__icontains=search_term) | 
                Q(phone_number__icontains=search_term)
            )
        
        if allotment_category_filter:
            queryset = queryset.filter(allotment_category__icontains=allotment_category_filter)
            
        if state_filter:
            queryset = queryset.filter(state__icontains=state_filter)
        
        # Order by seqno (primary key) for consistent pagination
        queryset = queryset.order_by('seqno')
        
        # Apply pagination
        paginator = Paginator(queryset, page_size)
        total_records = paginator.count
        total_pages = paginator.num_pages
        
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
            page = 1
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
            page = paginator.num_pages
        
        # Convert queryset to list of dictionaries
        data = []
        for record in page_obj:
            data.append({
                'seqno': record.seqno,
                'name': record.name,
                'phone_number': record.phone_number,
                'email': record.email,
                'rank_no': record.rank_no,
                'state': record.state,
                'allotment_category': record.allotment_category,
                'qualifying_group_or_course': record.qualifying_group_or_course,
                'specialization': record.specialization,
                'category': record.category,
                'created_at': record.created_at.isoformat() if record.created_at else None,
                'updated_at': record.updated_at.isoformat() if record.updated_at else None,
            })
        
        return JsonResponse({
            "status": "ok",
            "data": data,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_records": total_records,
                "page_size": page_size,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            },
            "filters_applied": {
                "search": search_term or None,
                "allotment_category": allotment_category_filter or None,
                "state": state_filter or None,
            }
        }, status=200)
        
    except ValueError as e:
        return JsonResponse({"detail": f"Invalid parameter value: {str(e)}"}, status=400)
    except Exception as e:
        return JsonResponse({"detail": f"Server error: {str(e)}"}, status=500)


@csrf_exempt
@require_GET
def get_tracker_stats(request: HttpRequest):
    """
    Admin-only endpoint to get statistics about NeetCounsellingSeatAllotmentTracker data.
    
    Returns counts grouped by various fields.
    """
    # Check authentication
    if not check_admin_auth(request):
        return JsonResponse({"detail": "Authentication required. Must be admin/staff user."}, status=401)
    
    try:
        from django.db.models import Count
        
        # Get total count
        total_records = NeetCounsellingSeatAllotmentTracker.objects.count()
        
        # Get counts by allotment_category
        category_stats = list(
            NeetCounsellingSeatAllotmentTracker.objects
            .values('allotment_category')
            .annotate(count=Count('seqno'))
            .order_by('-count')
        )
        
        # Get counts by state
        state_stats = list(
            NeetCounsellingSeatAllotmentTracker.objects
            .values('state')
            .annotate(count=Count('seqno'))
            .order_by('-count')
        )
        
        # Get counts by category
        category_type_stats = list(
            NeetCounsellingSeatAllotmentTracker.objects
            .values('category')
            .annotate(count=Count('seqno'))
            .order_by('-count')
        )
        
        return JsonResponse({
            "status": "ok",
            "statistics": {
                "total_records": total_records,
                "by_allotment_category": category_stats,
                "by_state": state_stats,
                "by_category": category_type_stats,
            }
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"detail": f"Server error: {str(e)}"}, status=500)