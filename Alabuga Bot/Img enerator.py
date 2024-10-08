import os
from gradio_client import Client
import time

def imag(prompt):
    try:
        client = Client("mukaist/Midjourney")
    except ValueError as e:
        print(f"Error: {e}")
        print("Unable to connect to the model. Please check the model URL and try again.")
        return None

    try:
        result = client.predict(
            prompt=prompt,
            negative_prompt="(deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime:1.4), text, close up, cropped, out of frame, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck",
            use_negative_prompt=True,
            style="2560 x 1440",
            seed=0,
            width=1024,
            height=1024,
            guidance_scale=6,
            randomize_seed=True,
            api_name="/run"
        )
    except Exception as e:
        print(f"Error: {e}")
        print("An error occurred while generating the image. Please try again.")
        return None

    # Create a directory for images if it doesn't exist
    images_dir = 'Images'
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    # Save the generated image to a file
    filename = f"{prompt}.png"
    filepath = os.path.join(images_dir, filename)
    result.save(filepath, format="PNG")
    print('Файл с результатом успешно сохранен!')

    # Return the filepath
    return filepath

while True:
    prompt = input('Введите запрос: ')
    imag(prompt)
    time.sleep(2)