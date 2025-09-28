from django.db import models

class CounsellingSeatAllotmentTracker(models.Model):
    seqno = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    rank_no = models.IntegerField(blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    allotment_category = models.CharField(max_length=100, blank=True, null=True)
    qualifying_group_or_course = models.CharField(max_length=200, blank=True, null=True)
    specialization = models.CharField(max_length=200, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "COUNSELLING_SEAT_ALLOTMENT_TRACKER"

    def __str__(self):
        return f"{self.name} ({self.rank_no})"


class NeetCounsellingSeatAllotment(models.Model):
    allotment_category = models.CharField(max_length=255)
    allotment_year = models.PositiveIntegerField()
    rank_no = models.PositiveIntegerField()
    allotted_quota = models.CharField(max_length=255)
    allotted_institute = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    qualifying_group_or_course = models.CharField(max_length=255)
    speciality = models.CharField(max_length=255)
    allotted_category = models.CharField(max_length=255)
    candidate_category = models.CharField(max_length=255)
    remarks = models.TextField(blank=True, null=True)
    
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "neet_counselling_seat_allotment"

    def __str__(self):
        return f"{self.rank_no} - {self.allotted_institute}"