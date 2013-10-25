# ==== Class: utilities::wget
#
#   Executes command wget to fetch a file from the internet
#
# === Parameters
#
#   [*file*]
#       The URL of the file to fetch.
#
# === Variables
#
#   None
#
# === Examples
#
#   utilities::wget{'http://python.org/ftp/python/2.7.3/Python-2.7.3.tgz':}
#
#   utilities::wget{'wget python':
#       file => 'http://python.org/ftp/python/2.7.3/Pyhton-2.7.3.tgz'
#   }
#
# === Authors
#
#   Stacey Wrazien <wraziens@email.chop.edu>
#
define utilities::wget($file = $title, $target){
  if $file == 'false' {
    fail('utilities::wget cannot run without a specified file to fetch.')
  }
  if $target == 'false' {
    fail('utilities::wget cannot run without a target location')
}


  exec{"wget ${file}":
    path    => $path,
    command => "wget --no-check-certificate -O $target ${file}",
    creates => "$target",
  }

}

