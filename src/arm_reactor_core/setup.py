from setuptools import find_packages, setup
from glob import glob

package_name = 'arm_reactor_core'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/web/static',
            glob('arm_reactor_core/web/static/*')),
        ('share/' + package_name + '/models/gesture',
            glob('models/gesture/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='gjkong',
    maintainer_email='skong097@gmail.com',
    description='Arm-agnostic reactor core — context, motion mapper/scheduler, dashboard, reactor node.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'dashboard_node = arm_reactor_core.dashboard_node:main',
            'reactor_node = arm_reactor_core.reactor_node:main',
            'gesture_detector_node = arm_reactor_core.gesture_detector_node:main',
        ],
    },
)
