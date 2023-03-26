from django.shortcuts import get_object_or_404
from rest_framework import (generics, mixins, permissions, status, views,
                            viewsets)
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from content.models import Favourite, Ingredient, Recipe, ShoppingList, Tag
from core.seralizers import BasicRecipeSerializer
from users.models import Follow, User
from .filters import RecipeFilter
from .paginators import LimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (CreateRecipeSerializer, CustomTokenSerializer,
                          IngredientSerializer, RecipeSerializer,
                          SetPasswordSerializer, SubscribeUserSerializer,
                          TagSerializer, UserSerializer)
from .utils import file_create, get_user_from_access_token


class LoginView(views.APIView):
    """Представление для получения токена авторизации пользователем."""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = CustomTokenSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            return Response({
                'auth_token': str(refresh.access_token),
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(views.APIView):
    """Представление для внесения refresh-токена в черный список."""
    def post(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header is None:
            return Response(
                {'errors': 'Авторизационные данные не предоставлены.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        auth_type, access_token = auth_header.split(' ')
        if auth_type != 'Bearer':
            return Response(
                {'errors': 'Некорректный тип токена.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = get_user_from_access_token(access_token)
        if user is None:
            return Response(
                {'errors': 'Неправильный ACCESS TOKEN.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        refresh_token = RefreshToken.for_user(user)
        refresh_token.blacklist()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """Представление для получения списка или конкретного тега."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """Представление для получения списка или конкретного ингредиента."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление для работы с рецептами."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPagination
    filterset_class = RecipeFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return CreateRecipeSerializer
        return RecipeSerializer

    def get_permissions(self):
        if self.action == 'retrieve':
            permission_classes = (permissions.AllowAny,)
        elif self.action in ('partial_update', 'destroy'):
            permission_classes = (IsAuthorOrReadOnly,)
        else:
            permission_classes = (permissions.IsAuthenticated,)
        return (permission() for permission in permission_classes)


class UserListCreateView(generics.ListCreateAPIView):
    """Представление для получения списка пользователей или создания нового."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = PageNumberPagination

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response_data = serializer.data.copy()
            response_data.pop('is_subscribed', None)
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(views.APIView):
    """Представление для получения данных пользователя по id."""

    def get(self, request, id):
        user = get_object_or_404(User, id=id)
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserPersonalView(views.APIView):
    """Представление для получения данных авторизованного пользователя."""

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class SetPasswordView(views.APIView):
    """Представление для изменения пароля."""

    def post(self, request):
        serializer = SetPasswordSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscribitionsView(generics.ListAPIView):
    """Представление для получения списка подписок пользователя."""
    serializer_class = SubscribeUserSerializer
    pagination_class = LimitPagination

    def get_queryset(self):
        following_ids = Follow.objects.filter(
            user=self.request.user).values_list('following')
        return User.objects.filter(id__in=following_ids)


class SubscribeView(views.APIView):
    """Представление для подписки или отписки от указанного пользователя."""

    def post(self, request, id):
        user = get_object_or_404(User, id=id)
        if request.user == user:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        _, created = Follow.objects.get_or_create(
            user=request.user, following=user
        )
        if not created:
            return Response(
                {'errors': 'Вы уже подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = SubscribeUserSerializer(
            user, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = get_object_or_404(User, id=id)
        follow = Follow.objects.filter(
            user=request.user, following=user).first()
        if not follow:
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavouriteView(views.APIView):
    """Представление для добавления рецепта в избранное."""

    def post(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        _, created = Favourite.objects.get_or_create(
            user=request.user, recipe=recipe
        )
        if not created:
            return Response(
                {'errors': 'Вы уже добавили этот рецепт.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = BasicRecipeSerializer(
            recipe, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        favourite = Favourite.objects.filter(
            user=request.user, recipe=recipe).first()
        if not favourite:
            return Response(
                {'errors': 'У вас нет этого рецепта в избранных.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        favourite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingListView(views.APIView):
    """Представление для редактирования шоппинг-листа."""

    def post(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        shopping_list, _ = ShoppingList.objects.get_or_create(
            user=request.user
        )
        if shopping_list.recipes.filter(id=id).exists():
            return Response(
                {'errors': 'Вы уже добавили этот рецепт.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        shopping_list.recipes.add(recipe)
        shopping_list.save()
        serializer = BasicRecipeSerializer(
            recipe, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        shopping_list = ShoppingList.objects.filter(
            user=request.user, recipes=recipe).first()
        if not shopping_list:
            return Response(
                {'errors': 'У вас нет этого рецепта в списке покупок.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        shopping_list.recipes.remove(recipe)
        shopping_list.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingList(views.APIView):
    """Представление для скачивания шоппинг-листа."""

    def get(self, request):
        shopping_list = get_object_or_404(ShoppingList, user=request.user)
        recipes = shopping_list.recipes.all()
        return file_create(recipes)
