import json


class JsonEnv:
    def __init__(self, env_file_path: str):
        self._env_file_path = env_file_path
        self._parameters = json.load(open(env_file_path))

    def __getitem__(self, item: str):
        self._fail_if_variable_undefined(item)
        return self._parameters[item]

    def get(self, item, default=None):
        if item not in self._parameters:
            return default
        return self[item]

    def _fail_if_variable_undefined(self, item):
        if item not in self._parameters:
            error_message = f'Variable "{item}" was not provided in the environment file "{self._env_file_path}"'
            raise KeyError(error_message)
