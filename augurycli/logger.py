import json
from sys import stdin, stdout


def logger_cli(augury, args):
    assert args.cmd == 'logger'

    output_file = stdout
    if args.output:
        output_file = open(args.output, 'w')

    section = None
    for line in stdin:
        line = line.strip()
        if line.startswith('>>>'):
            section = line[3:]
        else:
            json.dump({
                'section': section or "",
                'message': line
            }, output_file)
            output_file.write('\n')
    output_file.close()


def create_parser(parser):
    runner = parser.add_parser('logger')
    runner.add_argument('-o', '--output', help='file to write output to')
