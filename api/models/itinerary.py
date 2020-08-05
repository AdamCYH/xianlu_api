from django.db import models
from django.urls import reverse
from imagekit.models.fields import ProcessedImageField

from api.models.poi import Site
from api.models.user import User


class Itinerary(models.Model):
    """
    Itinerary: stores the sets of trips.
    """
    owner = models.ForeignKey(
        User,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='itineraries',  # author.posts: get all posts belong to this user
    )
    title = models.CharField(max_length=100)
    image = ProcessedImageField(
        upload_to='itinerary',
        format='JPEG',
        options={'quality': 100},
        blank=True,
        null=True,
        default="default.jpeg"
    )
    # default pic
    posted_on = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )

    view = models.BigIntegerField(default=0)
    is_public = models.BooleanField(default=False)
    description = models.TextField()
    like = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post", args=[str(self.id)])

    def get_like_count(self):
        return self.likes.count()

    def get_comment_count(self):
        return self.comments.count()

    class Meta:
        db_table = 'itinerary'


class DayTrip(models.Model):
    """
    Trip: stores single trip on daily basis
    """
    owner = models.ForeignKey(
        User,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='daytrip',  # author.posts: get all posts belong to this user
    )
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE)
    sites = models.ManyToManyField(
        Site, blank=True, through='DayTripSite')
    day = models.IntegerField()

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'day_trip'
        unique_together = ('itinerary', 'day')


class DayTripSite(models.Model):
    """
    Trip: stores single trip on daily basis
    """
    owner = models.ForeignKey(
        User,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='day_trip_site',  # author.posts: get all posts belong to this user
    )

    day_trip = models.ForeignKey(DayTrip, on_delete=models.CASCADE)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='site_to_day_trip')
    order = models.IntegerField()

    class Meta:
        db_table = 'day_trip_site'
        unique_together = ('day_trip', 'order')

    def __str__(self):
        return str(self.id)


class Highlight(models.Model):
    photo = models.ImageField(default="default.jpeg")
    headertext = models.CharField(max_length=50)
    url = models.CharField(max_length=100)

    def __str__(self):
        return self.headertext

    class Meta:
        db_table = 'highlight'


class Featured(models.Model):
    itinerary = models.OneToOneField(Itinerary, on_delete=models.CASCADE)

    class Meta:
        db_table = 'featured'


class Comment(models.Model):
    itinerary = models.ForeignKey(
        Itinerary, on_delete=models.CASCADE, related_name='comments', )
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(null=False, blank=False)
    posted_on = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return self.comment

    class Meta:
        db_table = 'comment'


class Like(models.Model):
    itinerary = models.ForeignKey(
        Itinerary, on_delete=models.CASCADE, related_name='likes', )
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'like'
        unique_together = ("itinerary", "owner")

    def __str__(self):
        return 'Like: ' + self.owner.username + ' ' + self.itinerary.title


class Favorite(models.Model):
    user = models.ForeignKey(
        User, null=False, blank=False, on_delete=models.CASCADE, related_name='favorites')
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user) + "Favorites" + str(self.itinerary)

    class Meta:
        db_table = 'favorite'
