from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import os
from genie.wrappers.GptWrapper import GptWrapper
import re
from tree_sitter import Language, Parser

JAVA_LANGUAGE = Language('../genie/resources/libtree-sitter-java.dylib', 'java')
PARSER = Parser()
PARSER.set_language(JAVA_LANGUAGE)


def extract_tokens(node, lines):
    if node.child_count == 0:
        if node.type not in {'\n', 'comment'}:
            yield lines[node.start_point[0]][node.start_point[1] : node.end_point[1]]
    else:
        for n in node.children:
            yield from extract_tokens(n, lines)


def get_codebleu_score(pred, target):
    # Parse the Java code
    predicted_tree = PARSER.parse(bytes(pred, "utf8"))
    target_tree = PARSER.parse(bytes(target, "utf8"))

    # Extract tokens
    predicted_tokens = list(extract_tokens(predicted_tree.root_node, pred.splitlines(True)))
    target_tokens = list(extract_tokens(target_tree.root_node, target.splitlines(True)))

    # Compute BLEU score
    bleu_score = sentence_bleu([target_tokens], predicted_tokens)
    return bleu_score


smoothing = SmoothingFunction()


def get_bleu_score(pred, target):
    return sentence_bleu(
        [target.split()],
        pred.split(),
        smoothing_function=smoothing.method1,
    )


def get_single_mock_pred():
    with open("resources/gpt_pred.txt", "r") as f:
        pred = f.read()
    pred = pred.replace("\n", " ").strip()
    pred = re.sub('[ \t]+', ' ', pred)
    return pred


# with open("results/gpt35-base-100-tests.txt", "r") as f:
#  mock_preds = f.readlines()
def get_mock_pred_by_index(i):
    return mock_preds[i]


results_path_name = "results/gpt3.5-bla"
os.makedirs(results_path_name)
eval_dir_path = "../../data/raw-plain/eval"
eval_input_path = f"{eval_dir_path}/input.methods.txt"
eval_output_path = f"{eval_dir_path}/output.tests.txt"

with open(eval_input_path, "r", encoding='utf-8') as f:
    eval_input_list = f.readlines()

with open(eval_output_path, "r", encoding='utf-8') as f:
    eval_output_list = f.readlines()

evaluation_dir = os.path.dirname(os.path.realpath(__file__))
gpt_system_prompt_path = f"{evaluation_dir}/resources/gpt_system_prompt_evaluation.txt"
gpt = GptWrapper(gpt_system_prompt_path)  # , model="gpt-3.5-turbo")
bleu_score_sum = 0
codebleu_score_sum = 0
predictions = []
failures_count = 0
bleu_scores = []
codebleu_scores = []
for i, (input, expected) in enumerate(zip(eval_input_list, eval_output_list)):
    try:
        pred = gpt.query(input)
        # pred = get_mock_pred_by_index(i)
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except:
        print("GPT query failed")
        pred = "N/A"

    pred = re.sub(r'//.*$', '', pred, flags=re.MULTILINE)  # Remove comments
    pred = pred.replace("\n", " ").strip()  # Remove newlines
    pred = re.sub('[ \t]+', ' ', pred)  # Merge multiple spaces into one
    print(pred)
    if pred == "N/A" or "//" in pred or "```" in pred or "@Test" not in pred:
        print("FAILURE INDEX: ", i)
        print(pred)
        failures_count += 1
        bleu_score = -1
        codebleu_score = -1
    else:
        bleu_score = get_bleu_score(pred, expected)
        codebleu_score = get_codebleu_score(pred, expected)
        bleu_score_sum += bleu_score
        codebleu_score_sum += codebleu_score

    bleu_scores.append(bleu_score)
    codebleu_scores.append(codebleu_score)
    predictions.append(pred)
    print("Single BLEU: ", bleu_score)
    print("Single CodeBLEU: ", codebleu_score)

with open(f"{results_path_name}-tests.txt", "w") as f:
    f.write("\n".join(predictions))

with open(f"{results_path_name}-bleus.txt", "w") as f:
    f.write("\n".join(str(s) for s in bleu_scores))

with open(f"{results_path_name}-codebleus.txt", "w") as f:
    f.write("\n".join(str(s) for s in codebleu_scores))

print(f"Avg. BLEU score: {bleu_score_sum / (len(predictions) - failures_count)}")
print(f"Avg. CodeBLEU score: {codebleu_score_sum / (len(predictions) - failures_count)}")
print("Predictions count: ", len(predictions))
print("Failures count: ", failures_count)
