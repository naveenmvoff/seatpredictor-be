from rest_framework import serializers
from .models import NeetCounsellingSeatAllotmentTracker, GroupCategory

class NeetCounsellingSeatAllotmentTrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = NeetCounsellingSeatAllotmentTracker
        fields = '__all__'

class GroupCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupCategory
        fields = ("id", "group_name", "category_type")
        read_only_fields = ("id",)
