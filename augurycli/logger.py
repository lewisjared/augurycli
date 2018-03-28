import json
from sys import stdin, stdout
from datetime import datetime

def logger_cli(augury, args):
    assert args.cmd == 'logger'

    streams = [stdout]
    if args.output:
        streams.append(open(args.output, 'w'))

    section = None
    for line in stdin:
        line = line.strip()
        if line.startswith('>>>'):
            section = line[3:]
        else:
            for s in streams:
                json.dump({
                    'section': section or "",
                    'logged_at': datetime.now().isoformat(),
                    'message': line
                }, s)
                s.write('\n')
                s.flush() # flush output to file/stdout so that filebeat can pick it up
    for s in streams:
        s.close()


def create_parser(parser):
    runner = parser.add_parser('logger')
    runner.add_argument('-o', '--output', help='file to write output to')
