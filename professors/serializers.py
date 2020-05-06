from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Professor, Review, LikedReview, DislikedReview, ReportReview, DeletedReviews


class ProfessorsSerializerPOST(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = '__all__'


class ProfessorsSerializerGET(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    college_name = serializers.SerializerMethodField()
    previous_college_name = serializers.SerializerMethodField()

    def get_rating(self, prof):
        if prof.num_reviews == 0:
            return 0
        else:
            return round(float(prof.total_score/prof.num_reviews) * 2)/2  # Rounding to nearest 0.5


    def get_college_name(self, prof):
        if prof.college is not None:
            return prof.college.name
        else:
            return None

    def get_previous_college_name(self, prof):
        try:
            if prof.previous_college is not None:
                return prof.previous_college.name
            else:
                return None
        except Exception as e:
            return None

    class Meta:
        model = Professor
        fields = ('id', 'name', 'college', 'previous_college', 'department', 'designation', 'rating', 'num_reviews',
                  'qualifications', 'college_name', 'previous_college_name')


class ReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class ReviewsSerializerGET(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField()
    is_disliked = serializers.SerializerMethodField()
    is_reported = serializers.SerializerMethodField()

    def get_is_liked(self, review):
        user_id = self.context.get("user_id")
        if user_id:
            try:
                LikedReview.objects.get(review=review.pk, user=user_id)
                return True
            except LikedReview.DoesNotExist: pass

        return False

    def get_is_disliked(self, review):
        user_id = self.context.get("user_id")
        if user_id:
            try:
                DislikedReview.objects.get(review=review.pk, user=user_id)
                return True
            except DislikedReview.DoesNotExist:
                pass
        return False

    def get_is_reported(self, review):
        user_id = self.context.get("user_id")
        if user_id:
            try:
                ReportReview.objects.get(review=review.pk, reported_by=user_id)
                return True
            except ReportReview.DoesNotExist:
                pass
        return False

    class Meta:
        model = Review
        fields = ('id', 'score', 'title', 'review', 'is_liked', 'is_disliked', 'is_reported')


class LikedReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikedReview
        fields = '__all__'


class DislikedReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = DislikedReview
        fields = '__all__'


class ReportReviewSerializerGET(serializers.ModelSerializer):
    class Meta:
        model = ReportReview
        fields = ['reason']


class ReportReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportReview
        fields = '__all__'


class DeletedReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeletedReviews
        fields = '__all__'
