from setuptools import setup

setup(
    name='cube2sphere_inv',
    version='0.1.0',
    description='Convert 6 cube face images to equirectangular image and skybox cross image',
    author='Fumiya Funatsu',
    author_email='funatsu.fumiya@gmail.com',
    py_modules=['cube2sphere_inv', 'skybox_cross'],
    install_requires=['numpy', 'Pillow'],
    entry_points={
        'console_scripts': [
            'cube2sphere-inv=cube2sphere_inv:main',
            'skybox-cross=skybox_cross:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
