#!/usr/bin/env python3
import os
import platform
from argparse import ArgumentParser
from argparse import RawTextHelpFormatter

from git import GitCommandError
from git import InvalidGitRepositoryError
from git import NoSuchPathError
from git import Repo
from git.util import RemoteProgress

from configparser import ConfigParser

import yaml
import subprocess
import pprint as pp

# defaults
install_dir = os.path.dirname(os.path.realpath(__file__))
default_config_file = os.path.join(install_dir, 'devman.conf')
default_repo_conf_file = os.path.join(install_dir, 'repos.yaml')
default_override_conf_file = 'devman.local.conf'


# Utils
def flatten(lst):
    return sum(([x] if not isinstance(x, list) else flatten(x) for x in lst),
               [])


def sh(cmd):
    try:
        output = subprocess.check_output(cmd,
                                         shell=True,
                                         stderr=subprocess.STDOUT)
    except Exception as e:
        output = str(e)
    return output


debug = False


class DisProgress(RemoteProgress):
    if debug:
        @staticmethod
        def line_dropped(line):
            print('{}'.format(line))

        @staticmethod
        def update(op_code, cur_count, max_count=None, message=''):
            print('{0} {1}/{2} {3}'.format(op_code,
                                           cur_count,
                                           max_count,
                                           message))


###
class DevMan:

    def __init__(self):
        self.args = self.argument_parser()
        self.conf = Conf(self.args.config, self.args.override)
        self.config = self.conf.get_overriden_config()
        self.command = self.args.cmd

        self.repo_conf_file = self.args.repofile
        stream = open(self.repo_conf_file, 'r')
        self.repo_list = yaml.safe_load(stream)

        self.dev_branch = self.config['default']['dev_branch']
        self.release_branch = self.config['default']['release_branch']
        self.stable_branch = self.config['default']['stable_branch']

        target_os = platform.system()

        # TODO: use config
        if target_os == 'Linux':
            self.repo_clone_path = os.path.expanduser(
                self.config['default']['repo_clone_path'])
            self.git_url = self.config['default']['git_baseurl']
            self.git_binary = sh("which git")
            self.git_login = sh("ssh git@github.com")
        elif target_os == 'Windows':
            self.repo_clone_path = os.path.expanduser(
                self.config['windows']['repo_clone_path'])
            self.git_url = self.config['windows']['git_baseurl']
            self.git_binary = sh("c:/vagrant/embedded/mingw/bin/which.exe git")
            self.git_login = sh("ssh git@github.com")
        elif target_os == 'Darwin':
            self.repo_clone_path = os.path.expanduser(
                self.config['default']['repo_clone_path'])
            self.git_url = self.config['default']['git_baseurl']
            self.git_binary = sh("which git")
            self.git_login = sh("ssh git@github.com")
        elif target_os.startswith('CYGWIN_NT-'):
            self.repo_clone_path = os.path.expanduser(
                self.config['cygwin']['repo_clone_path'])
            self.git_url = self.config['default']['git_baseurl']
            self.git_binary = sh("which git")
            self.git_login = sh("ssh git@github.com")
        else:
            print("OS not supported yet: {}".format(target_os))
            exit(1)

        # check if github is configured
        if self.git_binary.find(b"git") == -1:
            print("Please install git before you proceed any further.")
            exit(1)

        # create install path if it doesn't already exist
        if not os.path.isdir(self.repo_clone_path):
            sh("mkdir -p {}".format(self.repo_clone_path))

        # process given args before loading repos
        if self.args.all:
            self.groups = self.get_all_groups()
        elif not flatten(self.args.groups):
            self.groups = []
            self.groups.append(self.config['default']['repo_group'])
        else:
            self.groups = flatten(self.args.groups)

        # load repos definition
        self.repos = self.load_repos()

    def argument_parser(self):
        parser = ArgumentParser(description='DevMan')

        parser.add_argument('-c', '--config',
                            action='store',
                            default=default_config_file,
                            help='Set config file location (default: install_dir/devman.conf)',
                            dest='config')

        parser.add_argument('-o', '--override',
                            action='store',
                            default=default_override_conf_file,
                            help='Set config override location (default: install_dir/devman.local.conf)',
                            dest='override')

        parser.add_argument('-b', '--base',
                            action='store',
                            default=default_repo_conf_file,
                            help='Set base location (default: <read-config>',
                            dest='base')

        parser.add_argument('-r', '--repofile',
                            action='store',
                            default=default_repo_conf_file,
                            help='Set repofile location (default: install_dir/repos.yaml)',
                            dest='repofile')

        parser.add_argument('-a', '--all',
                            action='store_true',
                            default=False,
                            help='Process all known repogroups',
                            dest='all')

        subparsers = parser.add_subparsers(
            title='cmd',
            description="Command to perform on all repositories.",
            dest='cmd')
        subparsers.required = True

        groups_args = dict(metavar='RepoGroup',
                           action='append',
                           type=str, nargs='*',
                           help='a group of git repos to work on')

        sp_clone = subparsers.add_parser('clone', description='git clone on selected repo-groups')
        sp_clone.add_argument('groups', **groups_args)

        sp_co = subparsers.add_parser('co', description='git checkout -b branch origin/branch on selected repo-groups')
        sp_co.add_argument('-b', '--branch', action="store", dest="branch",
                           help="Pass the --branch option when checking out branches")
        sp_co.add_argument('groups', **groups_args)

        sp_ls = subparsers.add_parser('ls', description='List configured repo-groups')
        sp_ls.add_argument('groups', **groups_args)

        sp_fetch = subparsers.add_parser('fetch')
        sp_fetch.add_argument('-p', '--prune',
                              action="store_true",
                              dest="prune",
                              help="Pass the --prune option when doing git fetch")
        sp_fetch.add_argument('groups', **groups_args)

        sp_ff = subparsers.add_parser('ff', description='git pull --ff-only on selected repo-groups')
        sp_ff.add_argument('groups', **groups_args)

        # devman st
        sp_st = subparsers.add_parser('st',
                                      description='''Show status for all repos
<repo name> (<current branch><upstream status> <release status>)
 upstream status: see _GIT_PS1
 release status:
     Released: All dev branch commits have been merged into release and stable
               branches.
     Staging: A release is staged in release branch
     Unreleased: Dev branch contains commits not merged into release branch''',
                                      formatter_class=RawTextHelpFormatter)
        sp_st.add_argument('groups', **groups_args)

        # devman exec
        sp_exec = subparsers.add_parser('exec',
                    description='Execute command --exec on selected repo-groups. Current dir is set to the repo path.')
        sp_exec.add_argument('-e', '--exec',
                             action="store",
                             dest="execCmd",
                             help="Pass the --exec option to execute commands on repogroups")
        sp_exec.add_argument('groups', **groups_args)

        return parser.parse_args()

    def get_all_groups(self):
        all_groups = []
        repo_conf = self.repo_conf_file
        stream = open(repo_conf, 'r')
        repo_list = yaml.safe_load(stream)
        for group_name, group_config in repo_list.items():
            all_groups.append(group_name)
        return all_groups

    #
    # return repos from group
    #
    def get_repos(self):
        all_repos = {}
        for g in self.groups:
            all_repos[g] = self.repos[g]
        return all_repos

    def iter_repos(self, create=False, clean=True):
        for group, repo_definition in self.get_repos().items():
            for repo_name, repo_url in repo_definition.items():
                if group == 'root':
                    repo_path = os.path.join(self.repo_clone_path, repo_name)
                else:
                    repo_path = os.path.join(self.repo_clone_path, group,
                                             repo_name)
                try:
                    repo = Repo(repo_path)
                    if repo.bare is True:
                        print("Can't process bare repo: {}".format(
                            repo_name))
                        pass
                    elif repo.is_dirty():
                        if clean:
                            print("Can't process dirty repo: {}".format(
                                repo_name))
                            pass
                        else:
                            yield repo_name, repo_path, repo_url, repo
                    else:
                        yield repo_name, repo_path, repo_url, repo
                except InvalidGitRepositoryError:
                    print("Error: Repository {} isn't a git repo. Remove folder and try again.".format(repo_name))
                    exit(1)
                except NoSuchPathError:
                    if create:
                        try:
                            print("{}: cloning".format(repo_name))
                            this_repo = Repo.clone_from(
                                repo_url, repo_path,
                                progress=DisProgress()
                            )
                            for submodule in this_repo.submodules:
                                print("Initializing submodule: {}".format(
                                    str(submodule)))
                                submodule.update(progress=DisProgress())
                        except GitCommandError as e:
                            if e.status == 128:
                                print("Error: Can't access repository {} on remote.".format(repo_name))
                            else:
                                raise e
                    else:
                        print("{}: not cloned, skipped".format(repo_name))

    # Load git repos definition from yaml file
    # Merge configuration layer from default config
    def load_repos(self):

        # load only configured groups from config file
        repos = {}
        for group in self.groups:
            if group in self.repo_list:
                updated_repos = {}
                for repo_name, repo_url in self.repo_list[group].items():
                    remote_url = self.git_url + repo_url
                    updated_repos[repo_name] = remote_url
                repos[group] = updated_repos
            else:
                raise Exception("Error: Couldn't find group {} in {}.".format(group, self.repo_conf_file))
        return repos

    #
    # repo actions
    #
    def clone(self):
        repos = iter(self.iter_repos(create=True))
        while True:
            try:
                next(repos)
            except StopIteration:
                break


    # checkout branch
    def co(self, branch):
        for name, path, url, repo in self.iter_repos():
            remote_branches = [remote.strip() for remote in repo.git.branch(
                r=True).splitlines()]
            local_branches = repo.branches
            current_branch = str(repo.active_branch)
            remote_branch = "origin/" + branch

            # this remote branch exists
            if remote_branch in remote_branches:
                # we are not already on this branch
                if branch != current_branch:
                    print("{}: checking out {}".format(branch, name))
                    if branch in local_branches:
                        repo.git.checkout(branch)
                    else:
                        repo.git.checkout(remote_branch, b=branch)
                else:
                    pass

    def st(self):
        # Make sure remote branches are updated
        for name, path, url, repo in self.iter_repos(clean=False):
            try:
                repo.remotes.origin.fetch(prune=False, progress=DisProgress())
            except GitCommandError as e:
                if e.status == 128:
                    print("{}: error: can't access repository on remote.".format(
                        name))
                else:
                    raise e

            dirty = ""
            staged = ""

            [status, _, _] = repo.git.execute(
                ["git", "diff", "--no-ext-diff", "--quiet", "--exit-code"],
                with_extended_output=True,
                with_exceptions=False)
            if status != 0:
                dirty = "*"

                [status, _, _] = repo.git.execute(
                    ["git", "rev-parse", "--quiet", "--verify", "HEAD", "--"],
                    with_extended_output=True,
                    with_exceptions=False)
            if status == 0:
                [status, _, _] = repo.git.execute(
                    ["git", "diff-index", "--cached", "--quiet", "HEAD", "--"],
                    with_extended_output=True,
                    with_exceptions=False)
                if status == 1:
                    staged = "+"
            else:
                staged = "#"

            if not repo.head.is_detached:
                rev = "origin/{}...HEAD".format(repo.head.reference.name)
            else:
                rev = "refs/tags/{}...HEAD".format(repo.git.describe('--tags', '--abbrev=0'))

            try:
                out = repo.git.execute(["git", "rev-list", "--count", "--left-right", rev], with_exceptions=True)
            except GitCommandError as e:
                out = False
                if e.status != 128:
                    raise e

            upstream_status = u"\u2209".encode('utf-8')
            if out:
                [behind, ahead] = out.split("\t")
                if behind == "0" and ahead == "0":
                    upstream_status = "="
                elif behind == "0":
                    upstream_status = ">"
                elif ahead == "0":
                    upstream_status = "<"
                else:
                    upstream_status = "<>"

            release_ahead = ""
            stable_ahead = ""

            rev = "origin/{0}...origin/{1}".format(
                self.release_branch, self.dev_branch)
            grep_pattern = "^(?!Merge branch '{0}').+$".format(self.release_branch)
            out = repo.git.execute(
                ["git", "rev-list", "--count", "--left-right", rev, '--grep',
                 grep_pattern],
                with_exceptions=False)
            if out != "":
                [_, release_ahead] = out.split("\t")

            rev = "origin/{0}...origin/{1}".format(
                self.stable_branch, self.release_branch)
            out = repo.git.execute(
                ["git", "rev-list", "--count", "--left-right", rev],
                with_exceptions=False)

            if out != "":
                [_, stable_ahead] = out.split("\t")

            if release_ahead == "0" and stable_ahead == "0":
                release_status = "Released"
            elif release_ahead == "0":
                release_status = "Staging"
            elif stable_ahead == "0":
                release_status = "Unreleased"
            else:
                release_status = "Staging+Unreleased"

            if not repo.head.is_detached:
                rev = repo.head.reference.name
            else:
                rev = "{{({})}}".format(repo.git.describe('--tags', '--abbrev=0'))

            print("{0} ({1}{2}{3} {4} {5})".format(name,
                                                 rev,
                                                 dirty,
                                                 staged,
                                                 upstream_status,
                                                 release_status))
            if repo.untracked_files:
                for filename in repo.untracked_files:
                    print("  + {}".format(filename))

    def ff(self):
        for name, path, url, repo in self.iter_repos():
            print("{}: fast-forward from origin".format(name))
            if not repo.head.is_detached:
                cur_branch = repo.head.reference.name
            else:
                cur_branch = repo.git.describe()

            o = repo.remotes.origin
            try:
                o.pull(cur_branch, ff_only=True, progress=DisProgress())
            except GitCommandError as e:
                if e.status == 1:
                    print("Error: Repository {} or branch {} doesn't exist on remote.".format(name, cur_branch))
                elif e.status == 2:
                    print("Error: Branch {} doesn't exist on remote. Please push first.".format(cur_branch))
                else:
                    raise e

    def fetch(self, prune):
        for name, path, url, repo in self.iter_repos():
            try:
                if prune:
                    print("{}: fetch prune ".format(name))
                else:
                    print("{}: fetch ".format(name))
                repo.remotes.origin.fetch(prune=prune, progress=DisProgress())
            except AssertionError as e:
                if prune:
                    print("Assertion error probably due to pruned branch")
                else:
                    raise e
            except GitCommandError as e:
                if e.status == 128:
                    print("Error: Can't access repository {} on remote.".format(name))
                else:
                    raise e

    def repo_exec(self, cmd):
        if not cmd:
            print("exec expects --exec option. See `devman exec --help`")
        else:
            for name, path, url, repo in self.iter_repos():
                print("{}: execute command {}".format(name, cmd))
                subprocess.Popen(cmd, cwd=path, shell=True).communicate()

    def ls(self):
        print('------------------------------------------------')
        print('| Available                                    |')
        print('------------------------------------------------')
        pp.pprint(self.repo_list)
        print('------------------------------------------------')
        print('| Now                                          |')
        print('------------------------------------------------')
        pp.pprint(self.get_repos())

    def run(self):
        if self.command == 'ls':
            self.ls()
        elif self.command == 'clone':
            self.clone()
        elif self.command == 'fetch':
            self.fetch(self.args.prune)
        elif self.command == 'ff':
            self.ff()
        elif self.command == 'co':
            self.co(self.args.branch)
        elif self.command == 'st':
            self.st()
        elif self.command == 'exec':
            self.repo_exec(self.args.execCmd)
        else:
            print("Error: Command not found: {}".format(self.command))
            exit(1)


# Thx stackoverflow!
def merge(a, b, path=None):
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass
            else:
                a[key] = b[key]
        else:
            a[key] = b[key]
    return a


class Conf:
    #
    # Load default configurations from devman.conf ini file
    #
    def __init__(self,
                 config_path,
                 override_path
                 ):

        self.config = self.load_conf_file(config_path)
        self.override = self.load_conf_file(override_path)

    def load_conf_file(self, filename):
        parser = ConfigParser()
        parser.read(filename)
        conf = {}
        for section_name in parser.sections():
            section_confs = {}
            for name, value in parser.items(section_name):
                section_confs[name] = value
            conf[section_name] = section_confs
        return conf

    def get_overriden_config(self):
        return merge(self.config, self.override)


def main():
    devman = DevMan()
    devman.run()


# defaults
######
if __name__ == "__main__":
    main()
