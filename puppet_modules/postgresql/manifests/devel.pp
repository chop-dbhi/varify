class postgresql::devel {
    #file { 'postgresql.repo':
   #         path    => "/etc/yum.repos.d/postgresql.repo",
   #         source  => 'puppet:///modules/postgresql/postgresql.repo',
#         }

    #Add postgres binaries to the path so other tools can find them
    file {'postgresql.sh':
          path => '/etc/profile.d/postgresql.sh',
          source => 'puppet:///modules/postgresql/postgresql.sh'
    } 
 
    #Need to do this explicitly since the postgres yum repo is busted

    package {'postgresql92-libs':
              ensure => 'installed',
              source => 'http://yum.postgresql.org/9.2/redhat/rhel-6-x86_64/postgresql92-libs-9.2.8-1PGDG.rhel6.x86_64.rpm',
              provider => 'rpm'

    }
            
    package {'postgresql92':
              ensure => 'installed',
              source => 'http://yum.postgresql.org/9.2/redhat/rhel-6-x86_64/postgresql92-9.2.8-1PGDG.rhel6.x86_64.rpm',
              provider => 'rpm',
              require => Package['postgresql92-libs']
    }

    package {'postgresql92-devel':
              ensure => 'installed',
              source => 'http://yum.postgresql.org/9.2/redhat/rhel-6-x86_64/postgresql92-devel-9.2.8-1PGDG.rhel6.x86_64.rpm',
              provider => 'rpm',
              require => Package['postgresql92']
              }



    
}
