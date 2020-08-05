import logging

from django.db import IntegrityError
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response

from api.group_permissions import IsOwnerOrReadOnly
from api.models import DayTrip, Itinerary, DayTripSite, Highlight, Featured, Comment, Like, User
from api.serializers.itinerary import DayTripSerializer, DayTripSiteReadSerializer, DayTripSiteWriteSerializer, \
    ItinerarySerializer, ItineraryDetailSerializer, HighlightSerializer, FeaturedSerializer, FeaturedReadSerializer, \
    CommentSerializer, LikeDetailSerializer, LikeSerializer

logger = logging.getLogger(__name__)


class DayTripViewSet(viewsets.ViewSet):
    """
    API endpoint that allows day trip to be viewed or edited.
    """
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = DayTripSerializer

    def dispatch(self, request, *args, **kwargs):
        return super(DayTripViewSet, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Optionally restricts the day trips under a particular itinerary
        """
        queryset = DayTrip.objects.all()
        itinerary = self.request.query_params.get('itinerary', None)
        if itinerary is not None:
            iti_obj = get_object_or_404(Itinerary, pk=itinerary)
            if iti_obj is not None and (iti_obj.is_public or iti_obj.owner == self.request.user):
                queryset = queryset.filter(itinerary=iti_obj)
            else:
                queryset = queryset.none()
        return queryset

    def list(self, request):
        serializer = self.serializer_class(self.get_queryset().all().order_by('day'), many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(owner=request.user)
        else:
            logger.error(serializer.errors)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        day_trip = get_object_or_404(self.get_queryset().all(), pk=pk)
        serializer = self.serializer_class(day_trip)
        return Response(serializer.data)

    def update(self, request, pk=None):
        serializer = self.serializer_class(self.get_queryset().get(id=pk), data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(owner=request.user)
        else:
            logger.error(serializer.errors)

        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        new_index = self.request.query_params.get('new_order', None)
        if new_index is None:
            return Response({"status": "invalid parameter"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            new_index = int(new_index)
        except ValueError:
            return Response({"status": "invalid parameter"}, status=status.HTTP_400_BAD_REQUEST)

        day_trip = get_object_or_404(self.get_queryset().all(), pk=pk)
        original_index = day_trip.order
        if new_index == day_trip.order:
            pass
        elif new_index > day_trip.order:
            day_trip.order = -1
            day_trip.save()
            day_trips = self.get_queryset().filter(itinerary=day_trip.itinerary)
            for trip in day_trips:
                if original_index < trip.order <= new_index:
                    trip.order -= 1
                    trip.save()
            day_trip.order = new_index
            day_trip.save()
        else:
            day_trip.order = -1
            day_trip.save()
            day_trips = self.get_queryset().filter(itinerary=day_trip.itinerary)
            for trip in day_trips:
                if new_index <= trip.order < original_index:
                    trip.order += 1
                    trip.save()
            day_trip.order = new_index
            day_trip.save()

        return Response({"status": "successful"}, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        day_trip = get_object_or_404(self.get_queryset().all(), pk=pk)
        day_trip.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
        return [permission() for permission in permission_classes]


class DayTripSiteViewSet(viewsets.ViewSet):
    """
    API endpoint that allows day trip site to be viewed or edited.
    """

    def dispatch(self, request, *args, **kwargs):
        return super(DayTripSiteViewSet, self).dispatch(request, *args, **kwargs)

    queryset = DayTripSite.objects
    read_serializer_class = DayTripSiteReadSerializer
    serializer_class = DayTripSiteWriteSerializer

    def get_queryset(self):
        """
        Optionally restricts the day trip sites under a particular day trip
        """
        queryset = DayTripSite.objects.all()
        day_trip = self.request.query_params.get('day_trip', None)
        if day_trip is not None:
            day_trip_obj = get_object_or_404(DayTrip, pk=day_trip)
            if day_trip_obj is not None and (
                    day_trip_obj.itinerary.is_public or day_trip_obj.itinerary.owner == self.request.user):
                queryset = queryset.filter(day_trip=day_trip_obj)
            else:
                queryset = queryset.none()
        else:
            queryset = DayTripSite.objects.filter(day_trip__itinerary__is_public=True)
        return queryset

    def list(self, request):
        serializer = self.read_serializer_class(self.get_queryset().order_by('order'), many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            site = serializer.save(owner=request.user)
            return Response(self.read_serializer_class(site).data, status=status.HTTP_201_CREATED)
        else:
            logger.error(serializer.errors)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        day_trip = get_object_or_404(self.queryset.all(), pk=pk)
        serializer = self.read_serializer_class(day_trip)
        return Response(serializer.data)

    def update(self, request, pk=None):
        serializer = self.serializer_class(self.queryset.get(id=pk), data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(owner=request.user)
        else:
            logger.error(serializer.errors)

        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        new_index = self.request.query_params.get('new_order', None)
        if new_index is None:
            return Response({"status": "invalid parameter"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            new_index = int(new_index)
        except ValueError:
            return Response({"status": "invalid parameter"}, status=status.HTTP_400_BAD_REQUEST)

        day_trip_site = get_object_or_404(self.queryset.all(), pk=pk)
        original_index = day_trip_site.order
        if new_index == day_trip_site.order:
            pass
        elif new_index > day_trip_site.order:
            day_trip_site.order = -1
            day_trip_site.save()
            day_trip_sites = self.queryset.filter(day_trip=day_trip_site.day_trip).order_by("order")
            for site in day_trip_sites:
                if original_index < site.order <= new_index:
                    site.order -= 1
                    site.save()
            day_trip_site.order = new_index
            day_trip_site.save()
        else:
            day_trip_site.order = -1
            day_trip_site.save()
            day_trip_sites = self.queryset.filter(day_trip=day_trip_site.day_trip).order_by("-order")
            for site in day_trip_sites:
                if new_index <= site.order < original_index:
                    site.order += 1
                    site.save()
            day_trip_site.order = new_index
            day_trip_site.save()
        serializer = self.read_serializer_class(
            DayTripSite.objects.filter(day_trip=day_trip_site.day_trip).order_by("order"), many=True)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        day_trip_site = get_object_or_404(self.queryset.all(), pk=pk)
        delete_order = day_trip_site.order
        day_trip_site.order = -1
        day_trip_site.save()

        day_trip_sites = self.queryset.filter(day_trip=day_trip_site.day_trip).order_by("order")
        for site in day_trip_sites:
            if site.order > delete_order:
                site.order -= 1
                site.save()
        day_trip_site.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
        return [permission() for permission in permission_classes]


class ItineraryViewSet(viewsets.ViewSet):
    """
    API endpoint that allows itinerary to be viewed or edited.
    """
    serializer_class = ItinerarySerializer
    serializer_detail_class = ItineraryDetailSerializer

    def dispatch(self, request, *args, **kwargs):
        return super(ItineraryViewSet, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Optionally restricts the itinerary if an admin user want to retrieve all itinerary
        """
        list_all = self.request.query_params.get('allPublic', None)
        sort_by = self.request.query_params.get('sortBy', None)
        owner = self.request.query_params.get('owner', None)
        queryset = Itinerary.objects.all()
        if list_all is not None and list_all.lower() == 'true':
            queryset = queryset.filter(is_public=True)
        elif owner is not None:
            if self.request.user.is_anonymous or str(self.request.user.user_id) != owner:
                queryset = queryset.filter(Q(owner=owner) & Q(is_public=True))
            else:
                queryset = queryset.filter(owner=owner)
        else:
            if self.request.user.is_anonymous:
                queryset = queryset.filter(is_public=True)
            else:
                # Q(is_public=True) | Q(owner=self.request.user) or condition
                queryset = queryset.filter(Q(is_public=True) | Q(owner=self.request.user))
        if sort_by is not None:
            queryset = queryset.order_by('-' + sort_by)
        return queryset

    def list(self, request):
        limit = int(self.request.query_params.get('limit', 20))
        serializer = self.serializer_class(self.get_queryset()[:limit], many=True,
                                           context={"request": request})
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save(owner=request.user)
        else:
            logger.error(serializer.errors)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        itinerary = get_object_or_404(self.get_queryset(), pk=pk)
        if itinerary.owner != self.request.user:
            itinerary.view = itinerary.view + 1
            itinerary.save()
        serializer = self.serializer_detail_class(itinerary, context={"request": request})
        return Response(serializer.data)

    def update(self, request, pk=None):
        serializer = self.serializer_class(self.get_queryset().get(id=pk), data=request.data,
                                           context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save(owner=request.user)
        else:
            logger.error(serializer.errors)

        return Response(serializer.data)

    def destroy(self, request, pk=None):
        itinerary = get_object_or_404(self.get_queryset().all(), pk=pk)
        itinerary.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
        return [permission() for permission in permission_classes]


class HighlightViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows hotels to be viewed or edited.
    """

    def dispatch(self, request, *args, **kwargs):
        return super(HighlightViewSet, self).dispatch(request, *args, **kwargs)

    queryset = Highlight.objects.all()
    serializer_class = HighlightSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]


class FeaturedViewSet(viewsets.ViewSet):
    """
    API endpoint that allows hotels to be viewed or edited.
    """

    def dispatch(self, request, *args, **kwargs):
        return super(FeaturedViewSet, self).dispatch(request, *args, **kwargs)

    queryset = Featured.objects.all()
    serializer_class = FeaturedSerializer
    serializer_read_class = FeaturedReadSerializer

    def list(self, request):
        serializer = self.serializer_read_class(self.queryset.all(), many=True, context={"request": request})
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            featured = self.serializer_read_class(serializer.instance)
            return Response(featured.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(serializer.errors)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        featured = get_object_or_404(self.queryset.all(), pk=pk)
        serializer = self.serializer_read_class(featured)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        featured = get_object_or_404(self.queryset.all(), pk=pk)
        featured.delete()

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


class LikeViewSet(viewsets.ViewSet):
    """
    API endpoint that allows itinerary to be viewed or edited.
    """
    serializer_class = LikeSerializer
    serializer_read_class = LikeDetailSerializer
    queryset = Like.objects.all()

    def dispatch(self, request, *args, **kwargs):
        return super(LikeViewSet, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Optionally restricts the likes with particular user
        """
        queryset = Like.objects.all()
        user = self.request.query_params.get('user', None)
        if user is not None:
            user_obj = get_object_or_404(User, pk=user)
            if user_obj is not None:
                queryset = queryset.filter(owner=user)
            else:
                queryset = queryset.none()

        return queryset

    def list(self, request):
        serializer = self.serializer_read_class(self.get_queryset(), many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                like = serializer.save(owner=request.user)
                like.itinerary.like += 1
                like.itinerary.save()
            except IntegrityError:
                return Response({"Status": "Already liked."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.error(serializer.errors)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        likes = self.queryset.filter(itinerary_id=pk)
        serializer = self.serializer_class(likes, many=True)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        likes = self.queryset.filter(itinerary_id=pk, owner=request.user)
        if len(likes) > 0:
            for like in likes:
                like.itinerary.like -= 1
                like.itinerary.save()
                like.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
        return [permission() for permission in permission_classes]


class CommentViewSet(viewsets.ViewSet):
    """
    API endpoint that allows itinerary to be viewed or edited.
    """
    serializer_class = CommentSerializer

    def dispatch(self, request, *args, **kwargs):
        return super(CommentViewSet, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Optionally restricts the itinerary if an admin user want to retrieve all itinerary
        """
        queryset = Comment.objects.all()
        itinerary = self.request.query_params.get('itinerary', None)
        if itinerary is not None:
            queryset.filter(itinerary_id=itinerary)
        return queryset

    def list(self, request):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(owner=request.user)
        else:
            logger.error(serializer.errors)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        user = get_object_or_404(self.get_queryset().all(), pk=pk)
        serializer = self.serializer_class(user)
        return Response(serializer.data)

    def update(self, request, pk=None):
        serializer = self.serializer_class(self.get_queryset().get(id=pk), data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        else:
            logger.error(serializer.errors)

        return Response(serializer.data)

    def destroy(self, request, pk=None):
        comment = get_object_or_404(self.get_queryset(), pk=pk)
        comment.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
        return [permission() for permission in permission_classes]
