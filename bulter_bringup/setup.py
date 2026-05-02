from setuptools import setup
import os
from glob import glob

package_name = 'bulter_bringup'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
               
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        
        # Launch files
        (os.path.join('share', package_name, 'launch'), glob('launch/*')),

        # Config files
        (os.path.join('share', package_name, 'config'), glob('config/*')),

        # World files
        (os.path.join('share', package_name, 'world/hotel'), glob('world/hotel/*')),

        # Models
        
        (os.path.join('share', package_name, 'models/table'), glob('models/table/*')),
        (os.path.join('share', package_name, 'models/beer'), glob('models/beer/*.sdf')),
        (os.path.join('share', package_name, 'models/beer'), glob('models/beer/*.config')),
        (os.path.join('share', package_name, 'models/beer/scripts'), glob('models/beer/scripts/*')),
        (os.path.join('share', package_name, 'models/beer/textures'), glob('models/beer/textures/*')), 
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='thamil-selva',
    maintainer_email='tamilselvan1709@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
     extras_require={'test': ['pytest']},
    entry_points={
        'console_scripts': [
            'sdf_spawner = bulter_bringup.spawn_entity:main',
            'butler_delivery_node = bulter_bringup.bulter_delivery_node:main',
            'cafe_delivery_node = bulter_bringup.butler_delivery:main',
        ],
    },
)
