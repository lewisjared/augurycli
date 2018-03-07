import os


def kwargs_from_env(environment=None):
    if not environment:
        environment = os.environ

    host = environment.get('AUGURY_HOST')

    token = environment.get('AUGURY_TOKEN')

    params = {}

    if host:
        params['base_url'] = host

    if token:
        params['token'] = token

    return params