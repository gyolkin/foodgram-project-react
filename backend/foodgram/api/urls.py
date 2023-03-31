from django.urls import include, path
from djoser.views import TokenDestroyView, UserViewSet
from rest_framework.routers import SimpleRouter

from .views import (DownloadShoppingList, FavouriteView, IngredientViewSet,
                    LoginView, RecipeViewSet, ShoppingListView, SubscribeView,
                    SubscribitionsView, TagViewSet)

router = SimpleRouter()

router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path(
        'recipes/download_shopping_cart/',
        DownloadShoppingList.as_view(),
        name='download_shopping_cart'
    ),
    path('', include(router.urls)),
    path(
        'recipes/<int:id>/favorite/',
        FavouriteView.as_view(),
        name='favorite'
    ),
    path(
        'recipes/<int:id>/shopping_cart/',
        ShoppingListView.as_view(),
        name='shopping_cart'
    ),
    path(
        'users/',
        UserViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='user_list'
    ),
    path(
        'users/<int:id>/',
        UserViewSet.as_view({'get': 'retrieve'}),
        name='user_detail'
    ),
    path(
        'users/me/',
        UserViewSet.as_view({'get': 'me'}),
        name='user_me'
    ),
    path(
        'users/subscriptions/',
        SubscribitionsView.as_view(),
        name='subscriptions'
    ),
    path(
        'users/<int:id>/subscribe/',
        SubscribeView.as_view(),
        name='subscribe'
    ),
    path(
        'users/set_password/',
        UserViewSet.as_view({'post': 'set_password'}),
        name='user_set_password'
    ),
    path(
        'auth/token/login/',
        LoginView.as_view(),
        name='login'
    ),
    path(
        'auth/token/logout/',
        TokenDestroyView.as_view(),
        name='logout'
    ),
]
