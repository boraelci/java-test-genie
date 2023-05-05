#!/usr/bin/env python

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import platform
import re
import sys
import time
from tqdm import tqdm
import shutil

from genie.parsers.ClassParser import ClassParser
from genie.parsers.ConfigParser import ConfigParser
from genie.wrappers.GptWrapper import GptWrapper

SINGLE_FILE = False
SINGLE_FILE_NAME = "AssetService.json"
LOCAL_RESPONSE = False


def save_test(repo_test_path, test_content):
    repo_test_dir = os.path.dirname(repo_test_path)
    os.makedirs(repo_test_dir, exist_ok=True)
    with open(repo_test_path, "w") as f:
        f.write(test_content)
    print(f"Saved tests to {repo_test_path}")


def generate_whole_classes(genie_dir, repo_dir, selected_class_paths, do_overwrite):
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
            except KeyboardInterrupt:
                raise KeyboardInterrupt
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
        while True:
            if os.path.exists(repo_test_path):
                if do_overwrite is True:
                    user_input = "y"
                else:
                    user_input = input(f"{test_name}.java already exists. Do you want to overwrite it? (y/n): ")

                if user_input.lower() == "y":
                    save_test(repo_test_path, test_content)
                    break
                else:
                    print(f"Discarded")
                    break
            else:
                save_test(repo_test_path, test_content)
                break


def convert_to_json(response):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        response += "}\"}"
        response = json.loads(response)
    return response


def generate_by_methods(genie_dir, repo_dir, tmp_repo_out_dir, do_overwrite, batch_size):
    gpt_system_prompt_path = f"{genie_dir}/resources/generate_by_methods_prompt.txt"
    gpt = GptWrapper(gpt_system_prompt_path)
    os.chdir(tmp_repo_out_dir)
    for filename in os.listdir():
        if SINGLE_FILE is True and filename != SINGLE_FILE_NAME:
            continue

        print(f"\nGenerating tests for {filename.replace('json', 'java')}...")

        if LOCAL_RESPONSE is True:
            with open(f"{genie_dir}/resources/gpt_response_for_parsed_broken.json", "r") as f:
                response = f.read()
        else:
            with open(filename, "r") as f:
                content = f.read()
            focal_class = json.loads(content)
            class_path = focal_class["file"]
            class_name_java = class_path.split("/")[-1]
            class_name = class_name_java.replace(".java", "")
            constructor_signatures = [method["signature"] for method in focal_class["methods"] if method["constructor"]]
            superclass = focal_class["superclass"]
            interfaces = focal_class["interfaces"]
            methods = [m for m in focal_class["methods"] if not m["constructor"]]
            results = []
            start = time.time()

            # Initialize the progress bar with the total number of methods
            progress_bar = tqdm(total=len(methods), desc="Completed", unit="method")

            # Create a function to process a single method and submit it to the executor
            def process_method(m):
                submission = f"{class_name} {superclass} {interfaces} "
                submission += "{"
                submission += f"{m['body']} "
                for constructor_signature in constructor_signatures:
                    submission += f"{constructor_signature}; "
                submission += "}"
                submission = submission.replace("\n", " ").strip()  # Remove new lines
                submission = re.sub('[ \t]+', ' ', submission)  # Merge multiple spaces into one
                return gpt.query(submission)

            with ThreadPoolExecutor(max_workers=batch_size) as executor:
                futures = {executor.submit(process_method, m): m for m in methods}

                for future in as_completed(futures):
                    try:
                        result = future.result()
                        results.append(result)
                    except KeyboardInterrupt:
                        raise KeyboardInterrupt
                    except Exception as e:
                        print(f"Job failed with error: {e}")
                    progress_bar.update(1)

            progress_bar.close()
            progress_bar.close()
            end = time.time()
            print(f"Completed in {format(end - start, '.1f')} seconds")
            test_name = class_name + "Test"
            test_path = class_path.replace('src/main', 'src/test')
            test_path = test_path.replace(f"{class_name}.java", f"{test_name}.java")
            repo_test_path = f"{repo_dir}/{test_path}"
            repo_test_dir = os.path.dirname(repo_test_path)
            os.makedirs(repo_test_dir, exist_ok=True)

            def save_results():
                with open(repo_test_path, "w") as f:
                    for r in results:
                        r = re.sub(r"^```[a-zA-Z]*\n?", "", r, flags=re.MULTILINE)
                        f.write(r)
                        f.write("\n")
                print(f"Saved tests to {repo_test_path}")

            if os.path.exists(repo_test_path):
                while True:
                    if do_overwrite is True:
                        user_input = "y"
                    else:
                        user_input = input(f"{test_name}.java already exists. Do you want to overwrite it? (y/n): ")
                    if user_input.lower() == "y":
                        save_results()
                        break
                    elif user_input.lower() == "n":
                        print(f"Discarded")
                        break
            else:
                save_results()
                break

        """
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
        """


def main():
    args = parse_args()
    mode = args["mode"]
    if mode != "classes" and mode != "methods":
        print("Error: mode must be either 'classes' or 'methods'")
        sys.exit(1)
    do_overwrite = args["do_overwrite"]
    batch_size = args["batch_size"]
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

    tmp_repo_out_dir = f"/tmp/output/{repo_name}"
    try:
        shutil.rmtree(tmp_repo_out_dir)  # Clean up previous runs
    except:
        pass
    os.makedirs(tmp_repo_out_dir, exist_ok=True)

    class_parser = ClassParser(repo_dir, repo_name, grammar_file, tmp_repo_out_dir)
    all_class_paths = class_parser.find_classes()
    selected_class_paths = config_parser.get_selected_class_paths(all_class_paths)
    if mode == "methods":
        class_parser.parse_selected_classes(selected_class_paths)
        generate_by_methods(genie_dir, repo_dir, tmp_repo_out_dir, do_overwrite, batch_size)
    else:
        generate_whole_classes(genie_dir, repo_dir, selected_class_paths, do_overwrite)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        type=str,
        default="methods",
        help="Whether to generate tests by methods or by classes (default: methods)",
    )
    parser.add_argument(
        "--do_overwrite",
        action="store_true",
        default=False,
        help="Whether to overwrite existing files or not (default: False)",
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=15,
        help="How many methods to process in parallel with the 'methods' mode (default: 15)",
    )
    return vars(parser.parse_args())


if __name__ == "__main__":  # pragma: no cover
    main()
