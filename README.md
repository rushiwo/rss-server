# 北洋园pt 免费种子rss
----
## 要求
1. python3
2. flask
3. BeautifuSoup
4. requests
5. lxml
6. pytz
## 使用方法1
1. 修改`server.py`里的passkey、username、password、url
2. `python server.py`（直接执行，可能会异常退出）
3. 用`supervisor`管理（推荐）
rss地址：http://yourip:5000/rss

## 使用方法2

nginx + gunicorn 


