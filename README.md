<!-- vim: set ai ts=2 sw=2 et!: -->

devman
======

WORK IN PROGRESS
A python git repository manager.

It can be used to manage your git repositories 

 * Fork this repo
 * Create your configuration files
 * Have your team install devman from your fork
 * Stay up to date with our repository
 * Send a pull request to add new features

**Use case**

 * You have many teams working on different sets of repos and want a centralized, clear way to tell people what repo they need to clone for which project.

 * You have multiple systems and want them to always have the same repos. (ie: desktop & laptop)

 * You work on multiple projects that contain multiple repos and want to manage them from a unique tool. 

 * You are somewhat bored of cd'ing into your repos and want to control a specific repo, or group from any shell. 

 * You are most tired of clicking on your GUI to update all your repos and want to get up to speed with CLI users. ;-)

## Prerequisites

  - git is installed on your system (or msysgit)

  - python is installed on your system.

  - your github ssh access is configured for
    * key-based access or
    * https access (using a .netrc file) or 
    * using git-credential-winstore plugin (Windows)

## SETUP

  * Configure repo groups in yaml files group-name.yaml in "repos" folder
    * Each group contains a set of repos that are managed as a whole.
    * You then refer to a group of repositories when you want to do an operation.
  * When you specify no arguments, all groups are processed. 



## USAGE
### Linux / Mac

  devman -h

  # git pull --rebase for all your repos (TODO)

  devman [ff] [<group>]

  # checkout all branches to specific branch name (TODO)

  devman [co] <branch_name> [<group>] 

  # tag all repos in one group (not implemented yet)

  devman [t] <tag_name> [<group>] 

  # push all repos to origin (not implemented yet -- no upstream by default?)

  devman [p] [<group>] 

### Windows (Cygwin)
  
  C:/Python27/python.exe ./devman -h

## INSTALL
### Linux
    
  aptitude install git python-pip
  pip install gitpython

### Mac

  *Please contribute.*

### Windows (on cygwin)

Manually install msysgit

  https://code.google.com/p/msysgit/downloads/list?q=full+installer+official+git)

  https://msysgit.googlecode.com/files/Git-1.8.5.2-preview20131230.exe 

Install git-credential-winstore (to save your credentials with your session)

  http://gitcredentialstore.codeplex.com/releases/view/106064)
 
Manually install Python 2.7.6 (or version if you'd like to test it

  http://www.python.org/ftp/python/2.7.6/python-2.7.6.amd64.msi) 

Manually install dependencies in git-bash  / Cygwin

  cd /tmp

  curl -o ez_setup.py https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py 

  C:/Python27/python.exe ez_setup.py

  curl -o git-python.tar.gz https://pypi.python.org/packages/source/G/GitPython/GitPython-0.3.2.RC1.tar.gz

  tar.exe xfpv git-python.tar.gz 

  cd GitPython-0.3.2.RC1/

  C:/Python27/python.exe ./setup.py install

> We simply install git, python, SetupTools and GitPython. Beware that you might have to tweak this tool a little bit.

git-repo already exists for this, you might want to look there.
