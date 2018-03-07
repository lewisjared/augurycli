import argparse

from augurycli import from_env
from augurycli.runner import runner_cli, create_parser as create_runner_parser




def run_command(args):
    augury = from_env()
    if args.token:
        augury.token = args.token
    if args.cmd == 'runner':
        runner_cli(augury, args)


def main():
    parser = argparse.ArgumentParser(prog='augury', description='')
    parser.add_argument('-t', '--token', help='API token used for authentication')
    subparsers = parser.add_subparsers(dest='cmd')
    subparsers.required = True

    create_runner_parser(subparsers)

    args = parser.parse_args()
    run_command(args)


if __name__ == '__main__':
    main()
