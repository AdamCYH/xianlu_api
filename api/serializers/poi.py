from rest_framework import serializers
from rest_framework.utils import model_meta

from api.models import City, Site, Attraction, Restaurant, Hotel


class CitySerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=False)

    class Meta:
        model = City
        fields = '__all__'


class SiteWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = '__all__'


class SiteReadSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)

    class Meta:
        model = Site
        fields = '__all__'


class AttractionSerializer(serializers.ModelSerializer):
    site = SiteWriteSerializer()

    def create(self, validated_data):
        site_data = validated_data.pop('site')
        site_obj = Site.objects.create(**site_data)
        attraction = Attraction.objects.create(site=site_obj, **validated_data)
        return attraction

    def update(self, instance, validated_data):
        site_data = validated_data.pop('site')
        instance.site = validated_data.get('site', instance.site)

        site_info = model_meta.get_field_info(instance)
        attraction_info = model_meta.get_field_info(instance.site)

        update_attributes(site_data, instance.site, site_info)
        update_attributes(validated_data, instance, attraction_info)

        return instance

    class Meta:
        model = Attraction
        fields = '__all__'
        read_only_fields = ('site',)


class AttractionReadSerializer(serializers.ModelSerializer):
    site = SiteReadSerializer()

    class Meta:
        model = Attraction
        fields = '__all__'
        read_only_fields = ('site',)


class RestaurantSerializer(serializers.ModelSerializer):
    site = SiteWriteSerializer()

    def create(self, validated_data):
        site_data = validated_data.pop('site')
        site_obj = Site.objects.create(**site_data)
        restaurant = Restaurant.objects.create(site=site_obj, **validated_data)
        return restaurant

    def update(self, instance, validated_data):
        site_data = validated_data.pop('site')
        instance.site = validated_data.get('site', instance.site)

        site_info = model_meta.get_field_info(instance)
        restaurant_info = model_meta.get_field_info(instance.site)

        update_attributes(site_data, instance.site, site_info)
        update_attributes(validated_data, instance, restaurant_info)

        return instance

    class Meta:
        model = Restaurant
        fields = '__all__'
        read_only_fields = ('site',)


class RestaurantReadSerializer(serializers.ModelSerializer):
    site = SiteReadSerializer()

    class Meta:
        model = Restaurant
        fields = '__all__'
        read_only_fields = ('site',)


class HotelSerializer(serializers.ModelSerializer):
    site = SiteWriteSerializer()

    def create(self, validated_data):
        site_data = validated_data.pop('site')
        site_obj = Site.objects.create(**site_data)
        hotel = Hotel.objects.create(site=site_obj, **validated_data)
        return hotel

    def update(self, instance, validated_data):
        site_data = validated_data.pop('site')
        instance.site = validated_data.get('site', instance.site)

        site_info = model_meta.get_field_info(instance)
        hotel_info = model_meta.get_field_info(instance.site)

        update_attributes(site_data, instance.site, site_info)
        update_attributes(validated_data, instance, hotel_info)

        return instance

    class Meta:
        model = Hotel
        fields = '__all__'
        read_only_fields = ('site',)


class HotelReadSerializer(serializers.ModelSerializer):
    site = SiteReadSerializer()

    class Meta:
        model = Hotel
        fields = '__all__'
        read_only_fields = ('site',)


def update_attributes(data, instance, info):
    for attr, value in data.items():
        if attr in info.relations and info.relations[attr].to_many:
            field = getattr(instance, attr)
            field.set(value)
        else:
            setattr(instance, attr, value)
    instance.save()
