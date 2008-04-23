# --- doc tests for discussions app ---
import logging.config
from settings import *
logging.config.fileConfig(LOGGING_CONFIG_FILE)

banned_strings = r"""
>>> from ella.discussions.models import *
>>> from ella.discussions.views import *
>>> filter_banned_strings(u'A b prdel c d.')
u'A b *** c d.'

>>> filter_banned_strings(u'A b prdel c kurva d.')
u'A b *** c *** d.'

>>> filter_banned_strings(u'A b prdel c kurvaprdel d.')
u'A b *** c ****** d.'

>>> filter_banned_strings(u'A b kujvapudel d.')
u'A b kujvapudel d.'
"""


get_threads_by_date = r"""
>>> from django import template
>>> from django.template import Context, Template
>>> from ella.core.models import Category
>>> from django.contrib.contenttypes.models import ContentType
>>> from ella.discussions.models import *
>>> from ella.discussions.templatetags.discussions import *
>>> categ = Category.objects.get(pk=2)
>>> topic = Topic.objects.get(pk=1)
>>> map(lambda z: z.__unicode__(), topic.get_threads_by_date())
[u'Vlakno Three', u'Vlakno Two', u'Vlakno 0ne']
"""


get_most_active = r"""
>>> from django import template
>>> from django.template import Context, Template
>>> from ella.core.models import Category
>>> from django.contrib.contenttypes.models import ContentType
>>> from ella.discussions.models import *
>>> from ella.discussions.templatetags.discussions import *
>>> categ = Category.objects.get(pk=2)
>>> topic = Topic.objects.get(pk=1)
>>> act = topic.get_threads_by_activity()
>>> map(lambda z: z.__unicode__(), act)
[u'Vlakno Three', u'Vlakno Two', u'Vlakno One']
"""



# template tags test

most_active_tpltag = r"""
>>> tpl = '''
...   {% block container %}
...     {% load discussions %}
...     {% listing 10 of discussions.topic for category as topic_list %}
...     {% for topic in topic_list %}
...         "{{topic.target}}"
...         {% get_most_active_threads for topic as thr_topic %}
...         {% for t in thr_topic %}
...             "{{t}}"
...         {% endfor %}
...     {% endfor %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)

>>> from django import template
>>> from django.template import Context, Template
>>> from ella.core.models import Category
>>> from django.contrib.contenttypes.models import ContentType
>>> from ella.discussions.models import *
>>> from ella.discussions.templatetags.discussions import *
>>> categ = Category.objects.get(pk=2)
>>> t = Template(tpl)
>>> cx = Context({'category': categ})
>>> t.render(cx)
u'"Prvni tema""Vlakno Three""Vlakno Two""Vlakno One""Druhe tema""Vlakno Wife ;-)""Vlakno Four"'
"""


most_active_tpltag_string = r"""
>>> tpl = '''
...   {% block container %}
...     {% load discussions %}
...     {% get_most_active_threads for "prvni-tema" as thr %}
...     {% for i in thr %}
...         "{{i}}"
...     {% endfor %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)
>>> from django import template
>>> from django.template import Context, Template
>>> from ella.core.models import Category
>>> from django.contrib.contenttypes.models import ContentType
>>> from ella.discussions.models import *
>>> from ella.discussions.templatetags.discussions import *
>>> from ella.comments.models import Comment

>>> ct = ContentType.objects.get_for_model(TopicThread)
>>> thr = TopicThread.objects.get(title="Vlakno Two")
>>> c = Comment(content='new comment',subject='',ip_address='1.2.3.4', \
... target_ct=ct,target_id=thr._get_pk_val(),parent=None,user=User.objects.get(username="admin"))
>>> c.save()
>>> c = Comment(content='new comment to vlakno two #2',subject='',ip_address='1.2.3.4', \
... target_ct=ct,target_id=thr._get_pk_val(),parent=None,user=User.objects.get(username="admin"))
>>> c.save()

>>> thr = TopicThread.objects.get(title="Vlakno One")
>>> c = Comment(content='new comment to vlakno one',subject='',ip_address='1.2.3.4', \
... target_ct=ct,target_id=thr._get_pk_val(),parent=None,user=User.objects.get(username="admin"))
>>> c.save()

>>> categ = Category.objects.get(pk=2)
>>> t = Template(tpl)
>>> cx = Context({'category': categ})
>>> t.render(cx)
u'"Vlakno Two""Vlakno One""Vlakno Three"'
"""

most_active_tpltag_without_for = r"""
>>> tpl = '''
...   {% block container %}
...     {% load discussions %}
...     {% get_most_active_threads %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)
>>> from django import template
>>> from django.template import Context, Template
>>> from ella.core.models import Category
>>> from django.contrib.contenttypes.models import ContentType
>>> from ella.discussions.models import *
>>> from ella.discussions.templatetags.discussions import *

>>> ct = ContentType.objects.get_for_model(TopicThread)
>>> thr = TopicThread.objects.get(title="Vlakno Two")
>>> c = Comment(content='new comment',subject='',ip_address='1.2.3.4', \
... target_ct=ct,target_id=thr._get_pk_val(),parent=None,user=User.objects.get(username="admin"))
>>> c.save()
>>> c = Comment(content='new comment to vlakno two #2',subject='',ip_address='1.2.3.4', \
... target_ct=ct,target_id=thr._get_pk_val(),parent=None,user=User.objects.get(username="admin"))
>>> c.save()

>>> thr = TopicThread.objects.get(title="Vlakno One")
>>> c = Comment(content='new comment to vlakno one',subject='',ip_address='1.2.3.4', \
... target_ct=ct,target_id=thr._get_pk_val(),parent=None,user=User.objects.get(username="admin"))
>>> c.save()

>>> categ = Category.objects.get(pk=2)
>>> t = Template(tpl)
>>> cx = Context({'category': categ})
>>> t.render(cx)
u'[<TopicThread: Vlakno Wife ;-)>, <TopicThread: Vlakno Four>, <TopicThread: Vlakno Two>, <TopicThread: Vlakno One>, <TopicThread: Vlakno Three>]'
"""

newest_threads_tpltag = r"""
...         {% get_most_active_threads for topic as thr_topic %}
...         {% for t in thr_topic %}
...             "{{t}}"
...         {% endfor %}
>>> tpl = '''
...   {% block container %}
...     {% load discussions %}
...     {% listing 10 of discussions.topic for category as topic_list %}
...     {% for topic in topic_list %}
...         "{{topic.target}}"
...         {% get_newest_threads for topic as thr %}
...         {% for i in thr %}
...             "{{i}}"
...         {% endfor %}
...     {% endfor %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)

>>> from django import template
>>> from django.template import Context, Template
>>> from ella.core.models import Category
>>> from django.contrib.contenttypes.models import ContentType
>>> from ella.discussions.models import *
>>> from ella.discussions.templatetags.discussions import *
>>> categ = Category.objects.get(pk=2)
>>> t = Template(tpl)
>>> cx = Context({'category': categ})
>>> t.render(cx)
u'"Prvni tema""Vlakno Three""Vlakno Two""Vlakno One""Druhe tema""Vlakno Wife ;-)""Vlakno Four"'
"""

newest_threads_tpltag_string = r"""
>>> tpl = '''
...   {% block container %}
...     {% load discussions %}
...     {% get_newest_threads for "prvni-tema" as thr %}
...     {% for i in thr %}
...         "{{i}}"
...     {% endfor %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)

>>> from django import template
>>> from django.template import Context, Template
>>> from ella.core.models import Category
>>> from django.contrib.contenttypes.models import ContentType
>>> from ella.discussions.models import *
>>> from ella.discussions.templatetags.discussions import *
>>> categ = Category.objects.get(pk=2)
>>> t = Template(tpl)
>>> cx = Context({'category': categ})
>>> t.render(cx)
u'"Vlakno Three""Vlakno Two""Vlakno One"'
"""

filled_threads_tpltag_string = r"""
>>> tpl = '''
...   {% block container %}
...     {% load discussions %}
...     {% get_most_filled_threads for "druhe-tema" as thr %}
...     {% for i in thr %}
...         "{{i}}"
...     {% endfor %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)

>>> from django import template
>>> from django.template import Context, Template
>>> from ella.core.models import Category
>>> from django.contrib.contenttypes.models import ContentType
>>> from ella.discussions.models import *
>>> from ella.discussions.templatetags.discussions import *
>>> categ = Category.objects.get(pk=2)
>>> t = Template(tpl)
>>> cx = Context({'category': categ})
>>> t.render(cx)
u'"Vlakno Wife ;-)""Vlakno Four"'
"""

__test__ = {
    'discussions_filter_banned_strings': banned_strings,
    'discussions_most_active': get_threads_by_date,
    'discussions_most_active': get_most_active,
    'discussions_most_active_template_tag': most_active_tpltag,
    'discussions_most_active_template_tag_string': most_active_tpltag_string,
    'disucssions_most_active_template_tag_without_for': most_active_tpltag_without_for,
    'discussions_newest_threads_template_tag': newest_threads_tpltag,
    'discussions_newest_threads_template_tag_string': newest_threads_tpltag_string,
    'discussions_filled_threads_template_tag_string': filled_threads_tpltag_string,
}
