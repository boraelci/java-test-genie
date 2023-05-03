# JavaTestGenie
![MIT License](https://img.shields.io/github/license/boraelci/review-master)
[![PyPI](https://img.shields.io/pypi/v/java-test-genie)](https://pypi.org/project/java-test-genie/)

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
      "parent_dir": "src/main/java/com/ase/restservice/service",
      "dir_names": ["interface"],
      "file_names": []
    }
  ]
}
```

The file is case-sensitive. Ensure that you do not list files in the "exclude" section unless they match a path in the "include" section. Excluding a path will delete all matches, even if a specific class is explicitly listed in the "include" section. For instance, if you exclude "model/" but include "model/Account.java", it will not work. Instead, simply include "model/Account.java" and leave the "exclude" section empty, as the "model/" directory is already skipped.

Finally, you can run it with:

```bash
genie
```

## Example

Here is an example repo that you can use the config file above with.

`git clone https://github.com/boraelci/kaiserschmarrn.git`

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
