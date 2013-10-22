define packages::timezone(
    $zone = $title,
){
    file{"timezone ${zone}":
        ensure=>link,
        target =>  "/usr/share/zoneinfo/${zone}",
        path => "/etc/localtime",
    }
}
