from datetime import datetime
from os import read
from select import select
from sys import stdin, stdout
from time import time


class LineReader(object):
    def __init__(self, fd):
        self._fd = fd
        self._buf = ''

    def fileno(self):
        return self._fd

    def readlines(self):
        data = read(self._fd, 4096).decode('ascii')
        if not data:
            # EOF
            return None
        self._buf += str(data)
        if '\n' not in data:
            return []
        tmp = self._buf.split('\n')
        lines, self._buf = tmp[:-1], tmp[-1]
        return lines


def process_line(section, line):
    line = line.strip()
    if line.startswith('>>>'):
        section = line[3:]
        l = None
    else:
        l = {
            'section': section or "",
            'datetime': datetime.utcnow().isoformat(),
            'message': line
        }

    return section, l


def logger_cli(augury, args):
    assert args.cmd == 'logger'

    s = stdout
    if args.output:
        s = open(args.output, 'w')

    stdin_linereader = LineReader(stdin.fileno())
    readable = [stdin_linereader]

    queued_logs = []
    last_sent_time = time()
    section = None
    while readable:
        while readable:
            ready = select(readable, [], [], args.timeout / 5)[0]
            for stream in ready:
                lines = stream.readlines()
                if lines is None:
                    # got EOF on this stream
                    readable.remove(stream)
                    continue
                for line in lines:
                    section, l = process_line(section, line)
                    if l is not None:
                        queued_logs.append(l)
                        s.write('{} {}: {}\n'.format(l['datetime'], l['section'], l['message']))
                        s.flush()  # flush output to file/stdout so that filebeat can pick it up
            if time() - last_sent_time > args.timeout and len(queued_logs):
                augury.add_logs(queued_logs)
                queued_logs = []
                last_sent_time = time()


def create_parser(parser):
    runner = parser.add_parser('logger')
    runner.add_argument('-o', '--output', help='file to write output to')
    runner.add_argument('-t', '--timeout', help='timeout to aggregate logs in seconds', default=1, type=float)
