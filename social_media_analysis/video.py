import cv2
import torch
from facenet_pytorch import InceptionResnetV1
from torchvision import transforms
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from PIL import Image
import numpy as np
import os
from pytube import YouTube

# Загрузка модели для анализа выражений лиц
emotion_model = InceptionResnetV1(pretrained='vggface2').eval()

# Функция для анализа эмоций на лице
def analyze_emotion(frame):
    preprocess = transforms.Compose([
        transforms.Resize((160, 160)),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    ])
    
    frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    input_tensor = preprocess(frame).unsqueeze(0)
    
    with torch.no_grad():
        embeddings = emotion_model(input_tensor)
    
    # Эмбеддинги можно использовать для классификации эмоций с помощью линейного классификатора
    # Это упрощенная версия; можно применить предварительно обученные классификаторы эмоций
    emotion_score = embeddings.mean().item()  # Условный показатель эмоций
    return emotion_score  # Положительное значение может означать положительные эмоции

# Функция для сегментации видео на сцены
def split_video_into_scenes(video_path):
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector())
    video_manager.set_downscale_factor()  # Настройка разрешения

    video_manager.start()
    scene_manager.detect_scenes(video_manager)
    scenes = scene_manager.get_scene_list()
    return scenes

# Основная функция обработки видео
def process_video(video_path):
    # Сегментация видео на сцены
    scenes = split_video_into_scenes(video_path)
    print(f'Найдено сцен: {len(scenes)}')

    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    for scene in scenes:
        start_frame, end_frame = scene[0].get_frames(), scene[1].get_frames()
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        emotions = []
        
        for frame_no in range(start_frame, end_frame):
            ret, frame = cap.read()
            if not ret:
                break

            # Извлечение и анализ эмоций на кадре
            emotion_score = analyze_emotion(frame)
            emotions.append(emotion_score)
            
            # Отображение результата (опционально)
            cv2.imshow("Frame", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Анализ эмоций по сценам
        avg_emotion_score = np.mean(emotions) if emotions else 0
        print(f'Сцена {scenes.index(scene) + 1}: Средний показатель эмоций: {avg_emotion_score}')

    cap.release()
    cv2.destroyAllWindows()

# Функция для скачивания видео с YouTube
def download_youtube_video(url, output_path='videos'):
    yt = YouTube(url)
    stream = yt.streams.filter(file_extension='mp4').get_highest_resolution()
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    video_path = stream.download(output_path=output_path)
    print(f'Видео скачано по пути: {video_path}')
    return video_path

# Пример использования
if __name__ == '__main__':
    youtube_url = 'https://www.youtube.com/watch?v=lQBmZBJCYcY'  # Укажите ссылку на видео
    video_path = download_youtube_video(youtube_url)

    # Вызов функции анализа видео
    process_video(video_path)

    # Удаление видео после анализа
    if os.path.exists(video_path):
        os.remove(video_path)
        print(f'Видео удалено: {video_path}')
