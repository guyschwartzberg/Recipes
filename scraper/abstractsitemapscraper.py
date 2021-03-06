from datetime import datetime
from scrapy.spiders import SitemapSpider
from scrapy.exceptions import CloseSpider
from scraper.recipescraper import scrape_me
from scraper._utils import insert_to_es
from dateutil import parser


class FilteredSitemapSpider(SitemapSpider):
    i = 0
    name = "FilteredSitemapSpider"
    # if init = 1 - do the initial data acquisition, otherwise do the periodic data acquisition

    def __init__(self, *args, **kwargs):
        if kwargs:
            self.sitemap_urls = kwargs.get('sitemap_urls')

            self.sitemap_rules = kwargs.get('sitemap_rules')

            self.allowed_domains = kwargs.get('allowed_domains')

            self.es = kwargs.get('es')
            self.client = kwargs.get('client')
            self.num = kwargs.get('num')
            self.sitename = kwargs.get('sitename')
            self.init = kwargs.get('init')
            self.name = "FilteredSitemapSpider" + kwargs.get('sitename')
            super(FilteredSitemapSpider, self).__init__(*args, **kwargs)

    def sitemap_filter(self, entries):
        for entry in entries:
            try:
                if not self.init:
                    date_time = parser.parse(entry['lastmod'], ignoretz=True)
                    time_difference = datetime.now() - date_time
                    if time_difference.days <= 7:
                        yield entry
                else:
                    yield entry
            except KeyError:
                pass

    def parse_recipes(self, response):
        try:
            if self.num == 0 or self.i <= self.num:
                self.i += insert_to_es(self.es, self.client, scrape_me(response.url, response.body), self.sitename)
            else:
                raise CloseSpider('Crawled enough pages')
        except ValueError:
            pass
