from django.contrib import admin

from tagging.models import TaggingInlineOptions

from ella.ellaadmin import widgets
from ella.core.admin import ListingInlineOptions, HitCountInlineOptions
from ella.interviews.models import Interview, Question, Interviewee, Answer


class AnswerInlineOptions(admin.TabularInline):
    model = Answer
    extra = 2

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'content':
            kwargs['widget'] = widgets.RichTextAreaWidget
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)

class QuestionOptions(admin.ModelAdmin):
    list_display = ('interview', 'author', 'submit_date', 'answered',)
    list_filter = ('submit_date',)
    search_fields = ('content', 'nickname', 'email',)
    inlines = (AnswerInlineOptions,)

class IntervieweeOptions(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'author',)
    search_fields = ('user__first_name', 'user__last_name', 'name', 'description', 'slug', 'author__name',)
    prepopulated_fields = {'slug' : ('name',)}

class InterviewOptions(admin.ModelAdmin):
    list_display = ('title', 'category', 'ask_from', 'full_url',)
    list_filter = ('category__site', 'ask_from', 'category', 'authors',)
    date_hierarchy = 'ask_from'
    raw_id_fields = ('photo', 'interviewees',)
    search_fields = ('title', 'perex',)
    prepopulated_fields = {'slug' : ('title',)}
#    inlines = (ListingInlineOptions, TaggingInlineOptions, HitCountInlineOptions)
    inlines = (ListingInlineOptions, TaggingInlineOptions,)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ('perex', 'content'):
            kwargs['widget'] = widgets.RichTextAreaWidget
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)


admin.site.register(Interviewee, IntervieweeOptions)
admin.site.register(Interview, InterviewOptions)
admin.site.register(Question, QuestionOptions)
