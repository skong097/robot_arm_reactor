from setuptools import find_packages, setup
from glob import glob

package_name = 'omx_reactor'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/web/static',
            glob('omx_reactor/web/static/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Stephen Kong (gjkong)',
    maintainer_email='kong@pinklab.art',
    description='OMX reactor demo',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'reactor_node = omx_reactor.reactor_node:main',
            'dashboard_node = omx_reactor.dashboard_node:main',
        ],
    },
)
