# === Class: python::python_2_7_3
#
#   Install Python 2.7.3 on Centos so as not to break yum
#
# === Parameters
#
#   None
#
# === Variables
#
#   [*::opt_path*]
#       Convenience variable for opt path 
#
#   [*::python_path*]
#       Convenience variable for python path
#
# === Examples
#
#   include python::python_2_7_3
#
#   class{'python::python_2_7_3':}
#
# === Authors
#
#   Stacey Wrazien <wraziens@email.chop.edu>
#

class python::python_2_7_3{

    $opt_path = '/opt/local/bin/'
    $python_path = '/opt/local/Python-2.7.3/bin/'


    utilities::wget{'python':
        file    => 'http://python.org/ftp/python/2.7.3/Python-2.7.3.tgz',
		target => '/tmp/Python-2.7.3.tgz'
    }

    utilities::untar{'python': 
        file    => "Python-2.7.3.tgz",
        require => Utilities::Wget['python'],
    }

    exec{'config python':
        path    => $path,
        cwd     => '/tmp/Python-2.7.3/',
        command => '/bin/sh configure --prefix=/opt/local/Python-2.7.3',
        creates => '/tmp/Python-2.7.3/Makefile',
        require => Utilities::Untar['python']
    }

    exec {'make python':
        path    => $path,
        cwd     => '/tmp/Python-2.7.3/',
        command => 'make && make install',
        creates => $python_path,
        require => Exec['config python']
    }


    exec{'adjust path':
        path    => $path,
        cwd     => '/home/vagrant',
        command => "echo \"export PATH=${opt_path}:\\\$PATH\" >> .bashrc",
        require => Exec['make python'] 
    }
    
    exec{'adjust path for python':
        path    => $path,
        cwd     => '/etc/profile.d/',
        command => "echo \"export PATH=${python_path}:\\\$PATH\" > python.sh",
        require => Exec['make python'],
        creates => '/etc/profile.d/python.sh',
    }

    utilities::wget{'distribute':
        file    => 'http://pypi.python.org/packages/source/d/distribute/distribute-0.6.27.tar.gz',
		target => '/tmp/distribute-0.6.27.tar.gz',
        require => Exec['adjust path for python']
    }

    utilities::untar{'distribute':
        file    => 'distribute-0.6.27.tar.gz',
        require => Utilities::Wget['distribute'],
    }
    
    exec{'install distribute':
        path    => [$python_path, $opt_path, $path],
        cwd     => '/tmp/distribute-0.6.27/',
        command => 'python setup.py install',
        require => Utilities::Untar['distribute'],
        creates => "/opt/local/Python-2.7.3/lib/python2.7/site-packages/distribute-0.6.27-py2.7.egg",
    }

}
