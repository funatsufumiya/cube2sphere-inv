import argparse
import numpy as np
from PIL import Image
import os
from numba import njit

def load_faces(face_paths):
    return {name: np.array(Image.open(path)) for name, path in face_paths.items()}

# グローバルでfloat64型で定義
normals = np.array([
    [0, 1, 0], [0, -1, 0], [1, 0, 0], [-1, 0, 0], [0, 0, 1], [0, 0, -1]
], dtype=np.float64)
us = np.array([
    [1, 0, 0], [-1, 0, 0], [0, -1, 0], [0, 1, 0], [1, 0, 0], [1, 0, 0]
], dtype=np.float64)
vs = np.array([
    [0, 0, -1], [0, 0, -1], [0, 0, -1], [0, 0, -1], [0, -1, 0], [0, 1, 0]
], dtype=np.float64)

@njit
def direction_to_cube_face_numba(x, y, z):
    p = np.array([x, y, z], dtype=np.float64)
    max_dot = -1e10
    face_idx = -1
    for idx in range(6):
        dot = np.dot(p, normals[idx])
        if dot > max_dot:
            max_dot = dot
            face_idx = idx
    u = np.dot(p, us[face_idx])
    v = np.dot(p, vs[face_idx])
    u = (u + 1) / 2
    v = (v + 1) / 2
    # right, left, back だけフリップ
    if face_idx in (2, 3, 5):
        u = 1 - u
    return face_idx, u, v

@njit
def fast_equirectangular_from_cubemap(faces_arr, width, height, flip_flags):
    result = np.zeros((height, width, 3), dtype=np.uint8)
    for j in range(height):
        theta = np.pi * (1 - j / height)
        for i in range(width):
            phi = 2 * np.pi * (i / width)
            x = -np.sin(theta) * np.cos(phi)
            y = -np.sin(theta) * np.sin(phi)
            z = -np.cos(theta)
            face_idx, u, v = direction_to_cube_face_numba(x, y, z)
            if flip_flags[face_idx]:
                u = 1 - u
            face_img = faces_arr[face_idx]
            h, w = face_img.shape[:2]
            px = min(max(int(u * w), 0), w - 1)
            py = min(max(int(v * h), 0), h - 1)
            result[j, i] = face_img[py, px][:3]
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
    faces_arr = [faces['front'], faces['back'], faces['right'], faces['left'], faces['top'], faces['bottom']]
    # 6面のフリップ有無パターンを生成
    names = ["t","b","r","l","f","k"]  # k=back
    for i in range(64):
        pattern = [(i >> j) & 1 for j in range(6)]
        out_img = fast_equirectangular_from_cubemap(faces_arr, width, height, np.array(pattern))
        # 例: t0b0r0l0f0k0
        flagstr = ''.join([f"{n}{f}" for n, f in zip(names, pattern)])
        fname = f"out_{flagstr}.png"
        Image.fromarray(out_img).save(fname)
        print(f'Saved: {fname}')

if __name__ == '__main__':
    main()