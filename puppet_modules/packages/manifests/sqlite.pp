#installs 
#
#OS Support:: centOS
#
#Sample Usage::
#
# include sqlite
#

class packages::sqlite{
  
  $sqlite_software = [ "sqlite","sqlite-devel" ]

  package { $sqlite_software: ensure => "installed" }

  #package{'sqlite' :
  #      ensure 		=> present,
  #      require		=> Package[$sqlite_software_software],
  #  }
    	
	
}