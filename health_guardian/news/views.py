from django.shortcuts import render
from health_guardian.settings import NEWS_API
from newsapi import NewsApiClient

# Create your views here.
def newsFeeds(request):
    newsapi = NewsApiClient(api_key=NEWS_API)



    top_headlines = newsapi.get_top_headlines(category='health',
                                          language='en',
                                          country='us')
    articles = top_headlines['articles']
    
    news_list = []
    article_title = []
    article_author = []
    article_img = []
    article_desc = []
    article_url = []
    article_date = []
    for i in range(len(articles)):
        element = articles[i]
        if element['title'] != "[Removed]" and element['description'] != None:
            article_title.append(element['title'])
            article_author.append(element['author'])
            article_img.append(element['urlToImage'])
            article_desc.append(element['description'])
            article_url.append(element['url'])
            article_date.append(element['publishedAt'])

            news_list = zip(article_title, article_author, article_img, article_desc, article_url, article_date)

    return render(request, "news.html", {'articles' : news_list})
