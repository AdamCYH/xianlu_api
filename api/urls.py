from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers

from api.views.itinerary import DayTripViewSet, DayTripSiteViewSet, ItineraryViewSet, HighlightViewSet, FeaturedViewSet, \
    LikeViewSet, CommentViewSet
from api.views.poi import CityViewSet, AttractionViewSet, RestaurantViewSet, HotelViewSet
from api.views.user import UserView, GroupViewSet

router = SimpleRouter()
# POI
router.register(r'city', CityViewSet, basename='city')
router.register(r'attraction', AttractionViewSet, basename='attraction')
router.register(r'restaurant', RestaurantViewSet, basename='restaurant')
router.register(r'hotel', HotelViewSet, basename='hotel')

# Itinerary
router.register(r'day-trip', DayTripViewSet, basename='day-trip')
router.register(r'day-trip-site', DayTripSiteViewSet, basename='day-trip-site')
router.register(r'itinerary', ItineraryViewSet, basename='itinerary')
router.register(r'highlight', HighlightViewSet, basename='highlight')
router.register(r'featured', FeaturedViewSet, basename='featured')
router.register(r'like', LikeViewSet, basename='like')
router.register(r'comment', CommentViewSet, basename='comment')

# User
router.register(r'user', UserView, basename='user')
router.register(r'group', GroupViewSet, basename='group')

itinerary_router = routers.NestedSimpleRouter(router, r'itinerary', lookup='itinerary')
itinerary_router.register(r'day-trip', DayTripViewSet, basename='itinerary-day-trip')
