class nodejs::coffee-script{
    include nodejs::nodejs_0_8_14
	exec {'install cofee-script':
	     path    => $path,
	     command => '/usr/local/bin/npm install -g coffee-script',
		 creates => '/usr/local/lib/node_modules/coffee-script',
		 require => Exec['make nodejs']
	 }

}