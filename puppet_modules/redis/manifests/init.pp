class redis{

    utilities::wget{'redis':
        file    => 'http://download.redis.io/releases/redis-2.8.4.tar.gz',
		target => '/tmp/redis-2.8.4.tar.gz'
    }

    utilities::untar{'redis':
        file    => "redis-2.8.4.tar.gz",
        require => Utilities::Wget['redis'],
    }

    exec {'make redis':
        cwd     => '/tmp/redis-2.8.4/',
        path    => $path,
        command => 'make && make install',
        require => Utilities::Untar['redis'],
    }
}
