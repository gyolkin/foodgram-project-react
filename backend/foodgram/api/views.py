from django.shortcuts import get_object_or_404
from rest_framework import (generics, mixins, permissions, status, views,
                            viewsets)
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .paginators import LimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (CreateRecipeSerializer, IngredientSerializer,
                          RecipeSerializer, SubscribeUserSerializer,
                          TagSerializer)
from .utils import create_obj, delete_obj, file_create
from content.models import Favourite, Ingredient, Recipe, ShoppingList, Tag
from core.seralizers import BasicRecipeSerializer
from users.models import Follow, User


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
    filterset_class = IngredientFilter
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
        if self.action in ('retrieve', 'list'):
            permission_classes = (permissions.AllowAny,)
        elif self.action in ('partial_update', 'destroy'):
            permission_classes = (IsAuthorOrReadOnly,)
        else:
            permission_classes = (permissions.IsAuthenticated,)
        return (permission() for permission in permission_classes)

    def create(self, request):
        create_serializer = self.get_serializer(data=request.data)
        create_serializer.is_valid(raise_exception=True)
        recipe = create_serializer.save()
        response_serializer = RecipeSerializer(
            recipe, context={'request': request}
        )
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=('POST', 'DELETE'),)
    def favorite(self, request, pk):
        if self.request.method == 'POST':
            return create_obj(request, pk, Favourite, BasicRecipeSerializer)
        return delete_obj(request, pk, Favourite)

    @action(detail=True, methods=('POST', 'DELETE'),)
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return create_obj(request, pk, ShoppingList, BasicRecipeSerializer)
        return delete_obj(request, pk, ShoppingList)

    @action(detail=False, methods=('GET',),)
    def download_shopping_cart(self, request):
        shopping_list = ShoppingList.objects.filter(user=request.user)
        if not shopping_list.exists():
            return Response(
                {'errors': 'У вас нет добавленных рецептов.'},
                status=status.HTTP_404_NOT_FOUND
            )
        recipes_ids = shopping_list.values_list('recipe_id', flat=True)
        recipes = Recipe.objects.filter(id__in=recipes_ids)
        return file_create(recipes)


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
