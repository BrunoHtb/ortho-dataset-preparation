import cv2
import numpy as np
import os
from glob import glob
from dotenv import load_dotenv 


def rotate_point(x, y, angle, img_w, img_h):
    """
    Rotaciona um ponto (x, y) pelo centro da imagem para um ângulo especificado.
    """
    if angle == 90:
        return y, 1 - x  # 🔄 Correção para 90 graus
    elif angle == 180:
        return 1 - x, 1 - y  # 🔄 Correção para 180 graus
    elif angle == 270:
        return 1 - y, x  # 🔄 Correção para 270 graus
    else:
        return x, y  # 🔄 Sem rotação


def rotate_image_and_labels(image_path, label_path, output_dir, angles=[90, 180, 270]):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Erro ao carregar {image_path}")
        return
    
    img_h, img_w = img.shape[:2]

    with open(label_path, "r") as f:
        lines = f.readlines()

    for angle in angles:
        center = (img_w // 2, img_h // 2)
        rot_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated_img = cv2.warpAffine(img, rot_matrix, (img_w, img_h))

        new_lines = []
        for line in lines:
            parts = line.strip().split()
            class_id = parts[0]
            coords = np.array(parts[1:], dtype=float).reshape(-1, 2)

            rotated_coords = [rotate_point(x, y, angle, img_w, img_h) for x, y in coords]
            new_line = f"{class_id} " + " ".join(f"{x:.6f} {y:.6f}" for x, y in rotated_coords)
            new_lines.append(new_line)

        os.makedirs(output_dir, exist_ok=True)

        base_name = os.path.basename(image_path).replace(".jpg", f"_rot{angle}")
        new_image_path = os.path.join(output_dir, base_name + ".jpg")
        new_label_path = os.path.join(output_dir, base_name + ".txt")

        cv2.imwrite(new_image_path, rotated_img)
        with open(new_label_path, "w") as f:
            f.write("\n".join(new_lines))

        print(f"Salvo: {new_image_path}, {new_label_path}")


def process_directory(input_dir, output_dir, angles=[90, 180, 270]):
    image_files = glob(os.path.join(input_dir, "*.jpg"))
    
    for image_path in image_files:
        label_path = image_path.replace(".jpg", ".txt")
        if not os.path.exists(label_path):
            print(f"Aviso: Não existe anotação para {image_path}, pulando...")
            continue
        
        rotate_image_and_labels(image_path, label_path, output_dir, angles)

if __name__ == "__main__":
    load_dotenv()
    INPUT_PATH = os.getenv("INPUT_PATH")
    OUTPUT_PATH = os.getenv("OUTPUT_PATH")

    process_directory(INPUT_PATH, OUTPUT_PATH)
