from rest_framework import serializers
from .models import CounsellingSeatAllotmentTracker

class CounsellingSeatAllotmentTrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CounsellingSeatAllotmentTracker
        fields = '__all__'

