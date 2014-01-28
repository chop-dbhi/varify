group { "puppet":
   ensure => "present",
}

include packages::supplementary
include python
include gems
include postgresql::devel
include nodejs::coffee-script
include redis

#Create the virtual environment for varify

exec{"create virtualenv":
    cwd     => '/home/vagrant/',
    path => $path,
    command => '/opt/local/Python-2.7.3/bin/virtualenv --no-site-packages varify-env',
    user => 'vagrant',
    group => 'vagrant',
    creates => '/home/vagrant/varify-env',
    require => [Exec['adjust path for python'], Exec ['install virtualenv']]
}

file { '/home/vagrant/varify-env/varify':
   ensure => 'link',
   target => '/vagrant',
   owner => 'vagrant',
   group => 'vagrant',
   require => Exec ['create virtualenv'],
}

#Make sure memcached is running
exec{"memcached":
    path=>$path,
    command => "/etc/init.d/memcached start",
    require => Package['memcached']
}

service { "memcached":
  enable => true,
  require => Package['memcached']
}
