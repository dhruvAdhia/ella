from django.contrib import admin

from ella.ellaadmin.options import EllaAdminOptionsMixin

from ella.attachments.models import Attachment, Type


class AttachmentOptions(EllaAdminOptionsMixin, admin.ModelAdmin):
    list_display = ('name', 'type', 'created',)
    list_filter = ('type',)
    prepopulated_fields = {'slug' : ('name',)}
    rich_text_fields = {'small': ('description',)}
    raw_id_fields = ('photo',)

admin.site.register(Attachment, AttachmentOptions)
admin.site.register(Type)

