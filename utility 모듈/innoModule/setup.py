from setuptools import setup, find_packages

setup(
    name             = 'innoModule',
    version          = '1.0',
    description      = 'Module for Inno RPA',
    author           = 'Sung Gyu Jaegal',
    author_email     = 'jgsg3009@innorules.com',
    url              = 'https://github.com/jgsg3009/innoOCR',
    install_requires = [],
    packages         = find_packages(exclude = ['docs', 'tests*']),
    keywords         = ['innoModule','jython','excel','db connection','captcha'],
    python_requires  = '>=2.7',
    package_data={ 
        'inno' : ['rpa/poi-4.1.2/*','rpa/poi-4.1.2/*/*','rpa/jna/*','rpa/jdbc_drivers/*','rpa/captcha_sorvler_images/*'] 
    },
    zip_safe=False,
    classifiers      = [
        'Programming Language :: Python :: 2.7'
    ]
)
