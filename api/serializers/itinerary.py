from rest_framework import serializers

from api.models import DayTripSite, DayTrip, Comment, Like, Itinerary, Highlight, Featured, Site
from api.serializers.poi import SiteReadSerializer


class DayTripSiteReadSerializer(serializers.ModelSerializer):
    site = SiteReadSerializer(read_only=True)

    class Meta:
        model = DayTripSite
        fields = ('id', 'day_trip', 'site', 'order')


class DayTripSiteWriteSerializer(serializers.ModelSerializer):
    site = serializers.PrimaryKeyRelatedField(queryset=Site.objects.all())

    class Meta:
        model = DayTripSite
        fields = '__all__'
        read_only_fields = ('owner',)


class DayTripSerializer(serializers.ModelSerializer):
    sites = serializers.SerializerMethodField()

    def get_sites(self, instance):
        sites = DayTripSite.objects.filter(day_trip=instance).order_by('order')
        return DayTripSiteReadSerializer(sites, many=True).data

    class Meta:
        model = DayTrip
        fields = '__all__'
        read_only_fields = ('owner',)


class ItinerarySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    is_liked = serializers.SerializerMethodField()
    locations = serializers.SerializerMethodField()

    def get_is_liked(self, obj):
        if 'request' not in self.context:
            return False
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        else:
            likes = Like.objects.filter(itinerary=obj, owner=user)
            return len(likes) > 0

    def get_locations(self, obj):
        locations = dict()
        day_trips = DayTrip.objects.filter(itinerary_id=obj.id)
        for day_trip in day_trips:
            for site in day_trip.sites.all():
                city = site.city.city_name
                locations[city] = locations.get(city, 0) + 1
        sorted_locations = sorted(locations, key=locations.get, reverse=True)
        return sorted_locations

    class Meta:
        model = Itinerary
        fields = '__all__'
        read_only_fields = ('view', 'owner', 'like', 'is_liked')


class ItineraryDetailSerializer(ItinerarySerializer):
    comments = serializers.SerializerMethodField()

    def get_comments(self, obj):
        queryset = Comment.objects.filter(itinerary=obj)
        serializer = CommentSerializer(queryset, many=True)
        return serializer.data

    class Meta:
        model = Itinerary
        fields = '__all__'
        read_only_fields = ('view', 'owner', 'like', 'is_liked')


class HighlightSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=False)

    class Meta:
        model = Highlight
        fields = '__all__'


class FeaturedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Featured
        fields = '__all__'


class FeaturedReadSerializer(serializers.ModelSerializer):
    itinerary = ItinerarySerializer()

    class Meta:
        model = Featured
        fields = '__all__'


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'
        read_only_fields = ('owner',)


class LikeDetailSerializer(serializers.ModelSerializer):
    itinerary = ItineraryDetailSerializer()

    class Meta:
        model = Like
        fields = '__all__'
        read_only_fields = ('owner',)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('owner',)
