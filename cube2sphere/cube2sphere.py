#!/usr/bin/env python

__author__ = 'Xyene'

import argparse
import os
import sys
import subprocess
import math
from .version import __version__


def main():
    _parser = argparse.ArgumentParser(prog='cube2sphere-inv', description='''
        Maps 6 directional images (from cameras facing each direction) into an equirectangular image for sphere material.
    ''')
    for f in ['front', 'back', 'left', 'right', 'top', 'bottom']:
        _parser.add_argument(f, type=str, metavar='<%s>' % f, help='source %s cube face filename' % f)
    _parser.add_argument('-v', '--version', action='version', version=__version__)
    _parser.add_argument('-r', '--resolution', type=int, nargs=2, default=[1024, 512], metavar=('<width>', '<height>'),
                         help='resolution for rendered map (defaults to 1024x512)')
    # rotationは逆変換用途では不要
    _parser.add_argument('-o', '--output', type=str, default='out', metavar='<path>',
                         help='filename for rendered map (defaults to "out")')
    _parser.add_argument('-f', '--format', type=str, default='TGA', metavar='<name>',
                         help='format to use when saving map, i.e. "PNG" or "TGA"')
    _parser.add_argument('-b', '--blender-path', type=str, default='blender', metavar='<path>',
                         help='filename of the Blender executable (defaults to "blender")')
    _parser.add_argument('-t', '--threads', type=int, default=None, metavar='<count>',
                         help='number of threads to use when rendering (1-64)')
    _parser.add_argument('-V', '--verbose', action='store_true',
                         help='enable verbose logging')
    _args = _parser.parse_args()

    # 画像フォーマットを自動で大文字化
    _args.format = _args.format.upper()

    # rotationsは不要

    if _args.threads and _args.threads not in list(range(1, 65)):
        _parser.print_usage()
        print('cube2sphere: error: too many threads specified (range is 1-64)')
        sys.exit(1)

    output = _args.output
    output = output if os.path.isabs(output) else os.path.join(os.getcwd(), output)

    out = open(os.devnull, 'w') if not _args.verbose else None

    faces = [_args.front, _args.back, _args.left, _args.right, _args.top, _args.bottom]
    for i in range(len(faces)):
        face = faces[i]
        face = faces[i] if os.path.isabs(face) else os.path.join(os.getcwd(), face)
        faces[i] = face

    try:
        process = subprocess.Popen(
            [_args.blender_path, '-E', 'CYCLES', '--background', '-noaudio',
             '-b', os.path.join(os.path.dirname(os.path.realpath(__file__)), 'projector.blend'),
             '-F', _args.format, '-x', '1',
             '-P', os.path.join(os.path.dirname(os.path.realpath(__file__)), 'blender_init.py')]
            + (['-t', str(_args.threads)] if _args.threads else [])
            + ['--', faces[0], faces[1], faces[2], faces[3], faces[4], faces[5],
               str(_args.resolution[0]), str(_args.resolution[1]), output],
            stderr=out, stdout=out)
    except:
        print('error spawning blender (%s) executable' % _args.blender_path)
        import traceback

        traceback.print_exc()
        sys.exit(1)
    else:
        process.wait()
        if process.returncode:
            print('blender exited with error code %d' % process.returncode)
            sys.exit(process.returncode)
