import yaml

def read_yaml(file_name) -> dict:
    with open(file_name, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

def get_set(file_path) -> dict:
    test_yaml = read_yaml(file_path)
    for item in test_yaml['answerList']:
        yield item['test_desc'], item['value'], item['answer']
