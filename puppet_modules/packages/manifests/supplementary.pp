#installs 
#
#OS Support:: centOS
#
#Sample Usage::
#
# include supplementary
#

class packages::supplementary{
  
  $supplementary_software = ["httpd-devel", "openssl-devel", "ncurses-devel","rpm-devel","apr-util-devel","apr-devel","glibc-devel","memcached","readline-devel","bzip2","bzip2-devel","bzip2-libs","libpng-devel","openldap-devel","freetype","freetype-devel","lapack-devel","blas-devel","libgfortran","gcc-gfortran", "gcc", 'gcc-c++']

  package { $supplementary_software: ensure => "installed" }

  #package{'git' :
  #      ensure 		=> present,
  #      require		=> Package[$supplementary_software],
  #  }
    	
	
}

#Need to add gfortan and g++ and nginx
