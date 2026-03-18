import os
import time
import asyncio
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
import edge_tts
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips

# =============================
# CONFIG
# =============================

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "veo-3.1-fast-generate-preview"

INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

client = genai.Client(api_key=API_KEY)

# =============================
# IMAGE PATHS
# =============================

background = f"{INPUT_FOLDER}/background.png"
intro = f"{INPUT_FOLDER}/intro.png"
logo = f"{INPUT_FOLDER}/logo.png"

person = f"{INPUT_FOLDER}/person.png"
hat = f"{INPUT_FOLDER}/hat.png"
vest = f"{INPUT_FOLDER}/vest.png"
shoes = f"{INPUT_FOLDER}/shoes.png"

dung_cu = f"{INPUT_FOLDER}/dung_cu.png"
keo1 = f"{INPUT_FOLDER}/keo1.png"
keo2 = f"{INPUT_FOLDER}/keo2.png"

# =============================
# MERGE IMAGES
# =============================

def merge_images(image_list, output):

    images = [Image.open(i) for i in image_list]

    widths = [img.width for img in images]
    heights = [img.height for img in images]

    total_width = sum(widths)
    max_height = max(heights)

    new_img = Image.new("RGB",(total_width,max_height))

    x = 0
    for img in images:
        new_img.paste(img,(x,0))
        x += img.width

    new_img.save(output)

# =============================
# GENERATE SCENE
# =============================

def generate_scene(prompt, image_path, duration, output):

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    image_input = types.Image(
        image_bytes=image_bytes,
        mime_type="image/png"
    )

    operation = client.models.generate_videos(
        model=MODEL_NAME,
        prompt=prompt,
        image=image_input,
        config=types.GenerateVideosConfig(
            duration_seconds=duration,
            aspect_ratio="16:9"
        )
    )

    while not operation.done:
        print("Rendering video...")
        time.sleep(10)
        operation = client.operations.get(operation)

    video = operation.response.generated_videos[0]

    response = requests.get(
        video.video.uri,
        headers={"x-goog-api-key": API_KEY}
    )

    with open(output,"wb") as f:
        f.write(response.content)

# =============================
# BUILD REFERENCE IMAGES
# =============================

merge_images([person,hat,vest,shoes],"worker_ref.png")
merge_images([dung_cu],"tools_ref.png")
merge_images([keo1,keo2],"adhesive_ref.png")

# =============================
# SCENE 1 INTRO
# =============================

print("Scene 1")

generate_scene(
"""
Corporate intro animation showing Weber SAINT-GOBAIN brand.
Professional construction company intro.
Clean corporate background.
""",
intro,
4,
"scene1.mp4"
)

# =============================
# SCENE 2 WORKER
# =============================

print("Scene 2")

generate_scene(
"""
Vietnamese construction worker.
Must be the SAME PERSON from the reference image.
Same face identity, same helmet, vest and safety shoes.
Do not change the person.

Worker standing inside construction site preparing to work.
Realistic professional construction footage.
""",
"worker_ref.png",
4,
"scene2.mp4"
)

# =============================
# SCENE 3 TOOLS
# =============================

print("Scene 3")

generate_scene(
"""
Construction tools displayed on table.
Use the exact tools from the reference image.
Professional construction setup.
""",
"tools_ref.png",
4,
"scene3.mp4"
)

# =============================
# SCENE 4 ADHESIVE
# =============================

print("Scene 4")

generate_scene(
"""
Vietnamese construction worker mixing Weber tile adhesive.

The worker MUST be the SAME PERSON from worker reference image.
Same face identity.
Do not generate a new person.

Adhesive bags must match the reference image.
Real construction environment.
""",
"adhesive_ref.png",
4,
"scene4.mp4"
)

# =============================
# SCENE 5 LOGO
# =============================

print("Scene 5")

generate_scene(
"""
Ending screen showing Weber SAINT-GOBAIN logo.
Corporate outro.
Clean professional ending.
""",
logo,
4,
"scene5.mp4"
)

# =============================
# MERGE VIDEO
# =============================

clips = []

for i in range(1,6):
    clips.append(VideoFileClip(f"scene{i}.mp4"))

final = concatenate_videoclips(clips)

temp = "temp_video.mp4"
final.write_videofile(temp)

for c in clips:
    c.close()

# =============================
# GENERATE VOICE (SCENE BASED)
# =============================

VOICE_FILE="voice.mp3"

voice_text = """
Weber SAINT-GOBAIN
We care.

Hướng dẫn thi công bằng
Keo dán gạch.
Keo chà ron.

Trang bị bảo hộ gồm:
Nón bảo hộ.
Mắt kính.
Găng tay.
Giày bảo hộ.

Phần một:
Hướng dẫn thi công dán gạch.

Bước một:
Chuẩn bị dụng cụ.

Keo dán gạch Weber.
Bay răng cưa Weber.
Bay truyền thống.

Thước thủy sáu trăm milimet.
Thước một nghìn hai trăm milimet.

Hai thùng trộn keo.
Hai ca đong một nghìn mililit.

Máy trộn điện năm trăm vòng trên phút.

Búa cao su.
Hai miếng xốp nước.
"""

async def gen_voice():
    tts=edge_tts.Communicate(
        voice_text,
        voice="vi-VN-NamMinhNeural"
    )
    await tts.save(VOICE_FILE)

asyncio.run(gen_voice())

# =============================
# MERGE AUDIO
# =============================

video=VideoFileClip(temp)
audio=AudioFileClip(VOICE_FILE)

audio=audio.set_duration(video.duration)

final=video.set_audio(audio)

FINAL_VIDEO=f"{OUTPUT_FOLDER}/final_video.mp4"

final.write_videofile(
    FINAL_VIDEO,
    codec="libx264",
    audio_codec="aac",
    fps=video.fps
)

print("FINAL VIDEO:",FINAL_VIDEO)