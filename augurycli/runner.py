def runner_cli(augury, args):
    assert args.cmd == 'runner'

    paths = {
        'status': set_status,
        'config': get_config,
        'artifacts': add_artifacts,
    }
    paths[args.runner_cmd](augury, args)


def set_status(augury, args):
    if args.status:
        print(augury.set_runner_status(args.status))
    else:
        print(augury.get_runner_status())


def get_config(augury, args):
    print(augury.fetch_config())


def add_artifacts(augury, args):
    print(augury.add_artifacts(args.input))


def create_parser(parser):
    runner = parser.add_parser('runner')
    subparsers = runner.add_subparsers(dest='runner_cmd')
    subparsers.required = True
    status = subparsers.add_parser('status')
    status.add_argument('-s', '--status', help='status text to set')
    status.add_argument('-e', '--error', help='error message')
    config = subparsers.add_parser('config')
    artifacts = subparsers.add_parser('artifacts')
    artifacts.add_argument('input', nargs='+', help='list of files to mark as artifacts')
