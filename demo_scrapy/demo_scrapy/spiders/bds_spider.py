import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy import Request
# from pandas import pd
import scrapy
from scrapy.http import Request
from scrapy.downloadermiddlewares.retry import get_retry_request
import scrapy
from scrapy.http import Request
import time

HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }

class CrawlerItem(scrapy.Item):
    price = scrapy.Field()
    s = scrapy.Field()
    position = scrapy.Field()
    types = scrapy.Field()
    benefit = scrapy.Field()

class BdsSpiderSpider(scrapy.Spider):
    name = "bds_spider"
    list_check = ["ban-can-ho-chung-cu?cIds=650,362,41,325,163,575,361,40,283,44,562,45,48"
                  , "cho-thue-can-ho-chung-cu?cIds=651,52,577,51,57,576,50,55,53,59"
                  
    ]
    # , "ban-nha-dat", "ban-trang-trai-khu-nghi-duong", "ban-kho-nha-xuong", "ban-loai-bat-dong-san-khac" 
# "cho-thue-can-ho-chung-cu", "cho-thue-nha-rieng","cho-thue-nha-biet-thu-lien-ke", "cho-thue-nha-mat-pho","cho-thue-kho-nha-xuong-dat"]
    allowed_domains = ['batdongsan.com.vn']
    start_urls = list(map(lambda x: f"https://batdongsan.com.vn/{x}", list_check))

    custom_settings = {
        'BOT_NAME' : 'bds_spider',
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
            'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,
        },
        'FAKEUSERAGENT_PROVIDERS': [
            'scrapy_fake_useragent.providers.FakeUserAgentProvider',
            'scrapy_fake_useragent.providers.FakerProvider',
            'scrapy_fake_useragent.providers.FixedUserAgentProvider',
        ],
        'FEED_EXPORT_ENCODING': 'utf-8',
        'ROBOTSTXT_OBEY': True,
        'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
        'TELNETCONSOLE_ENABLED': False,
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
    }
    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, headers=HEADERS, callback=self.parse)

    def parse(self, response):
        print("Response URL:", response.url)

        titles = response.css('a.js__product-link-for-product-id::attr(href)').getall()
        for title in titles:
            if not title:
                continue
            title = response.urljoin(title)  # Convert relative URL to absolute URL
            self.logger.info(f"Following link: {title}")
            yield response.follow(title, headers=  HEADERS, callback=self.parse_item)

        next_page_button = response.css('a.re__pagination-icon')

        for button in next_page_button:
            icon_class = button.css('i::attr(class)').get()  # Get the class of the <i> tag
            if 're__icon-chevron-right--sm' in icon_class:  # Check if this is the "next" button
                next_page_url = button.attrib['href']
                if next_page_url == "/ban-can-ho-chung-cu/p100?cIds=650,362,41,325,163,575,361,40,283,44,562,45,48" \
                            or next_page_url == "/cho-thue-can-ho-chung-cu/p100?cIds=651,52,577,51,57,576,50,55,53,59":
                    continue
                next_page_url = response.urljoin(next_page_url)  # Convert relative URL to absolute URL
                self.logger.info(f"Following next page: {next_page_url}")
                yield response.follow(next_page_url, headers=  HEADERS, callback=self.parse)
                break 
            
    def parse_item(self, response):
        # Extract the item details
        price = response.xpath(
        '//div[contains(@class, "re__pr-short-info-item") and .//span[text()="Mức giá"]]//span[@class="value"]/text()'
    ).get()
        area = response.xpath(
        '//div[contains(@class, "re__pr-short-info-item") and .//span[text()="Diện tích"]]//span[@class="value"]/text()'
    ).get()
        address = response.xpath('//span[contains(@class, "js__pr-address")]/text()').get()
        titles = response.xpath('//div[contains(@class, "re__pr-specs-content-item")]//span[@class="re__pr-specs-content-item-title"]/text()').getall()
        values = response.xpath('//div[contains(@class, "re__pr-specs-content-item")]//span[@class="re__pr-specs-content-item-value"]/text()').getall()

        # Format the content as required
        benefit = ' - '.join([f"{title.strip()}: {value.strip()}" for title, value in zip(titles, values)])
        types = '-'.join(response.xpath('//div[contains(@class, "re__breadcrumb")]//a/text()').getall())

        # Create an item instance and populate it with the extracted data
        item = CrawlerItem()
        item['price'] = price.strip() if price else None
        item['s'] = area.strip() if area else None 
        item['position'] = address.strip() if address else None
        item['types'] = types.strip() if types else None
        item['benefit'] = benefit.strip() if benefit else None
        yield item
        