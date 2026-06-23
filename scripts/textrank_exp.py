import os
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer

INPUT_DIR = "../in_abs/subset_50/judgement"
OUTPUT_DIR = "../outputs/textrank_explainable"

os.makedirs(OUTPUT_DIR, exist_ok=True)

summarizer = TextRankSummarizer()

def explain_file(input_path, output_path, sentence_count=12):
    parser = PlaintextParser.from_file(input_path, Tokenizer("english"))
    document = parser.document

    summary = summarizer(document, sentence_count)
    sentences = list(document.sentences)
    total = len(sentences)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("EXPLAINABLE TEXTRANK SUMMARY\n")
        f.write("=" * 40 + "\n\n")

        for i, sentence in enumerate(summary, 1):
            position = sentences.index(sentence)

            if position < total * 0.3:
                section = "Beginning (Facts / Background)"
            elif position < total * 0.7:
                section = "Middle (Arguments / Reasoning)"
            else:
                section = "End (Judgment / Decision)"

            f.write(f"Rank {i}:\n")
            f.write(f"Sentence: {sentence}\n")
            f.write(f"Document position: {section}\n\n")

def main():
    files = os.listdir(INPUT_DIR)

    for file in files:
        if not file.endswith(".txt"):
            continue

        input_file = os.path.join(INPUT_DIR, file)
        output_file = os.path.join(OUTPUT_DIR, file)

        explain_file(input_file, output_file)
        print(f"Explained: {file}")

    print("Explainable TextRank completed.")

if __name__ == "__main__":
    main()
