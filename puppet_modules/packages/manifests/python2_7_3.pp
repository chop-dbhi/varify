#installs 
#
#OS Support:: centOS
#
#Sample Usage::
#
# 
#

class packages::python2_7_3{

    define get($file = $title){
        exec{"get ${file}":
            path => $path,
            cwd => "/home/vagrant/software/",
            command => "wget ${file}",
        }
    }

    define untar($file = $title){
        exec{"untar ${file}":
            path => $path,
            cwd => "/home/vagrant/software/",
            command => "tar xvzf ${file}",
        }
    }

    get{"python":
        file => "http://python.org/ftp/python/2.7.3/Python-2.7.3.tgz",
    }

    untar{"python": 
        file => "Python-2.7.3.tgz",
    }

    exec{'config python':
        path => $path,
        cwd => "/home/vagrant/software/Python-2.7.3/",
        command => "/bin/sh ./configure --prefix=/usr/local/python27 --enable-shared --enable-bz2",
        timeout	=> 400,
    }

    exec {'make python':
        path => $path,
        cwd => "/home/vagrant/software/Python-2.7.3/",
        command => "make && make install",
        timeout	=> 1200,
        logoutput=> on_failure,
    }

    $usr_path = "/usr/local/bin/"
    $python_path = "/usr/local/Python-2.7.3/bin/"

    exec{'adjust path':
        path => $path,
        cwd => "/home/vagrant",
        command => "echo \"export PATH='${usr_path}:\$PATH\'\" >> .bashrc",
    }
    
    exec{'adjust path for python':
        path => $path,
        cwd => "/home/vagrant",
        command => "echo \"export PATH='${python_path}:\$PATH'\" >> .bashrc",
    }

    get{"distribute":
        file => "http://pypi.python.org/packages/source/d/distribute/distribute-0.6.27.tar.gz",
    }

    untar{"distribute":
        file => "distribute-0.6.27.tar.gz",
    }
    
    exec{"install distribute":
        path => "${python_path}:${usr_path}:${path}",
        cwd => "/home/vagrant/software/distribute-0.6.27/",
        command => "python setup.py install",
    }

	
	
	define line($file, $line, $ensure = 'present') {
    case $ensure {
        default : { err ( "unknown ensure value ${ensure}" ) }
        present: {
            exec { "/bin/echo '${line}' >> '${file}'":
                unless => "/bin/grep -qFx '${line}' '${file}'"
            }
        }
        absent: {
            exec { "/bin/grep -vFx '${line}' '${file}' | /usr/bin/tee '${file}' > /dev/null 2>&1":
              onlyif => "/bin/grep -qFx '${line}' '${file}'"
            }

            # Use this resource instead if your platform's grep doesn't support -vFx;
            # note that this command has been known to have problems with lines containing quotes.
            # exec { "/usr/bin/perl -ni -e 'print unless /^\\Q${line}\\E\$/' '${file}'":
            #     onlyif => "/bin/grep -qFx '${line}' '${file}'"
            # }
          }
       }
	}
	
	
	
	
    Get['python'] -> Untar['python'] -> Exec['config python'] ->
    Exec['make python'] -> Exec['adjust path'] -> Exec['adjust path for python'] -> 
    Get['distribute'] -> Untar['distribute'] -> Exec['install distribute'] 

}