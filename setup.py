from setuptools import setup, find_packages

version = '0.0.1'

long_description = ""#open('README.rst').read()

setup(name='zenoss.zauthservice',
      version=version,
      description="Small daemon that uses bottle and a pool of zodb connections to serve authentication requests",
      long_description=long_description,
      classifiers=[
          "Programming Language :: Python",
      ],
      keywords='',
      author='Zenoss',
      author_email='dev@zenoss.com',
      url='https://github.com/zenoss/zauth-service',
      license='Commercial',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['zenoss'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'eventlet>=0.9.17',
          'astrolabe==0.2.1', 
          'metrology==0.9.0', 
          'bottle==0.11.6',
          'requests==1.2.3',
          'PyYAML==3.10'
      ],
      entry_points="""
      [console_scripts]
      zauth = zenoss.zauthservice.daemon:main
      """,
)
