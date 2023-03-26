from django.contrib import admin

from .models import Recipe, Tag, Ingredient, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'text', 'image', 'cooking_time',
                    'author', 'pub_date',)
    search_fields = ('name',)
    list_filter = ('cooking_time',)
    empty_value_display = '-empty-'
    inlines = (RecipeIngredientInline,)


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('title', 'hex_code')
    empty_value_display = '-empty-'


class IngedientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)
    empty_value_display = '-empty-'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngedientAdmin)
