# JavaTestGenie
[![MIT License](https://img.shields.io/github/license/boraelci/java-test-genie)](https://github.com/boraelci/java-test-genie/blob/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/java-test-genie)](https://pypi.org/project/java-test-genie/)

## Demo
Click on the image to watch the video
[![Video](https://github.com/boraelci/java-test-genie/blob/main/genie/images/video-thumbnail.png)](https://drive.google.com/file/d/1W8TnxP7CN2rSFGRzgUXU7qNrg4EGsbIk/view?usp=share_link)

## Installation

```bash
pip install java-test-genie
```

## Usage

Before running `genie`, set your OpenAI API key with `export OPENAI_API_KEY=<API-KEY-HERE>`. You can obtain it at https://platform.openai.com/account/api-keys

Ensure that you are in a at the same level with `src/` when running the tool.

You need to create a config file named `.genie.json` within your java repository. This file should be at the same level with `src/` as well as where you will run `genie`. In this file, you can specify which directories & files to include and exclude. The example below includes the `service/` directory but excludes `service/interface`. Similarly, you can specify file names.

```json
{
  "include": [
    {
      "parent_dir": "src/main/java/com/ase/restservice",
      "dir_names": ["service"],
      "file_names": []
    }
  ],
  "exclude": [
    {
      "parent_dir": "src/main/java/com/ase/restservice",
      "dir_names": ["service/interface"],
      "file_names": []
    }
  ]
}
```

The file is case-sensitive. Ensure that you do not list files in the "exclude" section unless they already match a path in the "include" section. Excluding a path will delete all matches, even if a specific class is explicitly listed in the "include" section. For instance, if you exclude "model/" but include "model/Account.java", it will not work. Instead, simply include "model/Account.java" and leave the "exclude" section empty, as the "model/" directory is already skipped.

Finally, you can run it with:

```bash
genie
```

## Example
Here is an example repo that you can use the config file above with.

```bash
git clone https://github.com/boraelci/kaiserschmarrn.git
```

## Arguments

1. `--help`: Displays the help message and lists all available arguments.
2. `--mode`: Allows you to switch between two modes:
   - `methods` (default): Generates test methods for individual methods within the input class. This mode is suitable for large input classes.
   - `classes`: Generates a complete test class, including imports, package name, and setup. This mode provides more comprehensive functionality but is not suitable for large input classes. If the input class is too large, you may encounter an error like `Error: this file is too large`.
   
3. `--do_overwrite`: Enables automatic overwriting of existing test files without asking for confirmation. By default, this is set to false to protect existing test files. To enable automatic overwriting, just include `--do_overwrite` without specifying a parameter.

4. `--batch-size`: Specifies the number of methods to process at the same time. It defaults to 15, but you can adjust this value based on your requirements.

## Limitations

Currently, only 1 class per Java file is supported. The tool may produce errors if you supply a path that corresponds to a file with more than 1 class in it.

## Grammar

Parsing Java files with the Tree-sitter library requires grammar files. They were obtained in the following way for this tool.

### For macOS

```bash
git clone https://github.com/tree-sitter/tree-sitter-java.git
cd tree-sitter-java
tree-sitter generate
gcc -shared -o libtree-sitter-java.dylib -Isrc src/parser.c
```

### For Windows

Used the one provided as [`java-grammar.so`](https://github.com/microsoft/methods2test/blob/main/scripts/java-grammar.so)
