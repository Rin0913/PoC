import os
import random
import numpy as np
import cv2
from PIL import Image, ImageDraw
from tensorflow.keras.layers import Conv2D, Conv2DTranspose, UpSampling2D, Input, MaxPooling2D 
from tensorflow.keras.models import Model

R = 100
weights_file="m.weights.h5"
epochs = 8


def generate_images(num_samples, N, image_size):

    width = height = image_size
    original_images = []
    noisy_images = []

    for _ in range(num_samples):
        original_image = Image.new("RGB", (width, height), "white")
        noisy_image = Image.new("RGB", (width, height), "white")
        draw_original = ImageDraw.Draw(original_image)
        draw_noisy = ImageDraw.Draw(noisy_image)

        rectangles = [(random.randint(10, 20), random.randint(10, 20), width - random.randint(10, 20), height - random.randint(10, 20))]
        for _ in range(N):
            # Randomly select a rectangle to split
            rect = random.choice(rectangles)
            rectangles.remove(rect)
            x1, y1, x2, y2 = rect

            # Randomly choose vertical or horizontal split
            if random.choice([True, False]) and (x2 - x1 > 100):  # Vertical split
                split = random.randint(x1 + 50, x2 - 50)
                rectangles.append((x1, y1, split, y2))  # Left rectangle
                rectangles.append((split, y1, x2, y2))  # Right rectangle
            elif y2 - y1 > 100:  # Horizontal split
                split = random.randint(y1 + 50, y2 - 50)
                rectangles.append((x1, y1, x2, split))  # Top rectangle
                rectangles.append((x1, split, x2, y2))  # Bottom rectangle
            else:
                # If cannot split, keep the rectangle
                rectangles.append(rect)

        # Draw the final rectangles and add text
        for rect in rectangles:
            x1, y1, x2, y2 = rect

            line_thickness = random.randint(1, 5)

            # Draw rectangles on the original image
            draw_original.rectangle([x1, y1, x2, y2], outline="black", width=line_thickness)

            x1_noisy = x1
            y1_noisy = y1
            x2_noisy = x2
            y2_noisy = y2

            random_int = lambda: random.randint(-3, 3)
            if x1 == x2:
                draw_noisy.line([(x1_noisy + random_int(), y1_noisy), (x2_noisy + random_int(), y1_noisy)], fill="black", width=line_thickness)
                draw_noisy.line([(x2_noisy + random_int(), y1_noisy), (x2_noisy + random_int(), y2_noisy)], fill="black", width=line_thickness)
                draw_noisy.line([(x2_noisy + random_int(), y2_noisy), (x1_noisy + random_int(), y2_noisy)], fill="black", width=line_thickness)
                draw_noisy.line([(x1_noisy + random_int(), y2_noisy), (x1_noisy + random_int(), y1_noisy)], fill="black", width=line_thickness)
            else:
                draw_noisy.line([(x1_noisy, y1_noisy + random_int()), (x2_noisy, y1_noisy + random_int())], fill="black", width=line_thickness)
                draw_noisy.line([(x2_noisy, y1_noisy + random_int()), (x2_noisy, y2_noisy + random_int())], fill="black", width=line_thickness)
                draw_noisy.line([(x2_noisy, y2_noisy + random_int()), (x1_noisy, y2_noisy + random_int())], fill="black", width=line_thickness)
                draw_noisy.line([(x1_noisy, y2_noisy + random_int()), (x1_noisy, y1_noisy + random_int())], fill="black", width=line_thickness)

        original_image = original_image.convert('L')
        noisy_image = noisy_image.convert('L')

        original_images.append(original_image)
        noisy_images.append(noisy_image)

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

