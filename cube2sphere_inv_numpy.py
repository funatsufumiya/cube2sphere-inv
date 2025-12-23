import argparse
import numpy as np
from PIL import Image
import os

def load_faces(face_paths):
    return {name: np.array(Image.open(path)) for name, path in face_paths.items()}

def direction_to_cube_face(x, y, z):
    abs_x, abs_y, abs_z = abs(x), abs(y), abs(z)
    if abs_x >= abs_y and abs_x >= abs_z:
        # X面
        if x > 0:
            face = 'right'
            u = -z / abs_x
            v = -y / abs_x
        else:
            face = 'left'
            u = z / abs_x
            v = -y / abs_x
    elif abs_y >= abs_x and abs_y >= abs_z:
        # Y面
        if y > 0:
            face = 'front'
            u = x / abs_y
            v = -z / abs_y
        else:
            face = 'back'
            u = -x / abs_y
            v = -z / abs_y
    else:
        # Z面
        if z > 0:
            face = 'top'
            u = x / abs_z
            v = -y / abs_z
        else:
            face = 'bottom'
            u = x / abs_z
            v = y / abs_z
    # u,v: [-1,1] → [0,1]
    u = (u + 1) / 2
    v = (v + 1) / 2
    return face, u, v

def equirectangular_from_cubemap(faces, width, height):
    result = np.zeros((height, width, 3), dtype=np.uint8)
    for j in range(height):
        theta = np.pi * (j / height)  # 緯度 [0, pi]
        for i in range(width):
            phi = 2 * np.pi * (i / width)  # 経度 [0, 2pi]
            # 球面座標→方向ベクトル
            x = np.sin(theta) * np.cos(phi)
            y = np.sin(theta) * np.sin(phi)
            z = np.cos(theta)
            # 方向ベクトル→cube face & face座標
            face, u, v = direction_to_cube_face(x, y, z)
            h, w = faces[face].shape[:2]
            px = min(max(int(u * w), 0), w - 1)
            py = min(max(int(v * h), 0), h - 1)
            result[j, i] = faces[face][py, px][:3]
    return result

def main():
    parser = argparse.ArgumentParser(description='Convert 6 cube face images to equirectangular image (numpy version)')
    parser.add_argument('front', type=str, help='front face image')
    parser.add_argument('back', type=str, help='back face image')
    parser.add_argument('left', type=str, help='left face image')
    parser.add_argument('right', type=str, help='right face image')
    parser.add_argument('top', type=str, help='top face image')
    parser.add_argument('bottom', type=str, help='bottom face image')
    parser.add_argument('-r', '--resolution', type=int, nargs=2, default=[1024, 512], metavar=('width', 'height'), help='output resolution')
    parser.add_argument('-o', '--output', type=str, default='out.png', help='output filename')
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
    width, height = args.resolution
    out_img = equirectangular_from_cubemap(faces, width, height)
    Image.fromarray(out_img).save(args.output)
    print(f'Saved: {args.output}')

if __name__ == '__main__':
    main()
