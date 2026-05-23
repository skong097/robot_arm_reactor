from setuptools import find_packages, setup
from glob import glob

package_name = 'omx_motion_pack'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/models/external_cam',
            glob('models/external_cam/*')),
        ('share/' + package_name + '/models/gesture',
            glob('models/gesture/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='gjkong',
    maintainer_email='skong097@gmail.com',
    description='OMX (OpenManipulator-X, 4-DOF) motion pack for arm_reactor_core.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [],
    },
)
