#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import datetime as DT

from common import log
from db import Task

from third_party.winreg__examples.get_active_setup_installed_components import get_active_setup_components
from third_party.winreg__examples.get_boot_execute import get_boot_execute
from third_party.winreg__examples.get_command_processor import get_command_processor
from third_party.winreg__examples.get_group_policy_scripts import get_scripts
from third_party.winreg__examples.get_image_file_execution_options import get_image_file_execution_options
from third_party.winreg__examples.get_known_dlls import get_known_dlls
from third_party.winreg__examples.get_run_paths import get_run_paths
from third_party.winreg__examples.get_startup_paths import get_all_files
from third_party.winreg__examples.get_winlogon_notify import get_winlogon_notify
from third_party.winreg__examples.get_winsock_providers import get_winsock_providers
from third_party.get_tasks_from_scheduler import get_tasks

from third_party.wait import wait
from third_party.add_notify_telegram import add_notify


def get_rids_from_simple_dict(d: dict) -> list[str]:
    return [f'{path} = {value}' for path, value in d.items()]


def get_all_rids() -> list[str]:
    items = []

    for path, components in get_active_setup_components().items():
        for component in components:
            title = component.default
            if component.version:
                title += f' ({component.version})'
            title += f' [installed={component.is_installed}]'
            title = title.strip()
            rid = fr'{path}\{component.guid}\{title} = {component.stub_path}'
            items.append(rid)

    items += get_rids_from_simple_dict(get_boot_execute())
    items += get_rids_from_simple_dict(get_command_processor())
    items += get_rids_from_simple_dict(get_scripts())
    items += get_rids_from_simple_dict(get_image_file_execution_options())
    items += get_rids_from_simple_dict(get_known_dlls())
    items += get_rids_from_simple_dict(get_run_paths())
    items += [str(path) for path in get_all_files()]
    items += [f'{path} = {values.get("DllName", "")}' for path, values in get_winlogon_notify().items()]
    items += get_rids_from_simple_dict(get_winsock_providers())

    for task in get_tasks():
        for action in task.actions:
            rid = f'{task.path}, hidden={task.hidden}, enabled={task.enabled}, action={action}'
            items.append(rid)

    return items


if __name__ == '__main__':
    while True:
        log.info('Started')

        number_tasks = Task.select().where(Task.deleted == False).count()
        is_first_runs = number_tasks == 0
        log.info(f'Tasks: {number_tasks}')

        try:
            rids = get_all_rids()
            log.info(f'Rids: {len(rids)}')

            for rid in rids:
                if Task.is_exists(rid):
                    continue

                msg = f'Added new task: {rid}'
                log.info(msg)
                Task.create(rid=rid)

                if not is_first_runs:
                    add_notify(log.name, msg)

            # Deleted tasks
            prefix = f'[deleted from {DT.datetime.now():%Y-%m-%d %H:%M:%S}]'
            for task in Task.select().where(Task.deleted == False, Task.rid.not_in(rids)):
                msg = f'Task #{task.id} rid={task.rid!r} is now mark as deleted!'
                log.info(msg)
                add_notify(log.name, msg)

                task.rid = f'{prefix} {task.rid}'
                task.deleted = True
                task.save()

        except Exception as e:
            log.exception('Error:')

            add_notify(log.name, f'ERROR: {e}', 'ERROR')
            wait(hours=1)
            continue

        finally:
            log.info('Finished\n')

        wait(minutes=5)
