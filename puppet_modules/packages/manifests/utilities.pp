#installs 
#
#OS Support:: centOS
#
#Sample Usage::
#
# include utilities
#

class packages::utilities{
  
  	package{'mlocate':
     	ensure => present,
  	}

	
}