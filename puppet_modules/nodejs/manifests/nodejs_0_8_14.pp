class nodejs::nodejs_0_8_14 {
	utilities::wget{'nodejs':
	     file    => 'http://nodejs.org/dist/v0.8.14/node-v0.8.14.tar.gz',
			target => '/tmp/node-v0.8.14.tar.gz'
	 }

	 utilities::untar{'nodejs': 
	     file    => "node-v0.8.14.tar.gz",
	     require => Utilities::Wget['nodejs'],
	 }

	 exec{'config nodejs':
	     path    => $path,
	     cwd     => '/tmp/node-v0.8.14/',
	     command => '/bin/sh configure',
	     creates => '/tmp/node-v0.8.14/Makefile',
	     require => Utilities::Untar['nodejs']
	 }

	 exec {'make nodejs':
	     path    => $path,
	     cwd     => '/tmp/node-v0.8.14/',
	     command => 'make && make install',
	     require => Exec['config nodejs'],
		 creates => '/usr/local/bin/node',
	 }


}
