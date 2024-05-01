from setuptools import setup, find_packages
import os

with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='wirelesswizard',
    version='0.1.0-alpha',
    packages=find_packages(),
    install_requires=[
        'pandas'
    ],
    python_requires='>=3.9',
    author='mind2hex',
    author_email='neodeus8@gmail.com',
    description='Simple wireless interface handler',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mind2hex/wirelesswizard',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        
    ],
    keywords='wireless, interface, WiFi, monitor, Linux, iw, iwconfig, ifconfig',
)