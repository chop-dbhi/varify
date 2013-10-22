#installs 
#
#OS Support:: centOS
#
#Sample Usage::
#
# include utilities
#

class packages::git{
  
  $git_software = [ "libcurl-devel", "expat-devel", "gettext-devel",openssl-devel,zlib-devel ]

  package { $git_software: ensure => "installed" }

  package{'git' :
        ensure 		=> present,
        require		=> Package[$git_software],
    }
    	
	
}