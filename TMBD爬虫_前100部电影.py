import requests
import csv
from lxml import html
import re

# 常量
MOVIE_LIST = 'movie_list_top_100.csv'
TMBD_BASE_URL = 'https://www.themoviedb.org'
TMBD_TOP_URL = 'https://www.themoviedb.org/movie/top-rated'
TMBD_ElSE_URL = 'https://www.themoviedb.org/discover/movie/items'

# 获取电影详情
def get_movie_info(movie_info_url):
    # 发送请求，获取数据
    movie_response = requests.get(movie_info_url, timeout=60)
    print(f"发送请求{movie_info_url}")
    # 解析数据，获取详情
    movie_doc = html.fromstring(movie_response.text)
    movie_name = movie_doc.xpath("//*[@id='original_header']/div[2]/section/div[1]/h2/a/text()")#电影名
    movie_year = movie_doc.xpath("//*[@id='original_header']/div[2]/section/div[1]/h2/span/text()")#年份
    movie_date = movie_doc.xpath("//*[@id='original_header']/div[2]/section/div[1]/div/span[@class='release']/text()")#上映日期
    movie_type = movie_doc.xpath("//*[@id='original_header']/div[2]/section/div[1]/div/span[@class='genres']/a/text()")#类型
    movie_time = movie_doc.xpath("//*[@id='original_header']/div[2]/section/div[1]/div/span[@class='runtime']/text()")#时长
    movie_score = movie_doc.xpath("//*[@id='consensus_pill']/div/div[1]/div/div/@data-percent")#评分
    movie_language = movie_doc.xpath("//*[@id='media_v4']/div/div/div[2]/div/section/div[1]/div/section[1]/p[3]/text()")#语言
    movie_director = movie_doc.xpath("//*[@id='original_header']/div[2]/section/div[3]/ol/li[1]/p[1]/a/text()")#导演
    movie_author = movie_doc.xpath("//*[@id='original_header']/div[2]/section/div[3]/ol/li[2]/p[1]/a/text()")#作者
    movie_cast = movie_doc.xpath("//*[@id='cast_scroller']/ol/li[1]/p[1]/a/text()")#主演
    movie_slogan = movie_doc.xpath("//*[@id='original_header']/div[2]/section/div[3]/h3[@class='tagline']/text()")#标语
    movie_description = movie_doc.xpath("//*[@id='original_header']/div[2]/section/div[3]/div/p/text()")#描述

    movie_date = movie_date[0].strip() if movie_date else None
    movie_time = movie_time[0].strip() if movie_time else None
    hour = re.search(r'(\d+)h', movie_time) if movie_time else None
    minute = re.search(r'(\d+)m', movie_time) if movie_time else None
    hour = int(hour.group(1)) if hour else 0
    minute = int(minute.group(1)) if minute else 0
    movie_time = f"{hour * 60 + minute}m"

    movie_info = {
        '电影名': movie_name[0].strip() if movie_name else None,
        '年份': movie_year[0].strip("() ") if movie_year else None,
        '上映日期': re.search(r'\d{4}-\d{2}-\d{2}', movie_date).group() if movie_date else None,
        '类型': ','.join(movie_type) if movie_type else None,
        '时长': movie_time,
        '评分': movie_score[0].strip() if movie_score else None,
        '语言': movie_language[0].strip() if movie_language else None,
        '导演': movie_director[0].strip() if movie_director else None,
        '作者': movie_author[0].strip() if movie_author else None,
        '主演': movie_cast[0].strip() if movie_cast else None,
        '标语': movie_slogan[0].strip() if movie_slogan else None,
        '描述': movie_description[0].strip() if movie_description else None
    }
    #返回电影详情
    return movie_info

# 保存电影数据到csv中
def save_all_movies(all_movies):
    with open(MOVIE_LIST, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['电影名', '年份', '上映日期', '类型', '时长', '评分', '语言', '导演', '作者', '主演', '标语', '描述'])
        writer.writeheader()
        writer.writerows(all_movies)

def main():
    all_movies = []
    for i in range(1, 6):
        if i == 1:
            print(f"开始第{i}页请求数据")
            response = requests.get(TMBD_TOP_URL, timeout=60)
            print(response)
        else:
            print(f"开始第{i}页请求数据")
            response = requests.post(TMBD_ElSE_URL, data=f"air_date.gte=&air_date.lte=&certification=&certification_country=CN&debug=&first_air_date.gte=&first_air_date.lte=&include_adult=false&include_softcore=false&latest_ceremony.gte=&latest_ceremony.lte=&page={i}&primary_release_date.gte=&primary_release_date.lte=&region=&release_date.gte=&release_date.lte=2027-05-03&show_me=everything&sort_by=vote_average.desc&vote_average.gte=0&vote_average.lte=10&vote_count.gte=300&vote_count.lte=&watch_region=CN&with_genres=&with_keywords=&with_networks=&with_origin_country=&with_original_language=&with_watch_monetization_types=&with_watch_providers=&with_release_type=&with_runtime.gte=0&with_runtime.lte=400&view=&discover_preset=top-rated", timeout=60)
            print(response)
        # 解析数据，获取电影列表
        document = html.fromstring(response.text)
        movie_list = document.xpath("//div[contains(@class, 'media-list-results')]//div[contains(@class, 'rounded-xl')]")  # 使用了模糊匹配
        # movie_list = document.xpath("/html/body/div[2]/main/section/div/div/div/div[3]/div[2]/div/section/div/div/div[1]/div[1]/div")
        # 遍历数据，提取信息
        for movie in movie_list:
            movie_href = movie.xpath("./div/div/div/a[contains(@class,'font-normal')]/@href")
            if movie_href:
                # 电影详情页URL
                movie_info_url = TMBD_BASE_URL + movie_href[0]
                movie_info = get_movie_info(movie_info_url)
                all_movies.append(movie_info)

    # 存储数据，写入csv文件
    print("开始保存数据")
    save_all_movies(all_movies)
    print("数据保存成功")

if __name__ == '__main__':
    main()