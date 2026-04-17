import os
import time
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types
from moviepy.editor import VideoFileClip, concatenate_videoclips

# =============================
# CONFIG
# =============================
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "veo-3.0-fast-generate-001"

INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

client = genai.Client(api_key=API_KEY)

# =============================
# IMAGE PATHS
# =============================
person = f"{INPUT_FOLDER}/worker_ref.png"
dung_cu = f"{INPUT_FOLDER}/dung_cu.png"
background = f"{INPUT_FOLDER}/background.png"
wall = f"{INPUT_FOLDER}/wall.png"
color_background = f"{INPUT_FOLDER}/brown_bg.png"

# # =============================
# # FORCE 16:9 FUNCTION
# # =============================
# def to_16_9(clip, target_width=1920, target_height=1080):
#     target_ratio = target_width / target_height
#     clip_ratio = clip.w / clip.h

#     if clip_ratio > target_ratio:
#         new_width = int(clip.h * target_ratio)
#         clip = clip.crop(x_center=clip.w / 2, width=new_width)
#     else:
#         new_height = int(clip.w / target_ratio)
#         clip = clip.crop(y_center=clip.h / 2, height=new_height)

#     return clip.resize((target_width, target_height))

# # =============================
# # GENERATE SCENE FUNCTION
# # =============================
# def generate_scene(prompt, image_path, duration, output):
#     with open(image_path, "rb") as f:
#         image_bytes = f.read()

#     image_input = types.Image(image_bytes=image_bytes, mime_type="image/png")

#     operation = client.models.generate_videos(
#         model=MODEL_NAME,
#         prompt=prompt,
#         image=image_input,
#         config=types.GenerateVideosConfig(
#             duration_seconds=duration,
#             aspect_ratio="16:9"
#         )
#     )

#     while not operation.done:
#         print("Đang render video...")
#         time.sleep(10)
#         operation = client.operations.get(operation)

#     if operation.response is None:
#         print("❌ Render FAILED")
#         return

#     video = operation.response.generated_videos[0]
#     response = requests.get(video.video.uri, headers={"x-goog-api-key": API_KEY})

#     # lưu tạm
#     temp_path = output.replace(".mp4", "_raw.mp4")
#     with open(temp_path, "wb") as f:
#         f.write(response.content)

#     # =============================
#     # ÉP 16:9 NGAY TẠI ĐÂY
#     # =============================
#     clip = VideoFileClip(temp_path)
#     clip = to_16_9(clip)

#     clip.write_videofile(
#         output,
#         codec="libx264",
#         audio_codec="aac",
#         fps=30
#     )

#     clip.close()
#     os.remove(temp_path)

# =============================
# GENERATE SCENE FUNCTION (Google style + duration)
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
            duration_seconds=duration,   # 👈 thêm lại
            aspect_ratio="16:9"
        )
    )

    # Poll
    while not operation.done:
        print("Waiting for video...")
        time.sleep(10)
        operation = client.operations.get(operation)

    if operation.response is None:
        print("❌ FAILED")
        return

    generated_video = operation.response.generated_videos[0]

    # Download giống Google
    client.files.download(file=generated_video.video)
    generated_video.video.save(output)

    print("✅ Saved:", output)

# print("Cảnh 1")
# generate_scene(
# """
# Cảnh công trình với người công nhân đứng gần bức tường và các bao keo (sử dụng hình wall.png).
# hành động: người đàn ông đi vào công trình chạm tay vào bước tường

# Voice:
# Nội dung đọc nhanh, đầy đủ, rõ ràng, không thêm bớt, không sai dấu, không thêm ký tự lạ như #, *, hoặc sai chính tả:
# "Muốn ốp gạch chuẩn chuyên nghiệp, bền chắc gấp đôi? Xem ngay quy trình thi công với keo dán gạch Weber!"

# Video rõ nét, sạch, tỉ lệ khung hình video đầu ra là 16:9.
# """,
# wall,
# 8,
# f"{OUTPUT_FOLDER}/scene1.mp4"
# )

# =============================
# Cảnh 1: Công nhân giới thiệu keo (4s, có voice)
# =============================
# print("Cảnh 1")
# generate_scene(
# """
# Người công nhân từ xa đi vào công trình công trình tới các bao keo thì dừng lại, tay chạm vào bao keo đã có trong ảnh worker_ref.png.
# Giữ nguyên hình worker_ref.png, không thêm hình bao keo ngoài.
# Không có bụi, khói, sương mù hay hiệu ứng ánh sáng đặc biệt.
# Video rõ nét, sáng, sạch, không có hiệu ứng bụi.
# Voice: 'bao keo dán gạch Weber giúp thi công nhanh và bền chắc.'
# """,
# person,
# 4,
# f"{OUTPUT_FOLDER}/scene1.mp4"
# )

# =============================
# Cảnh 2: Múc keo, trộn keo (4s, có voice)
# =============================
# print("Cảnh 2")
# generate_scene(
# """
# Cảnh người công nhân đứng cạnh thùng keo trong công trình (sử dụng hình worker_ref.png).
# Hành động:
# - bước 1: Người công nhân dùng cái ca nằm dưới mặt đất, múc keo từ bao keo cho vào thùng keo
# - bước 2: người đàn ông đặt ca trở lại xuống mặt đất và lấy máy trộn keo (cũng nằm dưới mặt đất) để trộn keo trong thùng
# - bước 3: Người công nhân trộn keo trong thùng bằng máy trộn, góc máy phải hướng xuống thùng keo
# Lưu ý: 
# - Không có hành động nào khác ngoài múc keo và trộn keo.
# - người công nhân phải dùng tay lấy các dụng cụ như ca, máy trộn để múc và trộn keo, các dụng cụ không dược bay lên
# - khi trộn keo góc máy phải hướng xuống thùng keo
# - các dụng cụ như ca và máy trộn keo được đặt dưới mặt đất, tay người công nhân phải lấy, các dụng cụ không được bay lên

# Chuyển động nhẹ:
# - Camera zoom-in nhẹ vào khu vực thùng keo
# - Người công nhân có chuyển động tay nhẹ tự nhiên gần thùng keo

# Giữ bố cục tự nhiên, không thay đổi nhiều chi tiết trong ảnh.

# Video rõ nét, sáng, sạch, thời lượng 4 giây.
# voice: 'Múc keo dán gạch Weber vào thùng, trộn đều với máy trộn chuyên dụng.'
# """,
# person,
# 8,
# f"{OUTPUT_FOLDER}/scene2.mp4"
# )


# print("Cảnh 2.1")

# generate_scene(
# """
# Cảnh người công nhân trong công trình (sử dụng hình worker_ref.png).

# Hành động:
# - Người công nhân đứng trước bức tường, dùng tay chạm nhẹ lên bề mặt tường bên cạnh bên phải để kiểm tra độ phẳng.
# - Sau đó chuyển sang cầm một chiếc búa cao su màu đen,cán là cán bằng gỗ, gõ nhẹ vào bề mặt viên gạch để kiểm tra độ cứng.
# - Hành động rõ ràng, tự nhiên, không nhanh quá.

# Yêu cầu:
# - Búa cao su màu đen, cán là cán bằng gỗ, phải nằm trong tay người công nhân, không được bay hoặc tự di chuyển.
# - Không có hành động thừa ngoài kiểm tra tường và gõ gạch.
# - Không có bụi, khói, hiệu ứng ánh sáng lạ.
# - đảm bảo phải giữ nguyên được bối cảnh công trình trong ảnh  worker_ref.png

# Chuyển động:
# - Camera zoom nhẹ vào khu vực tay và bề mặt tường/gạch.
# - Chuyển động tay tự nhiên, mượt.

# Hình ảnh:
# - Video rõ nét, sáng, sạch, góc quay ngang, bố cục 16:9.

# Voice:
# "Bề mặt phẳng phải cứng, sạch và khô"
# """,
# person,
# 4,
# f"{OUTPUT_FOLDER}/scene2_1.mp4"
# )

# print("Cảnh 3")
# generate_scene(
# """
# không ảnh backgound, không con người công nhân, chỉ có chữ xuất hiện trên màu nền lấy từ ảnh brown_bg.png.
# Hiển thị chữ tiếng Việt CHÍNH XÁC, không thay đổi nội dung, không sai dấu, viết lại chính tả, không thêm bớt từ ngữ, không thêm ký tự lạ như #, *, hoặc sai chính tả:
# 1) "Phần I: Hướng dẫn thi công dán gạch"
# 2) "Bước I: Chuẩn bị dụng cụ"

# Yêu cầu chữ:
# - Màu vàng #FFEB00
# - Căn giữa màn hình
# - Không thêm ký tự lạ như #, *, hoặc sai chính tả
# - dùng font cover.

# Hiệu ứng:
# - Dòng 1 xuất hiện trước, fade-in 0.5s → giữ → fade-out 0.5s, sau đó thu nhỏ lại.
# - Sau đó dòng 2 mới xuất hiện phóng to lên sau khi dòng 1 biến mất với hiệu ứng tương tự
# - Không dùng hiệu ứng đổi màu (không có đen → vàng)
# - Không hiệu ứng phức tạp khác

# Voice:
# "Phần 1: Hướng dẫn thi công dán gạch. Bước 1: chuẩn bị dụng cụ."
# """,
# background,
# 4,
# f"{OUTPUT_FOLDER}/scene3.mp4"
# )

# =============================
# Cảnh 4: Dụng cụ chuẩn bị (4s, không voice)
# =============================
# print("Cảnh 6")
# generate_scene(
# """
# Sử dụng nguyên bản hình ảnh dungcu.png làm nguồn duy nhất.
# KHÔNG thay đổi thứ tự dụng cụ, KHÔNG vẽ lại, vẽ thêm dụng cụ, KHÔNG thêm hoặc bớt chi tiết của các dụng cụ trong ảnh.

# ## Hiệu ứng:
# - Hiệu ứng chuyển động nhẹ nhàng, tự nhiên, không quá ồn ào, không có hiệu ứng bụi, khói, sương mù hay ánh sáng đặc biệt.
# - các dụng cụ xoay nhẹ, lơ lửng lên xuống, hoặc hiệu ứng chuyển động nhẹ nhàng khác nhưng vẫn giữ nguyên hình dạng và vị trí tương đối của các dụng cụ như ảnh gốc.
# - hiệu ứng chỉ duy nhất là các dụng cụ xoay nhẹ, không thêm cấc hiệu ứng phụ.

# ## Yêu cầu:
# - Giữ nguyên 100% hình dạng, màu sắc, vị trí tương đối của các dụng cụ như ảnh gốc.
# - Không tạo lại hình mới, không stylize.
# - Video rõ nét, sạch, không có bụi, khói, ánh sáng đặc biệt.

# ## Âm thanh
# - không có âm thanh, không tạo voice, không có hiệu ứng âm thanh nào khác.
# """,
# dung_cu,
# 4,
# f"{OUTPUT_FOLDER}/scene6.mp4"
# )

# print("Cảnh 7")
# generate_scene(
# """
# Cảnh người công nhân(sử dụng ảnh worker_ref.png) cầm tấm gạch lao sạch bề mặt viên gạch bằng miếng xốp ẩm màu vàng trong ảnh dungcu.png. màu sạch bà mặt sau của tấm gạch và đưa lên bề mặt tường đã được dán keo sẵn và dán vào.

# Chuyển động nhẹ:
# - Camera zoom-in nhẹ vào khu vực tấm gạch và bức tường
# - Người công nhân có chuyển động tay nhẹ, tạo cảm giác đang chuẩn bị dán gạch

# Bề mặt gạch sạch sẽ, rõ chi tiết.
# - lưu ý là công nhân lau bề mặt sau của tấm gạch, không phải là mặt trước.
# - mặt sau tấm gạch phải nhẵn, mặt sau có màu nâu có các đường răng cưa, mặt trước thì màu trắng, bóng loáng, không có đường răng cưa.
# - voice tiếng việt giọng nam

# Phân biệt bắt buộc:
# - Mặt SAU: màu nâu, nhám, có răng cưa →mặt sau được lau và dán vào tường, mặt sau không có keo, lau cho có không làm thay đổi hình dạng mặt sau.
# - Mặt TRƯỚC: màu trắng, bóng, phẳng → không được lau, không được chạm, không được dùng mặt trước dán vào tường.
# - Camera phải nhìn thấy rõ mặt SAU khi lau.

# Lưu ý quan trọng:
# - Không được lau mặt trước của gạch.
# - Không được nhầm lẫn giữa mặt trước và mặt sau.
# - Người công nhân phải cầm gạch bằng tay, không có vật thể bay.

# Video rõ nét, sáng, sạch, thời lượng 8 giây.
# voice: 'Chuẩn bị gạch đúng cách giúp tăng độ bám dính, Chỉ cần làm sạch mặt sau của gạch không cần ngâm gạch trong nước.'
# """,
# person,
# 8,
# f"{OUTPUT_FOLDER}/scene7.mp4"
# )



# =============================
# Cảnh 8: Đổ nước
# =============================
# print("Cảnh 8")
# generate_scene(
# """
# Cảnh cận thùng trộn trong công trình (sử dụng worker_ref.png).
# Hành động: người công nhân đổ nước sạch từ ca vào thùng.

# Yêu cầu:
# - Góc quay cận thùng
# - Nước đổ rõ ràng, không bắn tung tóe quá mức
# - Không có hành động khác

# Video rõ nét, sạch, thời lượng 4 giây.
# Voice: "Đổ nước vào thùng trước."
# """,
# person,
# 4,
# f"{OUTPUT_FOLDER}/scene8.mp4"
# )

# =============================
# Cảnh 9: Đổ keo
# =============================
# print("Cảnh 9")
# generate_scene(
# """
# Cảnh người công nhân dùng ca múc keo từ bao keo và đổ keo vào thùng (sử dụng worker_ref.png).

# Hành động:
# - người công nhân dùng ca múc keo từ bao keo và đổ keo vào thùng đã có nước

# Yêu cầu:
# - Góc quay từ trên xuống thấy rõ thùng
# - Keo rơi xuống tự nhiên
# - Không có hiệu ứng bụi, khói

# Video rõ nét, sạch, thời lượng 4 giây.
# Voice: "Sau đó thêm keo dán gạch."
# """,
# person,
# 4,
# f"{OUTPUT_FOLDER}/scene9.mp4"
# )

# # =============================
# # Cảnh 10: Hiện tỷ lệ
# # =============================
# print("Cảnh 10")
# generate_scene(
# """
# Cảnh hiển thị chữ trên nền (dùng ảnh worker_ref.png).

# không hiển thị chữ

# Yêu cầu:
# - Chữ màu vàng #FFEB00
# - Căn giữa màn hình
# - Font rõ, to
# - Không sai chính tả, không thêm ký tự lạ

# Hiệu ứng:
# - Fade in nhẹ
# - Giữ giữa màn hình

# Video rõ nét, sạch, thời lượng 4 giây.
# Voice: "Tỷ lệ tiêu chuẩn một nước ba keo theo thể tích"
# """,
# background,
# 4,
# f"{OUTPUT_FOLDER}/scene10.mp4"
# )

# # =============================
# # Cảnh 11: Trộn keo
# # =============================
# print("Cảnh 11")
# generate_scene(
# """
# Cảnh người công nhân dùng máy trộn keo trong thùng (sử dụng worker_ref.png).

# Hành động:
# - Máy trộn quay trong thùng keo
# - Keo chuyển động đều

# Yêu cầu:
# - Góc quay hướng xuống thùng
# - Không rung mạnh
# - Không có hành động khác

# Chuyển động nhẹ:
# - Zoom nhẹ vào thùng

# Video rõ nét, sạch, thời lượng 4 giây.
# Voice: "Khuấy đều bằng máy trộn đến khi đồng nhất."
# """,
# person,
# 4,
# f"{OUTPUT_FOLDER}/scene11.mp4"
# )

# # =============================
# # Cảnh 12: Nghỉ keo (time-lapse)
# # =============================
# print("Cảnh 12")
# generate_scene(
# """
# Cảnh thùng keo sau khi trộn xong, để yên, sử dụng worker_ref.png để làm bối cảnh.

# Góc quay:
# - Camera top-down (quay từ trên xuống thùng keo)
# - Khung hình tập trung vào miệng thùng keo

# Hành động:
# - Không có người thao tác
# - Thùng keo đứng yên

# Hiệu ứng:
# - Time-lapse nhẹ thể hiện thời gian trôi qua

# Yêu cầu:
# - Không hiển thị chữ / text overlay
# - Không thêm vật thể mới
# - Không hiệu ứng phức tạp

# Video rõ nét, sạch, thời lượng 4 giây.
# Voice: "Để keo nghỉ từ ba đến năm phút trước khi sử dụng."
# """,
# person,
# 4,
# f"{OUTPUT_FOLDER}/scene12.mp4"
# )

# print("Cảnh 13")
# generate_scene(
# """
# Trét keo lên tường (sử dụng worker_ref.png).

# Góc quay:
# - Góc rộng, thấy tay thợ và bề mặt tường

# Hành động:
# - Dùng bay trét keo đều lên tường
# - Động tác mượt, dứt khoát

# Yêu cầu:
# - Không text
# - Không thêm vật thể
# - Hình ảnh sạch, rõ

# Video 4 giây.
# Voice: "Trét keo lên bề mặt tường."
# """,
# person,
# 4,
# f"{OUTPUT_FOLDER}/scene13.mp4"
# )

# print("Cảnh 14")
# generate_scene(
# """
# Cận cảnh trét keo (sử dụng worker_ref.png).

# Góc quay:
# - Cận tay thợ và bay

# Hành động:
# - Trét keo kỹ hơn, thấy rõ lớp keo

# Yêu cầu:
# - Không text
# - Focus vào chuyển động tay

# Video 4 giây.
# Voice: ""
# """,
# person,
# 4,
# f"{OUTPUT_FOLDER}/scene14.mp4"
# )

# print("Cảnh 15")
# generate_scene(
# """
# Bắt đầu tạo răng cưa (sử dụng worker_ref.png).

# Góc quay:
# - Cận cảnh bay răng cưa

# Hành động:
# - Đặt bay nghiêng khoảng 60 độ lên keo

# Yêu cầu:
# - Không text
# - Nhấn mạnh góc nghiêng

# Video 4 giây.
# Voice: "Đặt bay răng cưa nghiêng khoảng sáu mươi độ."
# """,
# person,
# 4,
# f"{OUTPUT_FOLDER}/scene15.mp4"
# )

# print("Cảnh 16")
# generate_scene(
# """
# Kéo răng cưa tạo rãnh (sử dụng worker_ref.png).

# Góc quay:
# - Góc cận + theo chuyển động

# Hành động:
# - Kéo bay tạo các rãnh keo song song
# - Đều tay, chuyên nghiệp

# Hiệu ứng:
# - Slow motion nhẹ

# Yêu cầu:
# - Không text
# - Rãnh rõ, đẹp

# Video 4 giây.
# Voice: "Kéo đều tay để tạo các rãnh keo song song."
# """,
# person,
# 4,
# f"{OUTPUT_FOLDER}/scene16.mp4"
# )

# print("Cảnh 17")
# generate_scene(
# """
# Cận cảnh rãnh keo (sử dụng worker_ref.png).

# Góc quay:
# - Macro / rất cận

# Hành động:
# - Không thao tác
# - Focus texture rãnh keo

# Hiệu ứng:
# - Ánh sáng xiên làm nổi bề mặt

# Yêu cầu:
# - Không text
# - Hình ảnh sắc nét, đẹp

# Video 4 giây.
# Voice: ""
# """,
# person,
# 4,
# f"{OUTPUT_FOLDER}/scene17.mp4"
# )

# print("Cảnh 18")
# generate_scene(
# """
# Trét keo mặt sau gạch lớn (sử dụng worker_ref.png).

# Góc quay:
# - Cận tay và viên gạch

# Hành động:
# - Trét lớp keo mỏng phía sau viên gạch

# Yêu cầu:
# - Không text
# - Động tác gọn, rõ

# Video 4 giây.
# Voice: "Với gạch lớn, trét thêm một lớp mỏng phía sau để tăng độ bám."
# """,
# person,
# 4,
# f"{OUTPUT_FOLDER}/scene18.mp4"
# )

# print("Scene 19-23")

# Cảnh 19
generate_scene(
"""
Đưa gạch vào vị trí (sử dụng worker_ref.png).
- lưu ý là gạch không phải bao keo,
gach màu trăng, mặt sau gạch màu nâu có răng cưa, mặt trước gạch màu trắng bóng loáng không có răng cưa.

Góc quay:
- Trung cảnh, thấy tay + viên gạch + tường

Hành động:
- Đưa viên gạch từ dưới đất lại gần tường (chưa chạm)
- lấy gạch ở dưới đất lên, đưa lại gần tường, chuẩn bị dán

Chuyển cảnh:
- Kết thúc khi gạch gần chạm bề mặt

Yêu cầu:
- Không text
- Chuyển động mượt

Video 4 giây.
Voice: "Đặt viên gạch lên tường."
""",
person,
4,
f"{OUTPUT_FOLDER}/scene19.mp4"
)

# Cảnh 20
generate_scene(
"""
Ép gạch vào keo (sử dụng worker_ref.png).

Góc quay:
- Giữ giống cảnh trước

Hành động:
- Tiếp tục từ trạng thái gạch vừa chạm
- Ép nhẹ vào tường

Chuyển cảnh:
- Nối trực tiếp từ cảnh trước

Yêu cầu:
- Không text

Video 4 giây.
Voice: ""
""",
person,
4,
f"{OUTPUT_FOLDER}/scene20.mp4"
)

# Cảnh 21
# generate_scene(
# """
# Chuẩn bị gõ búa cao su (sử dụng worker_ref.png).

# Chi tiết công cụ:
# - Búa cao su
# - Đầu búa màu đen
# - Cán bằng gỗ

# Góc quay:
# - Cận tay + búa + gạch

# Hành động:
# - Đưa búa lên chuẩn bị gõ

# Chuyển cảnh:
# - Sau khi gạch đã ép xong

# Yêu cầu:
# - Không text

# Video 4 giây.
# Voice: "Dùng búa cao su gõ đều để dàn phẳng keo."
# """,
# person,
# 4,
# f"{OUTPUT_FOLDER}/scene21.mp4"
# )

# Cảnh 22
generate_scene(
"""
Gõ búa cao su và căn chỉnh (sử dụng worker_ref.png).

# Chi tiết công cụ:
- Búa cao su
- Đầu búa màu đen
- Cán bằng gỗ

Góc quay:
- Cận + theo chuyển động

Hành động:
- Gõ nhẹ 1-2 nhịp bằng búa cao su
- Sau đó dùng tay chỉnh nhẹ viên gạch

Hiệu ứng:
- Slow motion nhẹ lúc gõ

Chuyển cảnh:
- Nối trực tiếp từ cảnh trước

Yêu cầu:
- Hiển thị text: "Dễ dàng điều chỉnh trong 15-30 phút"
- Text nhỏ, không che thao tác

Video 4 giây.
Voice: "Có thể dễ dàng điều chỉnh trong mười lăm đến ba mươi phút."
""",
person,
4,
f"{OUTPUT_FOLDER}/scene22.mp4"
)

# Cảnh 23
generate_scene(
"""
Cận cảnh hoàn thiện (sử dụng worker_ref.png).

Góc quay:
- Cận bề mặt gạch

Hành động:
- Không thao tác
- Thể hiện gạch phẳng, đều

Hiệu ứng:
- Ánh sáng nhẹ làm nổi bề mặt

Chuyển cảnh:
- Kết thúc ổn định

Yêu cầu:
- Không text

Video 4 giây.
Voice: ""
""",
person,
4,
f"{OUTPUT_FOLDER}/scene23.mp4"
)