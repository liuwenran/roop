import numpy as np
from PIL import Image
import gradio as gr
import os
from datetime import datetime
import time
import cv2


def training(img, video):
    img_tail = img.split('.')[-1]
    img_name = f'./work_dirs/img.{img_tail}'
    cmd = f'mv {img} {img_name}' 
    os.system(cmd)

    video_input = video.name
    video_tail = video_input.split('.')[-1]
    time_str = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    video_name = f'./work_dirs/{time_str}.{video_tail}'
    cmd = f'mv {video_input} {video_name}'
    os.system(cmd)

    cap = cv2.VideoCapture(video_name)

    fps = int(round(cap.get(cv2.CAP_PROP_FPS)))

    cmd = f'python run.py -s {img_name} -t {video_name} -o "{time_str}.mp4" --keep-frames --keep-fps --output-video-quality 100'

    print(cmd)
    os.system(cmd)

    while True:
        file_path = f'{time_str}.mp4'
        time.sleep(1)
        if os.path.exists(file_path):
            break
    
    cmd = f'ffmpeg -y -r {fps} -i work_dirs/temp/{time_str}/%04d.png work_dirs/result.mp4'
    os.system(cmd)
    return 'work_dirs/result.mp4'


block = gr.Blocks().queue()
with block:
    gr.Markdown('## 表情包换脸')

    with gr.Row():
        with gr.Column():
            gr.Markdown('### 上传人像照')
            image_input = gr.Image(type="filepath", label='上传人像照')
            gr.Markdown('### 上传gif或视频')
            video = gr.File()

        with gr.Column():
            training_button = gr.Button(value='换脸')
            video_out = gr.Video(label='Video Result', elem_id='video-output')

    training_button_inputs = [image_input, video]
    training_button_outputs = [video_out]
    training_button.click(fn=training, inputs=training_button_inputs, outputs=training_button_outputs)

block.launch(server_name='0.0.0.0', server_port=8122, share=False)

