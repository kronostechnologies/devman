# install devman
class devman ($folder, $user, $config_file){

  case $operatingsystem {
    'Darwin'            : { $devman_install = "${folder}/devman/install-mac.sh" }
    'RedHat', 'CentOS'  : { $devman_install = "${folder}/devman/install-linux.sh" }
    /^(Debian|Ubuntu)$/ : { $devman_install = "${folder}/devman/install-linux.sh" }
    default             : { fail('not supported') }
  }

  class { 'python':
    version    => 'system',
    pip        => 'present',
  } ->
  python::pip { 'pyyaml':
  } ->
  python::pip { 'gitpython':
  } ->
  vcsrepo { "${folder}/devman":
    ensure   => present,
    provider => git,
    user     => $user,
    source   => 'git@github.com:kronostechnologies/devman.git',
  } ->
  exec { $devman_install:
    user    => $user,
    creates => "/home/${user}/bin/devman"
  }

  file { "${folder}/devman/repos.yaml":
    ensure => 'link',
    target => $config_file,
  }

}
