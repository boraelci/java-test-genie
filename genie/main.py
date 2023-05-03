#!/usr/bin/env python

import argparse
import json
import os
import platform
import re
import sys

from genie.parsers.ClassParser import ClassParser
from genie.parsers.ConfigParser import ConfigParser
from genie.wrappers.GptWrapper import GptWrapper

SINGLE_FILE = False
SINGLE_FILE_NAME = "AssetService.java"
LOCAL_RESPONSE = True


def save_test(repo_test_path, test_content):
    repo_test_dir = os.path.dirname(repo_test_path)
    os.makedirs(repo_test_dir, exist_ok=True)
    with open(repo_test_path, "w") as f:
        f.write(test_content)
    print(f"Saved tests to {repo_test_path}")


def gpt_raw_classes(genie_dir, repo_dir, selected_class_paths):
    gpt_system_prompt_path = f"{genie_dir}/resources/gpt_system_prompt_raw.txt"
    gpt = GptWrapper(gpt_system_prompt_path)
    for class_path in selected_class_paths:
        class_name_java = class_path.split("/")[-1]
        class_name = class_name_java.replace(".java", "")
        if SINGLE_FILE is True and class_name_java != SINGLE_FILE_NAME:
            continue

        print(f"\nGenerating tests for {class_name_java}...")
        if LOCAL_RESPONSE is True:
            with open(f"{genie_dir}/resources/gpt_response_for_raw.txt", "r") as f:
                response = f.read()
        else:
            with open(class_path, "r") as f:
                content = f.read()
            try:
                response = gpt.query(content)
                print(f"Succesfully generated tests for {class_name_java}")
            except Exception as e:
                print(e)
                print(f"Failed to generate tests for {class_name_java}")
                continue

        response = re.sub(r"^```$\n?", "", response, flags=re.MULTILINE)
        test_name = class_name + "Test"
        test_path = class_path.replace('src/main', 'src/test')
        test_path = test_path.replace(f"{class_name}.java", f"{test_name}.java")
        repo_test_path = f"{repo_dir}/{test_path}"

        test_content = response
        # print(test_content)
        if os.path.exists(repo_test_path):
            user_input = input(f"{test_name}.java already exists. Do you want to overwrite it? (y/n): ")
            if user_input.lower() == "y":
                save_test(repo_test_path, test_content)
            else:
                print(f"Discarded")
        else:
            save_test(repo_test_path, test_content)


def gpt_parsed_classes(genie_dir, repo_dir, tmp_repo_out_dir):
    gpt_system_prompt_path = f"{genie_dir}/resources/gpt_system_prompt_parsed.txt"
    gpt = GptWrapper(gpt_system_prompt_path)
    os.chdir(tmp_repo_out_dir)
    for filename in os.listdir():
        if SINGLE_FILE is True and filename != SINGLE_FILE_NAME:
            continue

        print(f"Generating tests for {filename.replace('json', 'java')}")
        if LOCAL_RESPONSE is True:
            with open(f"{genie_dir}/resources/gpt_response_for_parsed_broken.json", "r") as f:
                response = f.read()
            try:
                response = json.loads(response)
            except json.decoder.JSONDecodeError:
                response += "}\"}"
                response = json.loads(response)
        else:
            with open(filename, "r") as f:
                content = f.read()
            response = gpt.query(content)
            print(response)
            try:
                response = json.loads(response)
            except json.decoder.JSONDecodeError:
                response += "}\"}"
                response = json.loads(response)

        test_name = response['identifier']
        test_path = response['file']
        test_content = response['content']

        repo_test_path = f"{repo_dir}/{test_path}"
        if os.path.exists(repo_test_path):
            user_input = input(f"{test_name}.java already exists. Do you want to overwrite it? (y/n): ")
            if user_input.lower() == "y":
                save_test(repo_test_path, test_content)
            else:
                print(f"Discarded")
        else:
            save_test(repo_test_path, test_content)


def main():
    # args = parse_args()
    repo_dir = os.getcwd()
    repo_name = repo_dir.split("/")[-1]
    if repo_name == "java-test-genie":  # For quick local testing during early development
        repo_dir = "/Users/boraelci/Desktop/ASE/kaiserschmarrn"
        repo_name = repo_dir.split("/")[-1]
        os.chdir(repo_dir)
    config_path = f"{repo_dir}/.genie.json"

    # Check config file exists
    if not os.path.exists(config_path):
        print(
            f"Error: .genie.json file cannot be found at {config_path}; follow instructions in our README to create one"
        )
        sys.exit(1)
    config_parser = ConfigParser(config_path)

    # Check directory is correct
    if "src" not in os.listdir():
        print("Error: src folder cannot be found in the current directory")
        sys.exit(1)
    genie_dir = os.path.dirname(os.path.realpath(__file__))

    # Select grammar file depending on OS
    os_system = platform.system()
    if os_system == "Darwin":
        grammar_file = f"{genie_dir}/resources/libtree-sitter-java.dylib"
    else:
        grammar_file = f"{genie_dir}/resources/java-grammar.so"

    tmp_repo_out_dir = f"tmp/output/{repo_name}"
    os.makedirs(tmp_repo_out_dir, exist_ok=True)  # TODO try with exist_ok=False

    class_parser = ClassParser(repo_dir, repo_name, grammar_file, tmp_repo_out_dir)
    all_class_paths = class_parser.find_classes()
    selected_class_paths = config_parser.get_selected_class_paths(all_class_paths)
    class_parser.parse_selected_classes(selected_class_paths)
    gpt_raw_classes(genie_dir, repo_dir, selected_class_paths)


# TODO argparse do_overwrite

if __name__ == "__main__":  # pragma: no cover
    main()
