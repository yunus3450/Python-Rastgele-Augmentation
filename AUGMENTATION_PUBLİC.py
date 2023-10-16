import cv2
import os
import random
import shutil
import numpy as np

# Augmentation türlerini True/False belirleme
do_blur = True
do_gaussian_blur = True
do_median_blur = True
do_noise = True
do_saturation = True
do_rotation = True


# Açı
angle = 0
#Resim ve etiket bilgilerini içeren .txt uzantılı dosyaların olduğu klasör
path_folder = "path/path"


#Noise Fonksiyonu
def add_noise(image):
    h, w, c = image.shape
    mean = 0
    stddev = 10
    noise = np.zeros((h, w, c), np.uint8)
    cv2.randn(noise, mean, stddev)
    noisy_image = cv2.add(image, noise)
    return noisy_image

#Saturation Fonksiyonu
def adjust_saturation(image, saturation_factor):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv = np.array(hsv, dtype=np.float64)
    hsv[:, :, 1] = hsv[:, :, 1] * saturation_factor
    hsv[:, :, 1][hsv[:, :, 1] > 255] = 255
    hsv[:, :, 2] = hsv[:, :, 2] * saturation_factor 
    hsv[:, :, 2][hsv[:, :, 2] > 255] = 255
    hsv = np.array(hsv, dtype=np.uint8)
    img_sat = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return img_sat


# Rotation Fonksiyonu
def rotate_image(image, angle):
    height, width = image.shape[:2]
    rotation_matrix = cv2.getRotationMatrix2D((width/2, height/2), angle, 1)
    rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height))
    return rotated_image

# Augmentation işlemleri
def augment_image(image, do_rotation):
    if do_blur:
        image = cv2.blur(image, (5, 5))
    if do_gaussian_blur:
        image = cv2.GaussianBlur(image, (5, 5), 0)
    if do_median_blur:
        image = cv2.medianBlur(image, 5)
    if do_noise:
        image = add_noise(image)
    if do_saturation:
        saturation_factor = random.uniform(0, 2)
        image = adjust_saturation(image, saturation_factor)
    if do_rotation:
        angle = random.randint(0, 15)#Belirlenen aralıklarda dönme uygular
        image = rotate_image(image, angle)
    return image


# Ana döngü
for file in os.listdir(path_folder):
    if file.endswith(".jpg"):
        image_path = os.path.join(path_folder, file)
        image = cv2.imread(image_path)
        do_median_blur = random.choice([True, False]) 
        do_gaussian_blur = random.choice([True, False])
        do_noise = random.choice([True, False]) 
        do_saturation = random.choice([False, True]) 
        do_blur = random.choice([True, False]) 
        do_rotation = random.choice([True, False]) 
        augmented_image = augment_image(image, do_rotation)
        if do_rotation == True:
            
            rotated_image = rotate_image(augmented_image, angle)
            

            # Döndürülmüş görüntüyü kaydetmek isterseniz
            new_rotated_image_path = os.path.join(path_folder, "rotated_" + file)
            cv2.imwrite(new_rotated_image_path, rotated_image)
            

            # Sınıf numarası ve diğer özellikler aynı kalacak şekilde txt dosyasını güncelleme
            txt_file_path = os.path.splitext(image_path)[0] + ".txt"
            new_txt_file_path = os.path.splitext(new_rotated_image_path)[0] + ".txt"
            shutil.copy(txt_file_path, new_txt_file_path)

            with open(txt_file_path, 'r') as f:
                lines = f.readlines()
            with open(new_txt_file_path, 'w') as f:
                f.write(lines[0]) # sınıf numarası aynı kalır
                # Döndürülmüş koordinatları hesapla ve yazdır
                for line in lines[1:]:
                    line = line.strip().split()
                    x = float(line[1])
                    y = float(line[2])
                    cos_theta = np.cos(np.radians(angle))
                    sin_theta = np.sin(np.radians(angle))
                    x_new = x*cos_theta - y*sin_theta
                    y_new = x*sin_theta + y*cos_theta
                    f.write(f"{line[0]} {x_new} {y_new} {line[3]} {line[4]}\n")
        elif do_rotation == False:
            txt_file_path = os.path.splitext(image_path)[0] + ".txt"
            rotated_image = augmented_image
            # Augmentasyon yapılmış ama döndürülmemiş görüntüyü kaydetmek isterseniz
            new_augmented_image_path = os.path.join(path_folder, "augmented_" + file)
            cv2.imwrite(new_augmented_image_path, rotated_image)
            # Txt dosyasını kopyalamak yeterli
            new_txt_file_path = os.path.splitext(new_augmented_image_path)[0] + ".txt"
            shutil.copy(txt_file_path, new_txt_file_path)
