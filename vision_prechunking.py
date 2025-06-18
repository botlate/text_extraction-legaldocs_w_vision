import base64
import requests
import os

# === CONFIGURATION ===
BASE_DIR = r"C:/vision_prechunking"
IMG_FOLDER = os.path.join(BASE_DIR, "images")
CAPTION_FOLDER = os.path.join(BASE_DIR, "captions")
TOC_FOLDER = os.path.join(BASE_DIR, "toc")

MODEL_NAME = "gemma-3-27b-it"  # Change if needed
API_URL = "http://localhost:1234/v1/chat/completions"  # Or remote address

# Create output folders if not exist
os.makedirs(CAPTION_FOLDER, exist_ok=True)
os.makedirs(TOC_FOLDER, exist_ok=True)

# === PROMPTS ===

classify_prompt = (
    "You are an expert at identifying types of legal document pages in scanned court filings.\n"
    "Categories (choose one):\n"
    "1. Form (example: judicial council forms like SUM-100, POS-010, MC-025)\n"
    "2. Pleading cover page (caption page with case number, court, parties, attorneys, and document title)\n"
    "3. Pleading table of contents\n"
    "4. Pleading table of authorities\n"
    "5. Exhibit cover page\n"
    "6. Proof of service cover page\n"
    "7. Proof of service content\n"
    "8. Pleading content (numbered paragraphs or substantive legal arguments)\n"
    "9. Other\n"
    "If a page has numbered paragraphs or legal arguments, it is 'pleading content,' not 'form.'\n"
    "Only answer with one category from the list above.\n"
    "Which category does this page fall in?"
)

metadata_prompt = (
    "Extract the following fields from this legal pleading cover page image. For each field, use these rules:\n"
    "- Filing attorneys and full name of law firm: Extract verbatim text or write N/A.\n"
    "- Named plaintiffs: Extract the names of the individual or entity plaintiffs (not Does or unknowns) and normalize capitalization to Title Case (capitalize the first letter of each word, rest lowercase). List all separated by commas.\n"
    "- Named defendants: Extract the names of the individual or entity defendants (not Does or unknowns) and normalize capitalization to Title Case. List all separated by commas.\n"
    "- Court: Extract the full name of the court and normalize capitalization to Title Case.\n"
    "- Case number: Extract and output the official format as found on the document (including dashes if present).\n"
    "- Filing date: Output only a standardized date in YYYY-MM-DD format, or N/A if missing or unclear.\n"
    "- Document title: Extract the document title verbatim as it appears on the page.\n"
    "Format your answer as follows:\n"
    "Filing attorneys and full name of law firm: <text or N/A>\n"
    "Named plaintiffs: <Title Case names, comma-separated, or N/A>\n"
    "Named defendants: <Title Case names, comma-separated, or N/A>\n"
    "Court: <Title Case or N/A>\n"
    "Case number: <verbatim or N/A>\n"
    "Filing date: <YYYY-MM-DD or N/A>\n"
    "Document title: <verbatim or N/A>\n"
    "If any field is missing, put 'N/A' as the value."

)

toc_prompt = (
    "This page contains a table of contents from a document. "
    "Extract and return each heading or subheading exactly as it appears, preserving all original spelling, capitalization, punctuation, and numbering. "
    "Do not include any page numbers, filler characters, or ellipses (e.g., .....4 or [end of heading] 5.). Page number information is not helpful."
    "If the table of contents has an outline or hierarchy (such as Roman numerals, letters, or numbers), represent this hierarchy using Markdown heading markers: use '# ' for main/top-level headings, '## ' for second-level headings, '### ' for third-level headings, and so on. "
    "If there is no visible outline or hierarchy, use '# ' for all headings. "
    "Do not add, remove, or reformat any headings, except to remove ellipses and page number informaton."
    "Return only the heading lines, in order, using Markdown-style heading markers.\n"
    "Example:\n"
    "# INTRODUCTION\n"
    "# BACKGROUND\n"
    "## A. Relevant Legal Standard\n"
    "## B. Factual Allegations\n"
    "### 1. Alleged Misconduct\n"
    "### 2. Procedural History\n"
    "# ARGUMENT\n"
    "## I. PLAINTIFF’S CLAIMS FAIL AS A MATTER OF LAW\n"
    "### A. Plaintiff Does Not Allege that Defendant Owed it a Duty.\n"
    "### B. Plaintiff Not Allege that that Defendant Was the Cause of the Injuries.\n"
    "## II. ALTERNATIVELY, THE COURT SHOULD STRIKE IMPROPER ALLEGATIONS\n"
    "# CONCLUSION"
)

# === UTILITY ===

def call_vision_llm(image_path, prompt):
    with open(image_path, "rb") as img_file:
        img_b64 = base64.b64encode(img_file.read()).decode("utf-8")
    data = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                ]
            }
        ],
        "max_tokens": 1536
    }
    response = requests.post(API_URL, json=data)
    response.raise_for_status()
    output = response.json()
    return output["choices"][0]["message"]["content"]

# === MAIN WORKFLOW ===

def main():
    image_files = [f for f in os.listdir(IMG_FOLDER) if f.lower().endswith('.jpg')]
    for fname in image_files:
        image_path = os.path.join(IMG_FOLDER, fname)
        print(f"Classifying {fname}...")
        category = call_vision_llm(image_path, classify_prompt)
        print(f"  Category: {category}")

        # Pleading cover page → extract and save metadata
        if "pleading cover page" in category.lower():
            print(f"  Extracting metadata from {fname}...")
            metadata = call_vision_llm(image_path, metadata_prompt)
            outname = os.path.join(CAPTION_FOLDER, f"caption_{os.path.splitext(fname)[0]}.txt")
            with open(outname, "w", encoding="utf-8") as f:
                f.write(metadata)
            print(f"  Metadata written to {outname}")

        # Table of contents → extract and save Markdown-style TOC
        if "table of contents" in category.lower():
            print(f"  Extracting table of contents structure from {fname}...")
            toc_structure = call_vision_llm(image_path, toc_prompt)
            outname = os.path.join(TOC_FOLDER, f"toc_{os.path.splitext(fname)[0]}.txt")
            with open(outname, "w", encoding="utf-8") as f:
                f.write(toc_structure)
            print(f"  TOC structure written to {outname}")

if __name__ == "__main__":
    main()
