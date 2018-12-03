# coding: utf-8
"""Setup post actions, used in main setup.py."""

import os
import shutil
import sys
from setuptools.command.install import install
from stakkr import file_utils


try:
    import click

    @click.command(help="""Initialize for the first time stakkr by copying
templates and directory structure""")
    @click.option('--force', '-f', help="Force recreate directories structure", is_flag=True)
    def init(force: bool):
        """CLI Entry point, when initializing stakkr manually."""
        config_file = os.getcwd() + '/stakkr.yml'
        if os.path.isfile(config_file) and force is False:
            click.secho('Config file (stakkr.yml) already present. Leaving.', fg='yellow')
            return

        msg = "Config (stakkr.yml) not present, don't forget to create it"
        click.secho(msg, fg='yellow')
        _post_install(force)

except ImportError:
    def init():
        """If click is not installed, display that message."""
        print('Stakkr has not been installed yet')
        sys.exit(1)


def _post_install(force: bool = False):
    """Create templates (directories and files)."""
    print('Post Installation : create templates')

    project_dir = os.getcwd()
    # If already installed don't do anything
    if os.path.isfile(project_dir + '/stakkr.yml'):
        return

    required_dirs = [
        'conf/mysql-override',
        'conf/php-fpm-override',
        'conf/xhgui-override',
        'data',
        'home/www-data',
        'home/www-data/bin',
        'logs',
        'plugins',
        'services',
        'www'
    ]
    for required_dir in required_dirs:
        _create_dir(project_dir, required_dir, force)

    required_tpls = [
        # 'bash_completion', # How to do with a system wide installation ?
        'stakkr.yml.tpl',
        'conf/mysql-override/mysqld.cnf',
        'conf/php-fpm-override/example.conf',
        'conf/php-fpm-override/README',
        'conf/xhgui-override/config.php',
        'home/www-data/.bashrc'
    ]
    for required_tpl in required_tpls:
        _copy_file(project_dir, required_tpl, force)


def _create_dir(project_dir: str, dir_name: str, force: bool):
    dir_name = project_dir + '/' + dir_name.lstrip('/')
    if os.path.isdir(dir_name) and force is False:
        return

    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)


def _copy_file(project_dir: str, source_file: str, force: bool):
    full_path = file_utils.get_file('tpls', source_file)
    dest_file = project_dir + '/' + source_file
    if os.path.isfile(dest_file) and force is False:
        print('  - {} exists, do not overwrite'.format(source_file))
        return

    print('  - {} written'.format(source_file))
    try:
        shutil.copy(full_path, dest_file)
    except Exception:
        msg = "Error trying to copy {} .. check that the file is there ...".format(full_path)
        print(msg, file=sys.stderr)


class StakkrPostInstall(install):
    """Class called by the main setup.py."""

    def __init__(self, *args, **kwargs):
        """Inherit from setup install class and ensure we are in a venv."""
        super(StakkrPostInstall, self).__init__(*args, **kwargs)

        try:
            file_utils.find_project_dir()
            _post_install(False)
        except OSError:
            msg = 'You must run setup.py from a virtualenv if you want to have'
            msg += ' templates installed'
            print(msg)
