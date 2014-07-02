class gems {
    package { 'sass':
        ensure => 'installed',
        provider => 'gem'
    }

    package {'bourbon':
        ensure => 'installed',
        provider => 'gem'
    }

}
