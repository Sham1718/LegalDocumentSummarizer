import os
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer

# Paths
INPUT_DIR = "../in_abs/subset_50/judgement"
OUTPUT_DIR = "../outputs/textrank/summaries"

os.makedirs(OUTPUT_DIR, exist_ok=True)

summarizer = TextRankSummarizer()

def summarize_file(input_path, output_path, sentence_count=12):
    parser = PlaintextParser.from_file(input_path, Tokenizer("english"))
    summary = summarizer(parser.document, sentence_count)

    with open(output_path, "w", encoding="utf-8") as f:
        for sentence in summary:
            f.write(str(sentence) + "\n")

def main():
    files = os.listdir(INPUT_DIR)

    for file in files:
        if file.endswith(".txt"):
            input_file = os.path.join(INPUT_DIR, file)
            output_file = os.path.join(OUTPUT_DIR, file)

            summarize_file(input_file, output_file)
            print(f"Summarized: {file}")

    print("TextRank summarization completed.")

if __name__ == "__main__":
    main()
