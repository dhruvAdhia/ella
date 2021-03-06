# -*- coding: utf-8 -*-
from copy import copy
from datetime import datetime
from time import strftime

from django.utils.translation import ugettext_lazy as _

from ella.articles.models import Article

from example_project.tests.test_newman.helpers import (
    NewmanTestCase,
    DateTimeAssert,
)

class TestArticleBasics(NewmanTestCase):
    translation_language_code = 'cs'
    make_translation = True

    def test_article_saving(self):
        s = self.selenium

        # go to article adding
        s.click(self.elements['navigation']['articles'])
        s.click(self.elements['controls']['add'])

        # wait for the page to fully load
        s.wait_for_element_present(self.elements['controls']['suggester'])

        # fill the form
        data = {
            'title' : u'马 žš experiment',
            'upper_title' : u'vyšší',
            'description' : u'Article description',
            'slug' : u'title',
        }
        self.fill_fields(data)

        expected_data = copy(data)

        # fill in the suggesters
        suggest_data = {
            'category': ('we',),
            'authors':  ('Bar', 'Kin',),
            'placement_set-0-category' : ('we',)
        }
        self.fill_suggest_fields(suggest_data)

        self.fill_using_lookup({
            "authors" : u"King Albert II",
        })

        expected_data.update({
            'category' : [u"Africa/west-africa"],
            'authors' : [u"Barack Obama", u"King Albert II"],
            'placement_set-0-category' : [u"Africa/west-africa"],
        })


        calendar_data = {
            "publish_from" : {
                "day" : "1",
            },
            "publish_to" : {
                "day" : "3",
            }

        }

        self.fill_calendar_fields(calendar_data)

        # TODO: Replace fuzzy matching when it will be decided how to insert time
        expected_data.update({
            "placement_set-0-publish_from" : DateTimeAssert(datetime(
                year = int(strftime("%Y")),
                month = int(strftime("%m")),
                day = int(calendar_data['publish_from']['day']),
                hour = 0,
                minute = 0,
            )),

            "placement_set-0-publish_to" : DateTimeAssert(datetime(
                year = int(strftime("%Y")),
                month = int(strftime("%m")),
                day = int(calendar_data['publish_to']['day']),
                hour = 0,
                minute = 0,
            )),
        })

        self.save_form()

        s.wait_for_element_present(self.get_listing_object()+"/th")

        self.assert_equals(u"%s: %s" % (unicode(_(u"Article")), data['title']), s.get_text(self.get_listing_object_href()))

        # verify all fields
        s.click(self.get_listing_object_href())

        self.verify_form(expected_data)

    def test_article_search_from_articles(self):
        s = self.selenium
        search_term = 'experiment'
        search_input = "//input[@id='searchbar']"

        # go to articles
        s.click(self.elements['navigation']['articles'])
        s.wait_for_element_present(search_input)

        # write search term
        s.type('searchbar', search_term)
        s.click(self.elements['controls']['search_button'])

        # check that search input contains search term and we have 1 article
        s.wait_for_element_present(search_input)
        self.assert_equals(s.get_value("searchbar"), search_term)

