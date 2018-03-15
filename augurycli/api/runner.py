
class RunnerMixin(object):
    def add_artifacts(self, artifacts):
        url = self._url('/runner/artifacts')
        data = [{'filename': d} for d in artifacts]
        return self._result(self.post(url, json={
            'artifacts': data
        }))

    def fetch_config(self):
        url = self._url('/runner/config')
        return self._result(self.get(url))

    def get_runner_status(self):
        url = self._url('/runner/status')
        return self._result(self.get(url))

    def set_runner_status(self, status, error=None):
        url = self._url('/runner/status')

        data = {
            'status': status
        }
        if error:
            data['error'] = error
        return self._result(self.post(url, json=data))