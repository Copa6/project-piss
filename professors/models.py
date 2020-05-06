from django.contrib.auth.models import User
from django.db import models
from colleges.models import College


# Create your models here.
class Professor(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=150, blank=False)
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='current_college')
    previous_college = models.ForeignKey(College, on_delete=models.SET_NULL, blank=True, null=True,
                                         related_name='previous_college')
    department = models.CharField(max_length=1500, blank=False)
    designation = models.CharField(max_length=1500, blank=True, default='')
    qualifications = models.CharField(max_length=3000, blank=True, default='')
    total_score = models.BigIntegerField(verbose_name='Total score obtained as sum of reviews', blank=True, default=0)
    num_reviews = models.IntegerField(verbose_name='Total number of reviews', blank=True, default=0)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


class Review(models.Model):
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    score = models.IntegerField(blank=False)
    title = models.CharField(max_length=1000, blank=False, default='-----')
    review = models.CharField(max_length=3000, blank=True, default='')
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    like_count = models.BigIntegerField(default=0)
    dislike_count = models.BigIntegerField(default=0)
    times_reported = models.IntegerField(default=0)


class DeletedReviews(models.Model):
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    score = models.IntegerField(blank=False)
    title = models.CharField(max_length=1000, blank=False, default='-----')
    review = models.CharField(max_length=3000, blank=True, default='')
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    like_count = models.BigIntegerField(default=0)
    dislike_count = models.BigIntegerField(default=0)
    times_reported = models.IntegerField(default=0)

    @classmethod
    def create_from_review(cls, existing_review):
        deleted_review = cls(
            professor=existing_review.professor,
            score=existing_review.score,
            title=existing_review.title,
            review=existing_review.review,
            added_by=existing_review.added_by,
            like_count=existing_review.like_count,
            dislike_count=existing_review.dislike_count,
            times_reported=existing_review.times_reported
        )
        deleted_review.save()
        return deleted_review

    def update(self, existing_review):
        self.professor = existing_review.professor
        self.score = existing_review.score
        self.title = existing_review.title
        self.review = existing_review.review
        self.added_by = existing_review.added_by
        self.like_count = existing_review.like_count
        self.dislike_count = existing_review.dislike_count
        self.times_reported = existing_review.times_reported
        self.save()


class LikedReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, null=False)


class DislikedReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, null=False)


class ReportReview(models.Model):
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    review = models.ForeignKey(Review, on_delete=models.SET_NULL, null=True)
    deleted_review = models.ForeignKey(DeletedReviews, on_delete=models.SET_NULL, null=True, default=None)
    reason = models.CharField(max_length=1000, blank=True, default=None, null=True)
