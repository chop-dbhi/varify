# === Class: python::packages
#
#   Install Python packages pip and virtualenv.
#   Install Curl.
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
#   include python::packages
#
#   class{'python::packages':}
#
# === Authors
#
#   Stacey Wrazien <wraziens@email.chop.edu>
#
class python::packages{

    $opt_path = '/opt/local/bin/'
    $python_path = '/opt/local/Python-2.7.3/bin/'
    
    package{'curl':
        ensure  => present,
        require => Class['python::python_2_7_3'],
    }

    exec{'install pip':
        path    => [$python_path, $opt_path, $path], 
        command => 'curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python',
        require => [Package['curl']],
        creates => '/opt/local/Python-2.7.3/lib/python2.7/site-packages/pip'
    }

    exec{'install virtualenv': 
        path    => [$python_path, $opt_path, $path], 
        command => 'pip install virtualenv',
        require => [Exec['install pip'], Exec['install distribute']],
        creates => '/opt/local/Python-2.7.3/bin/virtualenv'
    }
    
}
