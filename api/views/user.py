import logging

from django.contrib.auth.models import Group
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from api.group_permissions import AdminPermission, IsUserSelf
from api.models import User
from api.serializers.user import UserSerializer, UserUpdateSerializer, GroupSerializer, TokenObtainPairPatchedSerializer

logger = logging.getLogger(__name__)


class TokenObtainPairPatchedView(TokenObtainPairView):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    serializer_class = TokenObtainPairPatchedSerializer

    token_obtain_pair = TokenObtainPairView.as_view()


class UserView(viewsets.ViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    serializer_update_class = UserUpdateSerializer

    def dispatch(self, request, *args, **kwargs):
        return super(UserView, self).dispatch(request, *args, **kwargs)

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
        user = get_object_or_404(self.queryset.all(), pk=pk)
        serializer = self.serializer_class(user)
        return Response(serializer.data)

    def update(self, request, pk=None):
        serializer = self.serializer_update_class(self.queryset.get(user_id=pk), data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        else:
            logger.error(serializer.errors)

        return Response(serializer.data)

    def destroy(self, request, pk=None):
        user = get_object_or_404(self.queryset.all(), pk=pk)
        user.is_active = False
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = [AllowAny]
        elif self.action == 'list':
            permission_classes = [AdminPermission]
        else:
            permission_classes = [IsAuthenticated, IsUserSelf]
        return [permission() for permission in permission_classes]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    permission_classes = [IsAdminUser]

    def dispatch(self, request, *args, **kwargs):
        return super(GroupViewSet, self).dispatch(request, *args, **kwargs)

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
