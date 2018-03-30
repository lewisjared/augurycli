from datetime import datetime
from os import read
from select import select
from sys import stdin, stdout
from time import time

from requests.exceptions import HTTPError
from six import string_types


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


def send_logs(augury, logs, out_stream):
    try:
        augury.add_logs(logs)
        del logs[:]
        return time()
    except HTTPError as e:
        out_stream.write('Error sending logs: status {}: {}'.format(e.response.status_code, e.response.content))


def logger_cli(augury, args):
    assert args.cmd == 'logger'

    in_fh = args.input
    if isinstance(in_fh, string_types):
        in_fh = open(in_fh)

    out_fh = args.output
    if isinstance(out_fh, string_types):
        out_fh = open(out_fh, 'w')

    in_linereader = LineReader(in_fh.fileno())
    readable = [in_linereader]

    queued_logs = []
    last_sent_time = time()
    section = None
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
                    out_fh.write('{} {}: {}\n'.format(l['datetime'], l['section'], l['message']))
                    out_fh.flush()  # flush output to file/stdout so that filebeat can pick it up
        if time() - last_sent_time > args.timeout and len(queued_logs):
            res = send_logs(augury, queued_logs, out_fh)
            # Update the last sent time if successful
            last_sent_time = res or last_sent_time

    if len(queued_logs):
        send_logs(augury, queued_logs, out_fh)


def create_parser(parser):
    runner = parser.add_parser('logger')
    runner.add_argument('-i', '--input', help='Log file to readin', default=stdin)
    runner.add_argument('-o', '--output', help='file to write output to', default=stdout)
    runner.add_argument('--timeout', help='timeout to aggregate logs in seconds', default=1, type=float)
