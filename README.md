devman
======
Manage your git repositories with your Workflow in mind.

 * Fork this repo
 * Create your configuration files
 * Clone devman from your fork (you and your team)
 * Use devman
 * Stay up to date with our repository (fetch upstream)
 * Send a pull request to add new features

**Use case**

 * You have many teams working on different sets of repos and want a centralized, clear way to tell people what repo they need to clone for which project.

 * You have multiple systems and want them to always have the same repos. (ie: desktop & laptop)

 * You work on multiple projects that contain multiple repos and want to manage them from a unique tool. 

 * You are somewhat bored of cd'ing into your repos and want to control a specific repo, or group from any shell.  

 * You are most tired of clicking on your GUI to update all your repos and want to get up to speed with CLI users. ;-)

## Prerequisites

  - git is installed on your system (or msysgit on cygwin)

  - python is installed on your system.

  - your github ssh access is configured for 
    * key-based access or
    * https access (using a .netrc file) or  
    * using git-credential-winstore plugin (Windows)

## USAGE

```
devman -h

# list configured repos
devman list [<group>]

# git clone <group>
devman clone [<group>]

# git pull --ff-only 
devman ff [<group>]

#git fetch [--prune] 
devman fetch [--prune] [<group>]

# checkout all branches to specific branch name
devman co -b <branch_name> [<group>] 

# list all configured repo groups
devman ls [<group>] 

# Get the status for all repos
# <repo name> (<current branch><upstream status> <release status>)
# upstream status: see _GIT_PS1
# release status:
#  Released - All dev branch commits are merged into release and stable branches.
#  Staging - A release is staging in release branch
#  Unreleased - Dev branch contains commits not merged into release branch
devman st [<group>]
```

## INSTALL
### Linux
    
```
./install-linux.sh
cp repos.sample.yaml repos.yaml
sudo ln -s `pwd`/devman ~/bin/
```

### Mac

```
./install-mac.sh # TODO
cp repos.sample.yaml repos.yaml
sudo ln -s `pwd`/devman ~/bin/

```  

### Cygwin

./install-windows.bat # TODO
cp repos.sample.yaml repos.yaml

Manually install msysgit

    https://code.google.com/p/msysgit/downloads/list?q=full+installer+official+git)

    https://msysgit.googlecode.com/files/Git-1.8.5.2-preview20131230.exe 

Install git-credential-winstore (to save your credentials with your session)

    http://gitcredentialstore.codeplex.com/releases/view/106064)
 
Manually install Python 2.7.6 (or version if you'd like to test it with)

    http://www.python.org/ftp/python/2.7.6/python-2.7.6.amd64.msi) 
