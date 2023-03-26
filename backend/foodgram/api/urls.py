from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (DownloadShoppingList, FavouriteView,
                    IngredientViewSet, RecipeViewSet, SetPasswordView,
                    ShoppingListView, SubscribeView, SubscribitionsView,
                    TagViewSet, UserDetailView, UserListCreateView,
                    UserPersonalView, LoginView, LogoutView)

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
        UserListCreateView.as_view(),
        name='users'
    ),
    path(
        'users/<int:id>/',
        UserDetailView.as_view(),
        name='user_detail'
    ),
    path(
        'users/me/',
        UserPersonalView.as_view(),
        name='user_me'
    ),
    path(
        'users/set_password/',
        SetPasswordView.as_view(),
        name='set_password'
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
        'auth/token/login/',
        LoginView.as_view(),
        name='login'
    ),
    path(
        'auth/token/logout/',
        LogoutView.as_view(),
        name='logout'
    ),
]
