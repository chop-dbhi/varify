# == Class: utilities::untar
#
#   Untar a file
#
# === Parameters
#
#   [*file*]
#       The tar file to untar.
#
# === Variables
#
#   None
#
# === Examples
#
#   utilities::untar{'Python-2.7.3.tgz':}
#
#   utilities::untar{'python':
#     file => 'Python-2.7.3.tgz',
#   }
#
# === Authors
#
#   Stacey Wrazien <wraziens@email.chop.edu>
#
define utilities::untar($file = $title){
  case $file{
    /\.tgz$|\.tar\.gz$|\.tar$/: {
      
      exec{"untar ${file}":
        path    => $path,
        cwd     => '/tmp/',
        command => "tar xvzf ${file}",
      }
    
    }
    'false': {
        fail('Please specify a file to untar.')
    }
    default:{
        fail("Cannot untar. Unrecognized file type ${file}")
    }
  }
}

