from django.contrib import admin
from django.utils.html import format_html

from .models import Book, Scene


class SceneInline(admin.TabularInline):
    model = Scene
    fields = ('order', 'title', 'prefab_key', 'glb_model', 'current_glb_model', 'qr_code', 'qr_preview')
    readonly_fields = ('current_glb_model', 'qr_code', 'qr_preview')
    extra = 1

    def current_glb_model(self, obj):
        if obj.glb_model:
            return obj.glb_model.name.rsplit('/', 1)[-1]
        return '-'

    def qr_preview(self, obj):
        if obj.qr_image:
            return format_html('<img src="{}" style="width:96px;height:96px;" />', obj.qr_image.url)
        return '-'


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'updated_at')
    list_filter = ('is_published',)
    search_fields = ('title', 'description')
    inlines = [SceneInline]


@admin.register(Scene)
class SceneAdmin(admin.ModelAdmin):
    list_display = ('book', 'order', 'title', 'prefab_key', 'current_glb_model', 'has_glb_model', 'qr_code', 'qr_preview')
    list_filter = ('book__is_published', 'book')
    search_fields = ('book__title', 'title', 'text', 'prefab_key', 'qr_code', 'glb_model')
    readonly_fields = ('current_glb_model', 'qr_preview')

    def current_glb_model(self, obj):
        if obj.glb_model:
            return obj.glb_model.name.rsplit('/', 1)[-1]
        return '-'

    current_glb_model.short_description = 'Modelo actual'

    def has_glb_model(self, obj):
        return bool(obj.glb_model)

    has_glb_model.boolean = True
    has_glb_model.short_description = 'GLB'

    def qr_preview(self, obj):
        if obj.qr_image:
            return format_html('<img src="{}" style="width:160px;height:160px;" />', obj.qr_image.url)
        return '-'
