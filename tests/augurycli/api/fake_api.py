
def get_fake_runner_config():
    status_code = 200
    response = "---" \
               "    test: [1, 2, 3]"
    return status_code, response


prefix = 'http://test.example.com'

fake_responses = {
    '{}/runner/config'.format(prefix): get_fake_runner_config
}