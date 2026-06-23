import os
from transformers import T5Tokenizer, T5ForConditionalGeneration

INPUT_DIR = "../in_abs/subset_50/judgement"
OUTPUT_DIR = "../outputs/t5/summaries"

os.makedirs(OUTPUT_DIR, exist_ok=True)

model_name = "t5-small"
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

def summarize_text(text, max_input_length=512, max_output_length=150):
    input_text = "summarize: " + text.strip().replace("\n", " ")

    input_ids = tokenizer.encode(
        input_text,
        return_tensors="pt",
        max_length=max_input_length,
        truncation=True
    )

    summary_ids = model.generate(
        input_ids,
        max_length=max_output_length,
        min_length=60,
        length_penalty=2.0,
        num_beams=4,
        early_stopping=True
    )

    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

def main():
    files = os.listdir(INPUT_DIR)

    for file in files:
        if not file.endswith(".txt"):
            continue

        input_path = os.path.join(INPUT_DIR, file)
        output_path = os.path.join(OUTPUT_DIR, file)

        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()

        summary = summarize_text(text)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(summary)

        print(f"T5 summarized: {file}")

    print("T5 abstractive summarization completed.")

if __name__ == "__main__":
    main()
