from setuptools import find_packages, setup

package_name = 'omx_reactor'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='gjkong',
    maintainer_email='skong097@gmail.com',
    description='OMX reactor — shim package (split 후 reactor_node + gesture_detector_node 만 잔존, 외부 import 호환용 shim 모듈 포함).',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [],
    },
)
