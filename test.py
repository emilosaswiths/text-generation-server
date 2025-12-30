
# from app.services.monthly_moment_caption_service import generate_monthly_moment_captions
# from app.core.model_loader import load_model

# load_model()

# captions = generate_monthly_moment_captions(
#     month="June 2024",
#     posts=[
#     {
#       "_id": 101,
#       "caption": "Mountain trip together",
#       "image_blip_caption": "two women standing in a field of flowers",
#       "emotion": "Happy",
#       "emotionScore": 0.87,
#       "qualityScore": 0.74
#     },
#     {
#       "_id": 102,
#       "caption": "Evening walk",
#       "image_blip_caption": "a man and woman walking through the park",
#       "emotion": "Calm",
#       "emotionScore": 0.65,
#       "qualityScore": 0.68
#     },
#     {
#       "_id": 103,
#       "caption": "Coffee date",
#       "image_blip_caption": "two hands holding a cup of coffee",       
#       "emotion": "Happy",
#       "emotionScore": 0.79,
#       "qualityScore": 0.71
#     },
#     {
#       "_id": 104,
#       "caption": "Sunset view",
#       "image_blip_caption": "a couple sitting on a rock looking at the sunset",
#       "emotion": "Romantic",
#       "emotionScore": 0.83,
#       "qualityScore": 0.76
#     }
#   ]
# )

# print(captions)

from app.core.generation import generate_text
from app.core.model_loader import load_model

model = load_model()

prompt = (
    "Reply like a real person chatting on WhatsApp or Instagram.\n"
    "Give exactly 3 short reply suggestions.\n"
    "Each reply must be on a new line.\n\n"
    "Chat message:\n"
    "Good morning! 😊"
)


response = generate_text(
    prompt=prompt,
    temperature=0.7,
    top_p=0.9,
    max_new_tokens=80,
    do_sample=True
)

print(response)
