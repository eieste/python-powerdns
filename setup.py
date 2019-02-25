# -*- coding: utf-8 -*-
#
#  PowerDNS web api python client and interface (python-powerdns)
#
#  Copyright (C) 2018 Denis Pompilio (jawa) <dpompilio@vente-privee.com>
#
#  This file is part of python-powerdns
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the MIT License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  MIT License for more details.
#
#  You should have received a copy of the MIT License along with this
#  program; if not, see <https://opensource.org/licenses/MIT>.

import os
import setuptools


if __name__ == '__main__':
    readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
    release = "0.2.6"
    setuptools.setup(
        name="python-pdns",
        version=release,
        url="https://github.com/eieste/python-powerdns",
        author="Denis Pompilio (jawa)",
        author_email="dpompilio@vente-privee.com",
        maintainer="Stefan Eiermann",
        maintainer_email="python-org@ultraapp.de",
        description="PowerDNS web api python client and interface",
        long_description=open(readme_file).read(),
        long_description_content_type='text/markdown',
        license="MIT",
        platforms=['UNIX'],
        packages=['powerdns'],
        package_dir={'powerdns': 'powerdns'},
        data_files=[
            ('share/doc/python-powerdns', ['README.md', 'LICENSE', 'CHANGES']),
        ],
        keywords=['dns', 'powerdns', 'api'],
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Operating System :: POSIX :: BSD',
            'Operating System :: POSIX :: Linux',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Environment :: Web Environment',
            'Topic :: Utilities',
            ],
        requires=['urllib3', 'requests']
    )
