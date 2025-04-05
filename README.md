# CrawlWebTest

## 1. Tổng quan:
Sử dụng Scrapy để crawl tài liệu từ 2 trang nhà thuê và nhà bán và các next page bên trong mỗi trang.

Set up pipeline trong scrapy để thay vì xử lý ngay lập tức thì sẽ có 1 server khác xử lý thông qua Kafka như 1 message queue.

Server xử lý sẽ store output vào trong csv file.

Tạo 1 code làm sạch và lưu dữ liệu tổng quan vào trong Elasticsearch.

Sử dụng Agno và hình thành 1 tool truy vấn dữ liệu trong đó để phản hồi người dùng.



## 2. Set up:

Chạy các lệnh sau để khởi tạo Elasticsearch, Kafka, Zookeeper
```
docker compose up -d 
```

Cài các thư viện:
```
pip install -r requirements.txt
```

## 3. Crawl dữ liệu:

Mở 2 terminal. 1 terminal chạy:

```
cd demo_scrapy
scrapy crawl bds_spider
```

Terminal kia chạy:
```
cd consumer
python consumer.py
```
Sau khi chạy xong trong folder info sẽ tồn tại file info.csv chứa dữ liệu chưa được lọc sạch

## 4. Lọc dữ liệu và store Elasticsearch

Trong file clean_es.ipynb, em đã command 1 số tác dụng của các block để lọc dữ liệu cũng như lưu vào trong Elasticsearch

## 5. Đưa ra phản hồi cuối cùng:

Chạy file 'inference' trong inference folder
```
python inference.py
```
## 6. Demo:

GG Drive chứa file crawl từ web và đã lọc sạch:

