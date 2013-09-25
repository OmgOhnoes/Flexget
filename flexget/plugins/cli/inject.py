from __future__ import unicode_literals, division, absolute_import
import argparse
import string
import random
import yaml

from flexget.entry import Entry
from flexget.event import event


@event('manager.subcommand.inject')
def do_cli(manager, options):
    entry = Entry(title=options.title)
    if options.url:
        entry['url'] = options.url
    else:
        entry['url'] = 'http://localhost/inject/%s' % ''.join(random.sample(string.letters + string.digits, 30))
    if options.force:
        entry['immortal'] = True
    if options.accept:
        entry.accept(reason='accepted by CLI inject')
    options.inject = [entry]
    manager.run_subcommand('execute', options)


def key_equals_value(text):
    if not '=' in text:
        raise argparse.ArgumentTypeError('must be in the form: <field name>=<value>')
    key, value = text.split('=')
    return key, yaml.safe_load(value)


# Run after other plugins, so we can get all exec subcommand options
@event('register_parser_arguments', priority=0)
def register_parser_arguments(core_parser):
    exec_parser = core_parser.get_subparser('execute')
    inject_parser = core_parser.add_subparser('inject', add_help=False, parents=[exec_parser],
                                              help='inject an entry from command line into tasks')
    inject_group = inject_parser.add_argument_group('inject arguments')
    inject_group.add_argument('title', help='title of the entry to inject')
    inject_group.add_argument('url', nargs='?', help='url of the entry to inject')
    inject_group.add_argument('--force', action='store_true', help='prevent any plugins from rejecting this entry')
    inject_group.add_argument('--accept', action='store_true', help='accept this entry immediately upon injection')
    inject_group.add_argument('--fields', metavar='NAME=VALUE', nargs='+', type=key_equals_value)
    # Hack the title of the exec options a bit (would be 'optional arguments' otherwise)
    inject_parser._action_groups[1].title = 'execute arguments'
    # The exec arguments show first... unless we switch them
    inject_parser._action_groups.remove(inject_group)
    inject_parser._action_groups.insert(0, inject_group)
