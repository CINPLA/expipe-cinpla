import pytest
import expipe
import sys
import os.path as op
import click
from click.testing import CliRunner

expipe.ensure_testing()

sys.path.append(expipe.config.config_dir)
if not op.exists(op.join(expipe.config.config_dir, 'expipe_params.py')):
    raise IOError('No "expipe_params.py" found.')
from expipe_params import (PAR.TEMPLATES, PAR.UNIT_INFO, PAR.POSSIBLE_TAGS,
                           PAR.POSSIBLE_LOCATIONS, OBLIGATORY_TAGS)

# TODO ADD ALL PAR.TEMPLATES

PROJECT_ID = PAR.PROJECT_ID
ACTION_ID = 'action-plugin-test'
MODULE_ID = 'module-plugin-test'
RAT_ID = 'test-rat'


def pytest_namespace():
    return {"PROJECT_ID": PROJECT_ID,
            "ACTION_ID": ACTION_ID,
            "MODULE_ID": MODULE_ID,
            "RAT_ID": RAT_ID,
            "USERNAME": PAR.USERNAME,
            "PAR.POSSIBLE_TAGS": PAR.POSSIBLE_TAGS,
            "OBLIGATORY_TAGS": OBLIGATORY_TAGS}


@click.group()
@click.pass_context
def cli(ctx):
    pass


def run_command(command_list, inp=None):
    result = CliRunner().invoke(cli, command_list, input=inp)
    if result.exit_code != 0:
        print(result.output)
        raise result.exception
    return result


@pytest.fixture(scope='function')
def teardown_setup_project():
    try:
        expipe.delete_project(PROJECT_ID, remove_all_childs=True)
    except NameError:
        pass
    project = expipe.require_project(PROJECT_ID)
    action = project.require_action(ACTION_ID)
    yield project, action


@pytest.fixture(scope='module')
def module_teardown_setup_project_setup():
    try:
        expipe.delete_project(PROJECT_ID, remove_all_childs=True)
    except NameError:
        pass
    project = expipe.require_project(PROJECT_ID)

    from expipe_plugin_cinpla.main import CinplaPlugin
    CinplaPlugin().attach_to_cli(cli)

    # make surgery action
    run_command(['register-surgery', pytest.RAT_ID,
                 '--weight', '500',
                 '--birthday', '21.05.2017',
                 '--procedure', 'implantation',
                 '-d', '21.01.2017T14:40',
                 '-a', 'mecl', 1.9,
                 '-a', 'mecr', 1.8])

    # init adjusment
    run_command(['adjust', pytest.RAT_ID,
                 '-a', 'mecl', 50,
                 '-a', 'mecr', 50,
                 '-d', 'now',
                 '--init'], inp='y')
    yield project


@pytest.fixture
def setup_project_action():
    project = expipe.require_project(PROJECT_ID)
    try:
        project.delete_action(ACTION_ID)
    except NameError:
        pass
    action = project.require_action(ACTION_ID)
    yield project, action
