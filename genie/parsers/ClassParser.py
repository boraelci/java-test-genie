"""
Adapted from [methods2test](https://github.com/microsoft/methods2test)
"""

import os
import json
import platform
import subprocess
import shutil
from .TestParser import TestParser


class ClassParser:
    def __init__(self, repo_path, repo_name, grammar_file, tmp_repo_out_path):
        self.repo_path = repo_path
        self.repo_name = repo_name
        self.language = 'java'
        self.grammar_file = grammar_file
        self.tmp_repo_out_path = tmp_repo_out_path

    def find_classes(self):
        root = self.repo_path
        # Move to folder
        if os.path.exists(root):
            os.chdir(root)
        else:
            return

        # Test Classes
        try:
            result = subprocess.check_output(r'grep -l -r @Test --include \*.java', shell=True)
            tests = result.decode('ascii').splitlines()
        except:
            print("Error during grep")
            return

        # Java Files
        os_system = platform.system()
        try:
            if os_system == "Darwin":
                result = subprocess.check_output(['find', '.', '-iname', '*.java'])
            else:
                result = subprocess.check_output(['find', '-name', '*.java'])
            java = result.decode('ascii').splitlines()
            java = [j.replace("./", "") for j in java]
        except:
            print("Error during find")
            return

        focals = list(set(java) - set(tests))
        focals = [f for f in focals if not "src/test" in f]
        print(f"Found {len(focals)} potential classes")
        return focals

    def parse_selected_classes(self, selected_class_paths):
        parser = TestParser(self.grammar_file, self.language)
        for java_file in selected_class_paths:
            parsed_classes = parser.parse_file(java_file)

            if len(parsed_classes) > 1:
                print("Too many classes in a file. It's > 1")
            for parsed_class in parsed_classes:
                class_methods = parsed_class['methods']

                if class_methods:
                    class_info = dict(parsed_class)
                    class_info.pop('argument_list')
                    class_info['file'] = java_file

                    class_file = f"{class_info['identifier']}.json"
                    json_path = os.path.join(self.tmp_repo_out_path, class_file)
                    self.export(class_info, json_path)
        print(f"Completed parsing {len(selected_class_paths)} selected classes")

    def export(self, data, out):
        with open(out, "w") as text_file:
            data_json = json.dumps(data)
            text_file.write(data_json)
