from django.db import models, transaction
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site

from ella.core.cache import get_cached_object


class DbTemplate(models.Model):
    name = models.CharField(_('Name'), maxlength=200, db_index=True)
    site = models.ForeignKey(Site)
    description = models.CharField(_('Description'), maxlength=500, blank=True)
    extends = models.CharField(_('Base template'), maxlength=200)

    text = models.TextField(_('Definition'), editable=False)
    def get_text(self):
        text = u'{%% extends "%s" %%}' % self.extends
        for block in self.templateblock_set.all():
            text += '{%% block %s %%}' % block.name
            if block.box_type and block.target:
                text += '{%% box %s for %s.%s with id %s %%}' % (
                        block.box_type,
                        block.target_ct.app_label,
                        block.target_ct.model,
                        block.target_id
)
            text += block.text + '\n'
            if block.box_type and block.target:
                text += '{% endbox %}'
            text += '{% endblock %}'
        return text


    objects = CurrentSiteManager()
    class Meta:
        ordering = ('name',)

    def save(self):
        self.text = self.get_text()
        super(DbTemplate, self).save()


class TemplateBlock(models.Model):
    template = models.ForeignKey(DbTemplate)
    name = models.CharField(_('Name'), maxlength=200)
    box_type = models.CharField(_('Box type'), maxlength=200, blank=True)
    target_ct = models.ForeignKey(ContentType, null=True, blank=True)
    target_id = models.IntegerField(null=True, blank=True)

    text = models.TextField(_('Definition'), blank=True, editable=False)

    @property
    def target(self):
        if not self.target_id or not self.target_ct:
            return None
        if not hasattr(self, '_target'):
            self._target = get_cached_object(self.target_ct, pk=self.target_id)
        return self._target

    @transaction.commit_on_success
    def save(self):
        super(TemplateBlock, self).save()
        # regenerate the full text
        self.template.save()

    class Meta:
        verbose_name = _('Teplate block')
        verbose_name_plural = _('Teplate blocks')
        unique_together = (('template', 'name',),)


class TemplateBlockInlineOptions(admin.TabularInline):
    pass
class DbTemplateOptions(admin.ModelAdmin):
    inlines = (TemplateBlockInlineOptions(
                    TemplateBlock,
                    extra=3,
#                    raw_id_fields=('target_ct'),
#                    fields=('', {'fields': ('name', 'box_type'),})
),
)

admin.site.register(DbTemplate, DbTemplateOptions)