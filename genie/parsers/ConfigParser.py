import json


class ConfigParser:
    def __init__(self, config_path):
        # Load the JSON file
        with open(config_path) as f:
            self.config = json.load(f)

    def get_selected_class_paths(self, focals):
        # Filter the Java files
        filtered_files = []
        for item in self.config['include']:
            parent_dir = item['parent_dir']

            # Check for matching files in file_names
            for file_name in item['file_names']:
                file_path = f"{parent_dir}/{file_name}"
                if file_path in focals:
                    filtered_files.append(file_path)

            # Check for matching files in dir_names
            for dir_name in item['dir_names']:
                dir_path = f"{parent_dir}/{dir_name}"
                for focal in focals:
                    if focal.startswith(dir_path):
                        filtered_files.append(focal)

        # Exclude files and directories specified in the exclude section
        for item in self.config['exclude']:
            parent_dir = item['parent_dir']

            # Exclude files in file_names
            for file_name in item['file_names']:
                file_path = f"{parent_dir}/{file_name}"
                if file_path in filtered_files:
                    filtered_files.remove(file_path)

            # Exclude files in dir_names
            for dir_name in item['dir_names']:
                dir_path = f"{parent_dir}/{dir_name}"
                filtered_files = [focal for focal in filtered_files if not focal.startswith(dir_path)]

        # Remove duplicates
        filtered_files = list(set(filtered_files))

        return filtered_files
