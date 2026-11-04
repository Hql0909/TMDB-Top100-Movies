# TMDB 前 100 部高分电影爬虫 🎬

> 抓取 [The Movie Database](https://www.themoviedb.org) 评分最高的 **100 部电影**,逐部进入详情页解析 12 个字段,输出为 CSV 文件。

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![requests](https://img.shields.io/badge/requests-2.31%2B-2C8EBB)
![lxml](https://img.shields.io/badge/lxml-5.0%2B-green)

---

## 📖 项目简介

一个 **94 行**的 Python 爬虫练习项目,完整走通"列表页 → 详情页 → 结构化数据"这条链路:

1. 请求 TMDB「Top Rated」榜单的 **5 个分页**(每页 20 部,共 100 部)
2. 从每部电影的**详情页**用 **XPath** 精确提取 12 个字段
3. 做简单的数据清洗(时长换算成分钟、日期用正则提取)
4. 用 `csv.DictWriter` 写入 `movie_list_top_100.csv`

适合作为 **requests + lxml + XPath** 的实战参考。

---

## ✨ 功能特性

| 特性 | 说明 |
| :--- | :--- |
| 📄 **分页抓取** | 第 1 页用 GET,第 2~5 页用 POST 调用 `discover/movie/items` 接口 |
| 🔍 **XPath 精准定位** | 每个字段单独一条 XPath 表达式,而不是粗暴地取整段文本 |
| 🧹 **基础清洗** | 时长 `2h 15m` → `135m`;上映日期用正则从 `2024-03-01 (US)` 里提出 `2024-03-01` |
| 🛡️ **空值容错** | 每个字段都做 `if xxx else None`,页面结构变化不会直接崩溃 |
| 📊 **结构化输出** | 12 列 CSV,Excel 可直接打开 |

---

## 🚀 快速开始

### 1. 获取代码

```bash
git clone https://github.com/Hql0909/TMDB-Top100-Movies.git
cd TMDB-Top100-Movies
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

> `lxml` 在 Windows 上偶尔需要编译环境,如果安装失败可以直接装预编译包:
> `pip install lxml --only-binary :all:`

### 3. 运行

```bash
python TMBD爬虫_前100部电影.py
```

终端会打印进度:

```
开始第1页请求数据
<Response [200]>
发送请求 https://www.themoviedb.org/movie/278
发送请求 https://www.themoviedb.org/movie/238
...
开始保存数据
数据保存成功
```

### 4. 查看结果

当前目录下生成 **`movie_list_top_100.csv`**,用 Excel 或 pandas 打开。

---

## 📋 输出示例

| 电影名 | 年份 | 上映日期 | 类型 | 时长 | 评分 | 语言 | 导演 | 作者 | 主演 | 标语 | 描述 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 肖申克的救赎 | 1994 | 1994-09-23 | 剧情,犯罪 | 142m | 87 | English | 弗兰克·德拉邦特 | 斯蒂芬·金 | 蒂姆·罗宾斯 | 恐惧让你沦为囚犯,希望让你重获自由 | 一场谋杀案使银行家安迪蒙冤入狱… |

> 实际内容以抓取时的页面为准。

### 字段说明

| 字段 | 来源 | 处理方式 |
| :--- | :--- | :--- |
| 电影名 | 详情页 `#original_header h2 a` | 去首尾空格 |
| 年份 | 同上 `h2 span` | 去掉括号 `(1994)` → `1994` |
| 上映日期 | `span.release` | 正则提取 `YYYY-MM-DD` |
| 类型 | `span.genres a`(多个) | 用逗号拼接 |
| 时长 | `span.runtime` | `2h 15m` → `135m` |
| 评分 | `#consensus_pill` 的 `data-percent` | 直接取值 |
| 语言 | 原始语言区块 | 去空格 |
| 导演 / 作者 | `ol li[1]` / `li[2]` | 取首个 `<a>` 文本 |
| 主演 | `#cast_scroller` 第一个 | 取首个 `<a>` 文本 |
| 标语 / 描述 | `h3.tagline` / `div p` | 去空格 |

---

## 📁 项目结构

```
TMDB-Top100-Movies/
├── TMBD爬虫_前100部电影.py   # ⭐ 主程序
├── requirements.txt          # 依赖清单
├── README.md                 # 本文件
└── .gitignore
```

运行后会在本地生成 `movie_list_top_100.csv`(已加入 `.gitignore`,不入库)。

---

## 🔧 实现思路

### 1. 分页策略

第 1 页直接 GET 榜单页;后续页 TMDB 走的是前端 XHR,所以改用 POST:

```python
if i == 1:
    response = requests.get(TMBD_TOP_URL, timeout=60)
else:
    response = requests.post(TMBD_ELSE_URL, data=f"...&page={i}&sort_by=vote_average.desc...", timeout=60)
```

> 表单里 `sort_by=vote_average.desc`、`vote_count.gte=300` 决定了"高分且有足够票数"的筛选口径。

### 2. 列表页取链接

```python
movie_list = document.xpath("//div[contains(@class, 'media-list-results')]//div[contains(@class, 'rounded-xl')]")
movie_href = movie.xpath("./div/div/div/a[contains(@class,'font-normal')]/@href")
```

用 `contains(@class, ...)` 而不是写死完整 class 名,是因为 TMDB 的 class 里常带随机后缀。

### 3. 详情页解析

每个字段一条 XPath,取到就清洗、取不到就给 `None`:

```python
movie_time = movie_time[0].strip() if movie_time else None
```

### 4. 时长归一化

```python
hour = re.search(r'(\d+)h', movie_time)
minute = re.search(r'(\d+)m', movie_time)
movie_time = f"{hour * 60 + minute}m"
```

把 `2h 15m` 统一成 `135m`,方便后续排序和统计。

---

## ⚠️ 注意事项与免责声明

- 本项目**仅供学习爬虫技术**,请勿用于商业用途。
- TMDB 的数据受其 [服务条款](https://www.themoviedb.org/documentation/api/terms-of-use) 约束,高频请求可能被封 IP。
- 建议在两次请求之间加 `time.sleep(1)`,降低服务器压力(本项目为教学简化,未加)。
- 页面结构随时可能改版,一旦 XPath 失效,字段会变成 `None` 而不会报错 —— 这是刻意设计的容错行为。

---

## ❓ 常见问题

<details>
<summary><b>抓到的字段大量是 None</b></summary>

多半是 TMDB 改版了,XPath 选择器失效。打开一部电影详情页,F12 检查对应元素,更新 `get_movie_info()` 里的表达式即可。

</details>

<details>
<summary><b>返回 403 / 429</b></summary>

请求太快被限流。在循环里加 `time.sleep(1)`,或换网络环境重试。

</details>

<details>
<summary><b>CSV 用 Excel 打开是乱码</b></summary>

文件本身是 UTF-8。Excel 需要"数据 → 从文本/CSV 导入"并选 UTF-8 编码;或者用 pandas 打开:

```python
import pandas as pd
print(pd.read_csv("movie_list_top_100.csv"))
```

</details>

<details>
<summary><b>只抓到不到 100 部</b></summary>

部分条目可能没有详情页链接(或页面结构特殊),被 `if movie_href:` 跳过了。可以打印 `len(all_movies)` 核对。

</details>

<details>
<summary><b>为什么文件名是 TMBD 不是 TMDB?</b></summary>

创建时的笔误,一直沿用未改。功能无影响。

</details>

---

## 🗺️ 后续计划

- [ ] 加入 `time.sleep` 限速与重试机制
- [ ] 支持命令行参数指定页数与输出文件名
- [ ] 增加海报图片、评分人数、预算/票房等字段
- [ ] 输出为 JSON / 写入 SQLite

---

## 📄 License

MIT
