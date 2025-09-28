# api/admin/group_dropdown.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.serializers import GroupCategorySerializer
from api.models import GroupCategory
from django.db import IntegrityError, transaction

class GroupDropdownUploadAPIView(APIView):
    """
    POST JSON:
    Single object:
      { "group_name": "hello", "category_type": "a" }

    OR list:
      [
        { "group_name": "hello", "category_type": "a" },
        { "group_name": "hello", "category_type": "b" }
      ]

    Response includes created_count and skipped list (already existed).
    """
    permission_classes = []  # change if you want to restrict access

    def post(self, request):
        payload = request.data

        # Normalize to list
        if isinstance(payload, dict):
            items = [payload]
        elif isinstance(payload, list):
            items = payload
        else:
            return Response({"detail": "Invalid payload. Provide an object or list of objects."},
                            status=status.HTTP_400_BAD_REQUEST)

        created = []
        skipped = []
        errors = []

        for i, item in enumerate(items):
            serializer = GroupCategorySerializer(data=item)
            if not serializer.is_valid():
                errors.append({"index": i, "errors": serializer.errors})
                continue

            data = serializer.validated_data
            group_name = data["group_name"].strip()
            category_type = data["category_type"].strip()

            # Prevent duplicates: check first
            exists = GroupCategory.objects.filter(group_name__iexact=group_name,
                                                  category_type__iexact=category_type).exists()
            if exists:
                skipped.append({"group_name": group_name, "category_type": category_type})
                continue

            try:
                with transaction.atomic():
                    obj = GroupCategory.objects.create(group_name=group_name, category_type=category_type)
                    created.append({"id": obj.id, "group_name": obj.group_name, "category_type": obj.category_type})
            except IntegrityError as e:
                errors.append({"index": i, "error": str(e)})

        result = {
            "created_count": len(created),
            "created": created,
            "skipped_count": len(skipped),
            "skipped": skipped,
            "errors": errors
        }
        return Response(result, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
