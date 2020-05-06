from django.contrib import admin
from .models import Professor, Review, LikedReview, DislikedReview, ReportReview

# Register your models here.
admin.site.register(Professor)
admin.site.register(Review)

admin.site.register(LikedReview)
admin.site.register(DislikedReview)
admin.site.register(ReportReview)