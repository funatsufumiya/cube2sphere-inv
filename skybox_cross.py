import argparse
import numpy as np
from PIL import Image
import os

def load_faces(face_paths):
    return {name: np.array(Image.open(path)) for name, path in face_paths.items()}

def save_skybox_cross(faces, face_size, output):
    # Unity標準のskyboxクロス配置
    #   [    ][top ][    ][    ]
    #   [left][front][right][back]
    #   [    ][bottom][    ][    ]
    img = np.zeros((face_size * 3, face_size * 4, 3), dtype=np.uint8)
    # 配置座標: (row, col)
    positions = {
        'front':  (1, 1),
        'back':   (1, 3),
        'left':   (1, 0),
        'right':  (1, 2),
        'top':    (0, 1),
        'bottom': (2, 1),
    }
    for name, (row, col) in positions.items():
        face = faces[name]
        if face.shape[0] != face_size or face.shape[1] != face_size:
            face = np.array(Image.fromarray(face).resize((face_size, face_size), Image.LANCZOS))
        y, x = row * face_size, col * face_size
        img[y:y+face_size, x:x+face_size, :] = face[:, :, :3]
    Image.fromarray(img).save(output)
    print(f'Saved: {output}')

def main():
    parser = argparse.ArgumentParser(description='Combine 6 cube face images into a Unity-style skybox cross image')
    parser.add_argument('front', type=str, help='front face image')
    parser.add_argument('back', type=str, help='back face image')
    parser.add_argument('left', type=str, help='left face image')
    parser.add_argument('right', type=str, help='right face image')
    parser.add_argument('top', type=str, help='top face image')
    parser.add_argument('bottom', type=str, help='bottom face image')
    parser.add_argument('-s', '--size', type=int, default=512, help='face size (pixels)')
    parser.add_argument('-o', '--output', type=str, default='skybox_cross.png', help='output filename')
    args = parser.parse_args()

    face_paths = {
        'front': args.front,
        'back': args.back,
        'left': args.left,
        'right': args.right,
        'top': args.top,
        'bottom': args.bottom,
    }
    faces = load_faces(face_paths)
    save_skybox_cross(faces, args.size, args.output)

if __name__ == '__main__':
    main()
