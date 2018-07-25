from distutils.core import setup, Extension
 
module1 = Extension("ftdIOmodule",
                    include_dirs = ['/home/its/libftdi/libftdi/src'],
                    libraries = ['ftd2xx'],
                    library_dirs = ['/usr/local/lib64'],
                    sources = ['ftdIOmodule.c'])
 
setup (name = "ftdIOmodule",
        version = '2',
        description = 'ftdIO functions for Python',
        ext_modules = [module1])
