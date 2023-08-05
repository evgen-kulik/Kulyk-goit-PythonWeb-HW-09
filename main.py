"""Скрапінг сайту 'http://quotes.toscrape.com/'"""


import scrapy
from itemadapter import ItemAdapter
from scrapy.crawler import CrawlerProcess
from scrapy.item import Item, Field
import json


class QuoteItem(Item):
    keywords = Field()
    author = Field()
    quote = Field()


class AuthorItem(Item):
    fullname = Field()
    date_born = Field()
    location_born = Field()
    bio = Field()


class QuotesPipline:
    """Цей клас забезпечує збирання даних у файлі в певному порядку. Тобто при
    отриманні чергового словника з даними, він буде приєднувати його у файлі
    до аналогічних словників (по ключам)"""

    quotes = []
    authors = []

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        # згрупуємо першу групу даних
        if (
            "fullname" in adapter.keys()
        ):  # використовуємо ключ 'fullname', т.я. він є унікальний для групи словників
            self.authors.append(
                {
                    "fullname": adapter["fullname"],
                    "date_born": adapter["date_born"],
                    "location_born": adapter["location_born"],
                    "bio": adapter["bio"],
                }
            )

        # згрупуємо другу групу даних
        if (
            "quote" in adapter.keys()
        ):  # використовуємо ключ 'quote', т.я. він є унікальний для групи словників
            self.quotes.append(
                {
                    "keywords": adapter["keywords"],
                    "author": adapter["author"],
                    "quote": adapter["quote"],
                }
            )
        return item

    def close_spider(self, spider):
        """Pipeline викличе цей метод після того, як закриється spider"""

        with open("quotes_scrapy.json", "w", encoding="utf-8") as fd:
            json.dump(self.quotes, fd, ensure_ascii=False)
        with open("authors_scrapy.json", "w", encoding="utf-8") as fd:
            json.dump(self.authors, fd, ensure_ascii=False)


class QuotesSpider(scrapy.Spider):
    name = "authors"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["http://quotes.toscrape.com/"]
    custom_settings = {"ITEM_PIPELINES": {QuotesPipline: 300}}

    def parse(self, response, *args):
        for quote in response.xpath("/html//div[@class='quote']"):
            keywords = quote.xpath(
                "div[@class='tags']/a/text()"
            ).extract()  # ".extract()" збирає всі елементи в список
            author = quote.xpath("span/small/text()").get().strip()
            q = (
                quote.xpath("span[@class='text']/text()").get().strip()
            )  # ".get() поверне тільки перше входження елемента"
            yield QuoteItem(keywords=keywords, author=author, quote=q)
            yield response.follow(
                url=self.start_urls[0] + quote.xpath("span/a/@href").get(),
                callback=self.nested_parse_author,
            )

        # Метод parse може повертати Request об'єкт і тоді Scrapy зробить запит і обробить його, передавши відповідь
        # у parse (тобто циклом пройдеться по всім сторінкам).
        # Посилання на наступну сторінку знаходиться під тегом li з класом next. Тоді вираз для отримання посилання
        # на наступну сторінку буде таким:
        next_link = response.xpath("//li[@class='next']/a/@href").get()
        if next_link:
            # повний шлях ми отримаємо, склавши домен і відносний шлях
            yield scrapy.Request(url=self.start_urls[0] + next_link)

    def nested_parse_author(self, response, *args):
        author = response.xpath('/html//div[@class="author-details"]')
        fullname = author.xpath('h3[@class="author-title"]/text()').get().strip()
        date_born = (
            author.xpath('p/span[@class="author-born-date"]/text()').get().strip()
        )
        location_born = (
            author.xpath('p/span[@class="author-born-location"]/text()').get().strip()
        )
        bio = author.xpath('div[@class="author-description"]/text()').get().strip()
        yield AuthorItem(
            fullname=fullname, date_born=date_born, location_born=location_born, bio=bio
        )


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(QuotesSpider)
    process.start()
