# == Class: devman
#
# Full description of class devman here.
#
# === Parameters
#
# Document parameters here.
#
# [*sample_parameter*]
#   Explanation of what this parameter affects and what it defaults to.
#   e.g. "Specify one or more upstream ntp servers as an array."
#
# === Variables
#
# Here you should define a list of variables that this module would require.
#
# [*sample_variable*]
#   Explanation of how this variable affects the funtion of this class and if
#   it has a default. e.g. "The parameter enc_ntp_servers must be set by the
#   External Node Classifier as a comma separated list of hostnames." (Note,
#   global variables should be avoided in favor of class parameters as
#   of Puppet 2.6.)
#
# === Examples
#
#  class { 'devman':
#    servers => [ 'pool.ntp.org', 'ntp.local.company.com' ],
#  }
#
# === Authors
#
# Author Name <author@domain.com>
#
# === Copyright
#
# Copyright 2015 Your name here, unless otherwise noted.
#
class devman ($folder, $user, $config_file){

  # install devman
  case $operatingsystem {
    'Darwin'            : { $devman_install = "${folder}/devman/install-mac.sh" }
    'RedHat', 'CentOS'  : { $devman_install = "${folder}/devman/install-linux.sh" }
    /^(Debian|Ubuntu)$/ : { $devman_install = "${folder}/devman/install-linux.sh" }
    default             : { fail('not supported') }
  }

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

  class { 'python':
    version    => 'system',
    pip        => 'present',
  }
  python::pip { 'pyyaml':
  }
  python::pip { 'gitpython':
  }

  file { "${folder}/devman/repos.yaml":
    ensure => 'link',
    target => $config_file,
  }
}
