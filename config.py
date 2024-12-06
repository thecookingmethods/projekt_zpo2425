import json


class Config:
    db_dir_key = "db_dir"
    ai_model_path_key = "ai_model_path"
    ai_model_tokens_path_key = "ai_model_tokens_path"
    webapi_host_key = "webapi_host"
    webapi_port_key = "webapi_port"

    def __init__(self, config_path):
        with open(config_path) as config_file:
            config_dict = json.load(config_file)

        self.db_dir = config_dict[self.db_dir_key]
        self.ai_model_path = config_dict[self.ai_model_path_key]
        self.ai_model_tokens_path = config_dict[self.ai_model_tokens_path_key]
        self.webapi_host = config_dict[self.webapi_host_key]
        self.webapi_port = config_dict[self.webapi_port_key]
