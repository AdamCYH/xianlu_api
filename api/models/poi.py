from django.db import models


class City(models.Model):
    country_name = models.CharField(max_length=30)
    city_name = models.CharField(max_length=30)
    photo = models.ImageField(default="default.jpeg")

    def __str__(self):
        return self.city_name

    class Meta:
        db_table = 'city'


class Site(models.Model):
    """
    Site: a site for visit, data retrieved from Yelp API
    """
    CATEGORY_CHOICES = [
        ('Attraction', 'Attraction'),
        ('Restaurant', 'Restaurant'),
        ('Hotel', 'Hotel'),
    ]
    name = models.CharField(max_length=100)
    latitude = models.CharField(max_length=15)
    longitude = models.CharField(max_length=15)
    site_category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    url = models.CharField(max_length=100)
    city = models.ForeignKey(City, null=True, on_delete=models.SET_NULL)
    address = models.CharField(max_length=100)
    description = models.TextField()
    photo = models.ImageField(default="default.jpeg")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'site'


class Attraction(models.Model):
    site = models.OneToOneField(Site, related_name='attraction', on_delete=models.CASCADE, primary_key=True)
    category = models.CharField(max_length=30)

    def __str__(self):
        return self.site

    class Meta:
        db_table = 'attraction'


class Restaurant(models.Model):
    site = models.OneToOneField(Site, related_name='restaurant', on_delete=models.CASCADE, primary_key=True)
    category = models.CharField(max_length=30)
    open_at = models.IntegerField()  # An integer represending the Unix time

    def __str__(self):
        return self.site

    class Meta:
        db_table = 'restaurant'


class Hotel(models.Model):
    site = models.OneToOneField(Site, related_name='hotel', on_delete=models.CASCADE, primary_key=True)
    category = models.CharField(max_length=30)
    star_rate = models.DecimalField(max_digits=2, decimal_places=1)

    def __str__(self):
        return self.site

    class Meta:
        db_table = 'hotel'
