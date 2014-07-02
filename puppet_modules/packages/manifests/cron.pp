class packages::cron{
    
    package{'crontabs':
        ensure => present,
    }

    exec{'cron start':
        path => $path,
        command => "service crond start",
    }

    exec{'chkconfig cron':
        path => $path,
        command => "chkconfig --levels 235 crond on"
    }

    Package['crontabs'] -> Exec['cron start'] -> Exec['chkconfig cron']
    

}
