import re
from django.shortcuts import render
from googleapiclient.discovery import build
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import praw
from transformers import pipeline
from PIL import Image
import requests
from io import BytesIO
import vk_api

# Убедитесь, что VADER загружен
nltk.download('vader_lexicon')

# Настройка VK API
vk_session = vk_api.VkApi(token='3167edc73167edc73167edc7ed32455baf331673167edc7565fb70621ac932820d87898')  # Замените на ваш токен
vk = vk_session.get_api()

# Настройка Reddit API
reddit = praw.Reddit(
    client_id='B2Gcc5A3cWdUvBZ6oWvetg',
    client_secret='nf3SO5phIQ5s200LXkmb4v7hdvyhbA',
    user_agent='social_media_analysis/1.0 by /u/Happy_Cow_9698 ')

# Настройка YouTube API
API_KEY = 'AIzaSyCATDA40htAs7Q-FWAA6D0ivY7MavJ02C4' # Замените на ваш ключ API
youtube = build('youtube', 'v3', developerKey=API_KEY)


def get_video_details(video_id):
    video_response = youtube.videos().list(
        part='snippet',
        id=video_id
    ).execute()
    return video_response['items'][0]['snippet']


def get_vk_post_image(post_id):
    try:
        post_data = vk.wall.getById(posts=post_id)
        print(f"Полученные данные поста: {post_data}")  # Отладка
        if 'attachments' in post_data[0]:
            for attachment in post_data[0]['attachments']:
                if attachment['type'] == 'photo':
                    image_url = attachment['photo']['sizes'][-1]['url']
                    return image_url
        else:
            print("В посте нет вложений.")  # Отладка
    except vk_api.exceptions.ApiError as e:
        print(f"Ошибка API VK: {e}")
    except Exception as e:
        print(f"Ошибка при получении изображения поста ВКонтакте: {e}")
    return None


def analyze_image_sentiment(image_url):
    try:
        # Загрузить изображение
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))

        # Используем предобученную модель для анализа настроения изображения
        vision_model = pipeline("image-classification", model="google/vit-base-patch16-224")
        result = vision_model(img)

        # Пример обработки результата
        sentiment_score = result[0]['score']  # Здесь можно адаптировать логику
        return sentiment_score
    except Exception as e:
        print(f"Ошибка анализа изображения: {e}")
        return None


def analyze_vk_view(request):
    if request.method == 'POST':
        vk_url = request.POST.get('vk_url')
        print(f"Полученный URL: {vk_url}")  # Отладка

        vk_results = []

        if vk_url:
            # Извлечение ID поста
            post_id = vk_url.split('wall')[-1]
            print(f"Извлеченный ID поста: {post_id}")  # Отладка

            image_url = get_vk_post_image(post_id)
            if image_url:
                image_sentiment = analyze_image_sentiment(image_url)
                vk_results.append({
                    'image_url': image_url,
                    'image_sentiment': image_sentiment,
                    'url': vk_url
                })
            else:
                print("Не удалось получить URL изображения.")  # Отладка

        if not vk_results:
            print("Результаты анализа для ВКонтакте не найдены.")  # Отладка

        return render(request, 'analysis/vk_results.html', {'vk_results': vk_results})

    return render(request, 'analysis/analyze_vk.html')


def get_video_comments(video_id):
    comments = []
    response = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        textFormat='plainText'
    ).execute()

    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
        comments.append(comment)

    return comments


def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(text)['compound']
    return score


def analyze_view(request):
    if request.method == 'POST':
        reddit_url = request.POST.get('reddit_url')
        youtube_url = request.POST.get('youtube_url')
        vk_url = request.POST.get('vk_url')

        reddit_results = []
        youtube_results = []
        vk_results = []

        # Анализ Reddit
        if reddit_url:
            url_parts = reddit_url.split('/')
            post_id = url_parts[-3]

            try:
                submission = reddit.submission(id=post_id)
                sentiment = analyze_sentiment(submission.title)

                result = {
                    'title': submission.title,
                    'sentiment': sentiment,
                    'url': submission.url
                }

                if submission.url.endswith(('.jpg', '.png')):
                    image_sentiment = analyze_image_sentiment(submission.url)
                    result['image_sentiment'] = image_sentiment

                reddit_results.append(result)

                submission.comments.replace_more(limit=0)
                for comment in submission.comments.list():
                    comment_sentiment = analyze_sentiment(comment.body)
                    reddit_results.append({
                        'title': comment.body,
                        'sentiment': comment_sentiment,
                        'url': reddit_url
                    })

            except Exception as e:
                print(f"Ошибка при получении данных из Reddit: {e}")

        # Анализ YouTube
        if youtube_url:
            video_id = re.search(r'(?<=v=)[^&]+', youtube_url) or re.search(r'(?<=be/)[^&]+', youtube_url)
            if video_id:
                video_id = video_id.group(0)

                video_details = get_video_details(video_id)
                video_description = video_details['description']
                description_sentiment = analyze_sentiment(video_description)

                comments = get_video_comments(video_id)
                comments_sentiment = [analyze_sentiment(comment) for comment in comments]

                youtube_results.append({
                    'title': video_details['title'],
                    'description': video_description,
                    'description_sentiment': description_sentiment,
                    'comments_sentiment': comments_sentiment,
                    'url': youtube_url
                })

        # Анализ VK
        if vk_url:
            post_id = vk_url.split('wall')[-1]
            image_url = get_vk_post_image(post_id)
            if image_url:
                image_sentiment = analyze_image_sentiment(image_url)
                vk_results.append({
                    'image_url': image_url,
                    'image_sentiment': image_sentiment,
                    'url': vk_url
                })
            else:
                print("Не удалось получить данные поста ВКонтакте.")  # Отладка

        return render(request, 'analysis/result.html', {
            'reddit_results': reddit_results,
            'youtube_results': youtube_results,
            'vk_results': vk_results
        })

    return render(request, 'analysis/analyze.html')
