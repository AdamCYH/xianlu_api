import logging

from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from api.models import City, Restaurant
from api.serializers.poi import CitySerializer, AttractionSerializer, AttractionReadSerializer, RestaurantSerializer, \
    RestaurantReadSerializer, HotelSerializer, HotelReadSerializer

logger = logging.getLogger(__name__)


class CityViewSet(viewsets.ViewSet):
    queryset = City.objects
    serializer_class = CitySerializer

    def dispatch(self, request, *args, **kwargs):
        return super(CityViewSet, self).dispatch(request, *args, **kwargs)

    def list(self, request):
        serializer = self.serializer_class(self.queryset.all(), many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        else:
            logger.error(serializer.errors)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        city = get_object_or_404(self.queryset.all(), pk=pk)
        serializer = self.serializer_class(city)
        return Response(serializer.data)

    def update(self, request, pk=None):
        serializer = self.serializer_class(self.queryset.get(id=pk), data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        else:
            logger.error(serializer.errors)

        return Response(serializer.data)

    def destroy(self, request, pk=None):
        city = get_object_or_404(self.queryset.all(), pk=pk)
        city.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]


class AttractionViewSet(viewsets.ViewSet):
    """
    API endpoint that allows attractions to be viewed or edited.
    """

    serializer_class = AttractionSerializer
    serializer_class_read = AttractionReadSerializer

    def dispatch(self, request, *args, **kwargs):
        return super(AttractionViewSet, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Optionally restricts the attraction based on city
        """
        queryset = Attraction.objects.all()
        city = self.request.query_params.get('city', None)
        if city is not None:
            queryset = Attraction.objects.filter(site__city_id=city)
        return queryset

    def list(self, request):
        serializer = self.serializer_class_read(self.get_queryset().all(), many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            attraction = self.serializer_class_read(serializer.instance)
            return Response(attraction.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None):
        attraction = get_object_or_404(self.get_queryset().all(), pk=pk)
        serializer = self.serializer_class_read(attraction)
        return Response(serializer.data)

    def update(self, request, pk=None):
        serializer = self.serializer_class(self.get_queryset().get(site_id=pk), data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            attraction = self.serializer_class_read(serializer.instance)
            return Response(attraction.data)
        else:
            logger.error(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        attraction = get_object_or_404(self.get_queryset().all(), pk=pk)
        attraction.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]


class RestaurantViewSet(viewsets.ViewSet):
    """
    API endpoint that allows restaurants to be viewed or edited.
    """
    serializer_class = RestaurantSerializer
    serializer_class_read = RestaurantReadSerializer

    def dispatch(self, request, *args, **kwargs):
        return super(RestaurantViewSet, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Optionally restricts the restaurant based on city
        """
        queryset = Restaurant.objects.all()
        city = self.request.query_params.get('city', None)
        if city is not None:
            queryset = Restaurant.objects.filter(site__city_id=city)
        return queryset

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def list(self, request):
        serializer = self.serializer_class_read(self.get_queryset().all(), many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            restaurant = self.serializer_class_read(serializer.instance)
            return Response(restaurant.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None):
        restaurant = get_object_or_404(self.get_queryset().all(), pk=pk)
        serializer = self.serializer_class_read(restaurant)
        return Response(serializer.data)

    def update(self, request, pk=None):
        serializer = self.serializer_class(self.get_queryset().get(site_id=pk), data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            restaurant = self.serializer_class_read(serializer.instance)
            return Response(restaurant.data)
        else:
            logger.error(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        attraction = get_object_or_404(self.get_queryset().all(), pk=pk)
        attraction.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class HotelViewSet(viewsets.ViewSet):
    """
    API endpoint that allows hotels to be viewed or edited.
    """

    def dispatch(self, request, *args, **kwargs):
        return super(HotelViewSet, self).dispatch(request, *args, **kwargs)

    serializer_class = HotelSerializer
    serializer_class_read = HotelReadSerializer

    def get_queryset(self):
        """
        Optionally restricts the hotel based on city
        """
        queryset = Hotel.objects.all()
        city = self.request.query_params.get('city', None)
        if city is not None:
            queryset = Hotel.objects.filter(site__city_id=city)
        return queryset

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def list(self, request):
        serializer = self.serializer_class_read(self.get_queryset().all(), many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            hotel = self.serializer_class_read(serializer.instance)
            return Response(hotel.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None):
        hotel = get_object_or_404(self.get_queryset().all(), pk=pk)
        serializer = self.serializer_class_read(hotel)
        return Response(serializer.data)

    def update(self, request, pk=None):
        serializer = self.serializer_class(self.get_queryset().get(site_id=pk), data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            hotel = self.serializer_class_read(serializer.instance)
            return Response(hotel.data)
        else:
            logger.error(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        attraction = get_object_or_404(self.get_queryset().all(), pk=pk)
        attraction.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
