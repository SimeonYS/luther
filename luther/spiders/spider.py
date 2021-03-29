import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import LutherItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class LutherSpider(scrapy.Spider):
	name = 'luther'
	start_urls = ['https://www.lutherburbanksavings.com/about-us/whats-new/#tab-3']


	def parse(self, response):
		articles = response.xpath('//div[@id="tab-3"]/ul[@class="NewsList__list"]/li[@class="NewsList__item"]')
		for article in articles:
			date = article.xpath('.//span[@class="NewsList__date"]/text()').get()
			post_links = article.xpath('.//a/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

	def parse_post(self, response, date):
		title = response.xpath('//div[@class="field__item"]/text() | //h2[@style="text-align: center;"]/text()').get()
		if not title:
			title = response.xpath('//div[@class="col-sm-10 col-sm-offset-1 col-xs-12 "]/h1/text() |//div[@class="col-sm-7 col-sm-offset-1 col-vcenter col-xs-12 "]/h1/text() |//h2/text()').get()

		content = response.xpath('//div[@class="node__content"]//text() | //div[@class="typography container Page__content"]//text()[not (ancestor::h2)] | (//div[@class="col-sm-10 col-sm-offset-1"])[last()]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=LutherItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
