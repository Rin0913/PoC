import os
import random
import numpy as np
import math
import cv2
from PIL import Image, ImageDraw
from tensorflow.keras.layers import Conv2D, Conv2DTranspose, UpSampling2D, Input, MaxPooling2D 
from tensorflow.keras.models import Model

R = 100
weights_file="m.weights.h5"
epochs = 8


def generate_images(num_samples, N, image_size, invert=False):
    width = height = image_size
    original_images = []
    noisy_images = []

    def draw_dashed_line(draw, start_pos, end_pos, min_dash_length, max_dash_length, min_gap_length, max_gap_length, width, **kwargs):
        x1, y1 = start_pos
        x2, y2 = end_pos

        total_length = math.hypot(x2 - x1, y2 - y1)
        if total_length == 0:
            return
        dx = (x2 - x1) / total_length
        dy = (y2 - y1) / total_length

        current_length = 0

        while current_length < total_length:
            line_thickness = width + random.randint(-1, 1)
            dash_length = random.randint(min_dash_length, max_dash_length)
            gap_length = random.randint(min_gap_length, max_gap_length)

            start = (
                x1 + dx * current_length,
                y1 + dy * current_length
            )
            end = (
                x1 + dx * (current_length + dash_length),
                y1 + dy * (current_length + dash_length)
            )

            if (dx >= 0 and end[0] > x2) or (dx < 0 and end[0] < x2):
                end = (x2, y2)
            if (dy >= 0 and end[1] > y2) or (dy < 0 and end[1] < y2):
                end = (x2, y2)

            draw.line([start, end], width=line_thickness, **kwargs)

            current_length += dash_length + gap_length

    for _ in range(num_samples):
        original_image = Image.new("L", (width, height), "black")
        noisy_image = Image.new("L", (width, height), "black")
        draw_original = ImageDraw.Draw(original_image)
        draw_noisy = ImageDraw.Draw(noisy_image)

        rectangles = []
        min_offset = image_size // 20
        max_offset = image_size // 10

        # Define rectangles in four quadrants
        rectangles.append((
            random.randint(0, random.randint(min_offset, max_offset)),  # x1
            random.randint(0, random.randint(min_offset, max_offset)),  # y1
            image_size // 2 - random.randint(min_offset, max_offset),   # x2
            image_size // 2 - random.randint(min_offset, max_offset)    # y2
        ))
        rectangles.append((
            random.randint(0, random.randint(min_offset, max_offset)),  # x1
            image_size // 2 + random.randint(min_offset, max_offset),   # y1
            image_size // 2 - random.randint(min_offset, max_offset),   # x2
            image_size - random.randint(min_offset, max_offset)         # y2
        ))
        rectangles.append((
            image_size // 2 + random.randint(min_offset, max_offset),   # x1
            random.randint(0, random.randint(min_offset, max_offset)),  # y1
            image_size - random.randint(min_offset, max_offset),        # x2
            image_size // 2 - random.randint(min_offset, max_offset)    # y2
        ))
        rectangles.append((
            image_size // 2 + random.randint(min_offset, max_offset),   # x1
            image_size // 2 + random.randint(min_offset, max_offset),   # y1
            image_size - random.randint(min_offset, max_offset),        # x2
            image_size - random.randint(min_offset, max_offset)         # y2
        ))

        for _ in range(N):
            # Randomly select a rectangle to split
            if not rectangles:
                break
            rect = random.choice(rectangles)
            rectangles.remove(rect)
            x1, y1, x2, y2 = rect

            # Randomly choose vertical or horizontal split
            if random.choice([True, False]) and (x2 - x1 >= image_size // 10):  # Vertical split
                split = random.randint(x1 + image_size // 20, x2 - image_size // 20)
                rectangles.append((x1, y1, split, y2))  # Left rectangle
                rectangles.append((split, y1, x2, y2))  # Right rectangle
            elif y2 - y1 >= image_size // 10:  # Horizontal split
                split = random.randint(y1 + image_size // 20, y2 - image_size // 20)
                rectangles.append((x1, y1, x2, split))  # Upper rectangle
                rectangles.append((x1, split, x2, y2))  # Lower rectangle
            else:
                # If cannot split, keep the rectangle
                rectangles.append(rect)

        # Draw the final rectangles
        for rect in rectangles:
            x1, y1, x2, y2 = rect

            line_thickness = 2

            # Draw rectangle on the original image
            draw_original.rectangle([x1, y1, x2, y2], outline="white", width=line_thickness)

            x1_noisy = x1
            y1_noisy = y1
            x2_noisy = x2
            y2_noisy = y2

            random_int = lambda: random.randint(-3, 3)

            # Draw irregular dashed rectangle on noisy image
            min_dash_length = image_size // 20
            max_dash_length = image_size // 10
            min_gap_length = image_size // 100
            max_gap_length = image_size // 50

            draw_dashed_line(
                draw_noisy,
                (x1_noisy + random_int(), y1_noisy + random_int()),
                (x2_noisy + random_int(), y1_noisy + random_int()),
                min_dash_length, max_dash_length, min_gap_length, max_gap_length,
                fill="white",
                width=line_thickness
            )
            draw_dashed_line(
                draw_noisy,
                (x2_noisy + random_int(), y1_noisy + random_int()),
                (x2_noisy + random_int(), y2_noisy + random_int()),
                min_dash_length, max_dash_length, min_gap_length, max_gap_length,
                fill="white",
                width=line_thickness
            )
            draw_dashed_line(
                draw_noisy,
                (x2_noisy + random_int(), y2_noisy + random_int()),
                (x1_noisy + random_int(), y2_noisy + random_int()),
                min_dash_length, max_dash_length, min_gap_length, max_gap_length,
                fill="white",
                width=line_thickness
            )
            draw_dashed_line(
                draw_noisy,
                (x1_noisy + random_int(), y2_noisy + random_int()),
                (x1_noisy + random_int(), y1_noisy + random_int()),
                min_dash_length, max_dash_length, min_gap_length, max_gap_length,
                fill="white",
                width=line_thickness
            )

        if invert:
            # Invert images: lines become black (0), background white (255)
            original_image = ImageOps.invert(original_image)
            noisy_image = ImageOps.invert(noisy_image)

        original_images.append(np.array(original_image))
        noisy_images.append(np.array(noisy_image))

    return np.array(original_images), np.array(noisy_images)

def build_autoencoder(input_shape):
    input_img = Input(shape=input_shape)
    x = Conv2D(32, (3, 3), activation='relu', padding='same')(input_img)
    x = Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = Conv2D(1, (3, 3), activation='sigmoid', padding='same')(x)

    autoencoder = Model(input_img, x)
    return autoencoder

autoencoder = build_autoencoder((None, None, 1))
autoencoder.compile(optimizer='adam', loss='binary_crossentropy')

if os.path.exists(weights_file):
    print(f"Loading weights from {weights_file}")
    autoencoder.load_weights(weights_file)

if __name__ == '__main__':
    while True:
        X_train, y_train = generate_images(num_samples=6400, N=random.randint(15, 30), image_size=R)
        X_test, y_test = generate_images(num_samples=128, N=random.randint(15, 30), image_size=R)

        X_train = X_train.astype('float32') / 255
        y_train = y_train.astype('float32') / 255
        X_test = X_test.astype('float32') / 255
        y_test = y_test.astype('float32') / 255

        X_train = X_train[..., np.newaxis]
        y_train = y_train[..., np.newaxis]
        X_test = X_test[..., np.newaxis]
        y_test = y_test[..., np.newaxis]

        history = autoencoder.fit(X_train, y_train,
                                  epochs=epochs,
                                  batch_size=64,
                                  shuffle=True,
                                  validation_data=(X_test, y_test))

        print("Model training complete.")

        # i = not i
        print(f"Saving weights to {weights_file}")
        autoencoder.save_weights(weights_file)

