"""Express Config Module"""
import os
import sys
import tarfile
import shutil
from os.path import expanduser
import requests
import click

from .modules.util import Pf9ExpVersion

from .cli.commands import version
from .config.commands import config
from .cluster.commands import cluster


@click.group()
@click.version_option(message='%(version)s')
@click.pass_context
def cli(ctx):
    """Express-CLI
    A CLI for Platform9 Express."""
    # Set Global Vars into context objs
    if ctx.obj is None:
        ctx.obj = dict()
    ctx.obj['pf9_venv'] = sys.prefix
    ctx.obj['venv_activate'] = "{}/bin/activate".format(ctx.obj['pf9_venv'])
    ctx.obj['venv_python'] = sys.executable
    ctx.obj['home_dir'] = expanduser("~")
    ctx.obj['pf9_dir'] = os.path.join(ctx.obj['home_dir'], 'pf9/')
    ctx.obj['pf9_log_dir'] = os.path.join(ctx.obj['pf9_dir'], 'log')
    ctx.obj['pf9_db_dir'] = os.path.join(ctx.obj['pf9_dir'], 'db')
    ctx.obj['pf9_exp_dir'] = os.path.join(ctx.obj['pf9_dir'], 'pf9-express/')
    ctx.obj['pf9_exp_conf_dir'] = os.path.join(ctx.obj['pf9_exp_dir'], 'config/')
    ctx.obj['exp_config_file'] = os.path.join(ctx.obj['pf9_exp_conf_dir'], 'express.conf')
    ctx.obj['pf9_exp_ansible_runner'] = os.path.join(ctx.obj['pf9_exp_dir'],
                                                     'express', 'pf9-express')

# Add top-level commands to cli.
# Any commands defined here or added will be toplevel
cli.add_command(version)
cli.add_command(config)
cli.add_command(cluster)


@cli.command('init')
@click.pass_obj
def init(obj):
    """Initialize Platform9 Express."""

    access_rights = 0o755
    pf9_dir = obj['pf9_dir']
    pf9_exp_dir = obj['pf9_exp_dir']
    target_path = pf9_dir + 'express.tar.gz'

    if not os.path.exists(pf9_exp_dir):
        get_exp_ver = Pf9ExpVersion()
        current_express_ver = get_exp_ver.get_release_json()['version']
        url = current_express_ver['url_tar']

        if not os.path.exists(pf9_dir):
            try:
                os.mkdir(pf9_dir, access_rights)
            except OSError:
                print("Creation of the directory %s failed" % pf9_dir)
            else:
                print("Successfully created the directory %s " % pf9_dir)

        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(target_path, 'wb') as raw_tar:
                raw_tar.write(response.raw.read())

        tar = tarfile.open(target_path, "r:gz")
        tar.extractall(pf9_exp_dir)
        tar.close()

        with open(pf9_exp_dir + 'version', 'w') as file:
            file.write(current_express_ver + '\n')
            file.close()

        for sub_dir in next(os.walk(pf9_exp_dir))[1]:
            if 'platform9-express-' in sub_dir:
                os.rename(pf9_exp_dir + sub_dir, pf9_exp_dir + 'express')

        click.echo('Platform9 Express initialization complete')
    else:
        click.echo('Platform9 Express already initialized')


@cli.command('upgrade')
@click.pass_obj
def upgrade(obj):
    """Upgrade Platform9 Express."""

    ver = Pf9ExpVersion()
    click.echo(ver.get_release_json())

    r = requests.get('https://api.github.com/repos/platform9/express/releases/latest')
    response = r.json()
    url = response['tarball_url']
    new_version = response['tag_name']
    access_rights = 0o755
    pf9_dir = obj['pf9_dir']
    pf9_exp_dir = obj['pf9_exp_dir']
    target_path = pf9_dir + 'express.tar.gz'

    with open(pf9_exp_dir + 'version', 'r') as v:
        current_version = v.readline()
        current_version = current_version.strip()
        v.close()

    if current_version != new_version:
        click.echo("A newer version of Platform9 Express is avialable")
        if not os.path.exists(pf9_exp_dir):
            try:
                os.mkdir(pf9_exp_dir, access_rights)
            except OSError:
                print("Creation of the directory %s failed" % pf9_exp_dir)
            else:
                print("Successfully created the directory %s " % pf9_exp_dir)

        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(target_path, 'wb') as f:
                f.write(response.raw.read())

        tar = tarfile.open(target_path, "r:gz")
        tar.extractall(pf9_exp_dir)
        tar.close()

        os.rename(pf9_exp_dir + 'express', pf9_exp_dir + 'express-bak')

        for sub_dir in next(os.walk(pf9_exp_dir))[1]:
            if 'platform9-express-' in sub_dir:
                os.rename(pf9_exp_dir + sub_dir, pf9_exp_dir + 'express')

        shutil.rmtree(pf9_exp_dir + 'express-bak')

        with open(pf9_exp_dir + 'version', 'w') as file:
            file.write(new_version + '\n')
            file.close()

        click.echo('Platform9 Express upgrade complete')

    else:
        click.echo('Platform9 Express is already the latest version')
