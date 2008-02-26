from ella.core.custom_urls import dispatcher
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from ella.discussions.models import Topic
from ella.discussions.views import question, ask_question, topic

dispatcher.register(slugify(_('ask')), ask_question, model=Topic)
dispatcher.register(slugify(_('question')), question, model=Topic)
dispatcher.register_custom_detail(Topic, topic)
