import numpy as np
from PIL import Image
import gradio as gr
import os
from datetime import datetime
import time
import cv2
from roop import core


dir_path = f'work_dirs/'
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
dir_path = f'work_dirs/temp'
if not os.path.exists(dir_path):
    os.makedirs(dir_path)


def training(img, video):
    img_tail = img.split('.')[-1]
    img_name = f'./work_dirs/img.{img_tail}'
    cmd = f'cp {img} {img_name}' 
    os.system(cmd)

    video_input = video.name
    video_tail = video_input.split('.')[-1]
    time_str = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    video_name = f'./work_dirs/{time_str}.{video_tail}'
    cmd = f'cp {video_input} {video_name}'
    os.system(cmd)

    cap = cv2.VideoCapture(video_name)

    fps = int(round(cap.get(cv2.CAP_PROP_FPS)))

    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if length > 500:
        raise gr.Error("视频太长了，搞不动一点。请减小视频长度，这只是表情包。")

    args = core.parse_args()

    args.source_path = img_name
    args.target_path = video_name
    args.output_path = f'{time_str}.mp4'
    args.keep_frames = True
    args.keep_fps = True
    args.output_video_quality = 100
    core.run(args)

    
    cmd = f'ffmpeg -y -r {fps} -i work_dirs/temp/{time_str}/%04d.png work_dirs/result.mp4'
    os.system(cmd)
    return 'work_dirs/result.mp4'


block = gr.Blocks().queue(max_size=20)
with block:
    gr.Markdown('## 表情包换脸')

    with gr.Row():
        with gr.Column():
            gr.Markdown('### 上传人像照')
            image_input = gr.Image(type="filepath", label='上传人像照', height=512)
            gr.Markdown('### 上传gif或视频')
            video = gr.File()
            video_show = gr.Video()
            example_folder = os.path.join(os.path.dirname(__file__), "./example_gifs")
            example_list = [os.path.join(example_folder, example) for example in os.listdir(example_folder)]
            example_input = []
            for example in example_list:
                example_input.append([example, example])
            gr.Examples(
                examples=example_input,
                inputs=[video, video_show],
                # outputs=[input_image],
                cache_examples=False,
                label='Examples (click one of the video below to start)',
                examples_per_page=4
            )

        with gr.Column():
            gr.Markdown('### 生成结果')
            video_out = gr.Video(label='Video Result', elem_id='video-output', height=512)
            training_button = gr.Button(value='换脸')

    training_button_inputs = [image_input, video]
    training_button_outputs = [video_out]
    training_button.click(fn=training, inputs=training_button_inputs, outputs=training_button_outputs)

block.launch(server_name='0.0.0.0', server_port=7860, share=False)

