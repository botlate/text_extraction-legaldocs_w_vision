# Vision-Assisted Text Extraction for Pre-chunking - Pages of Legal Documents with Difficult Layouts

## Purpose

This simple project uses a local vision-capable large language model (LLM) for classifying and extracting metadata from individual images taken from PDFs of legal pleadings. It targets especially challenging pages like caption pages and tables of contents that OCR often muddles. This process is run concurrently with OCR, and the results are joined with OCR text when chunking and embedding. 
 
The goal is to use machine vision as a lightweight substitute for complex layout models (like LayoutLM or Donut) that typically require expensive fine-tuning for legal document structure. Standard OCR often gets confused by legal layouts, mixing up party names, document titles, or headings, especially on cover pages, critical information where errors are time consuming to correct. Here, a general-purpose, pre-trained LLM (such as Gemma-3-27B Q8 via LM Studio) is used without fine-tuning to produce structured metadata and clean document boundaries for later embedding and search.  

**Results:** Pretty good. In a batch of 32 images, the script correctly categorized 31 pages. The one misclassification was a DFEH complaint page filed prelitigation that  resembled a pleading but was actually an exhibit. This shows the limits of stateless, per-image analysis. There were other limitations, most notably a few incorrect filing dates. See below.

## How it works

You extract individual images from PDFs of legal pleadings and place them in the `images/` folder. The script sends each image to a vision-capable LLM  with instructions to classify the page. (This script was tested with Gemma-3-27B via LM Studio’s API, but any OpenAI-compatible, open source vision LLM can be used). The LLM classifies the page type and returns the content. 

If the page is identified as a pleading cover page or table of contents, the image is sent back for further processing. The LLM is given a prompt to extract structured information—such as party names, case number, or a clean, Markdown-style list of headings—that will make chunking for embedding far more robust. That is saved as text files, which can be used later on after OCRing and during chunking. The process moves to the next page, and so forth. 

Outputs are organized in subfolders:
- `captions/` for extracted metadata from pleading cover pages
- `toc/` for extracted table of contents heading structure

**Supported document types (can be extended):**
- Form (e.g., court/judicial forms)
- Pleading cover page (caption/case info/title) _should probably be renamed "pleading caption page"_
- Table of contents
- Table of authorities
- Exhibit cover page
- Proof of service cover page
- Proof of service content
- Pleading content (numbered paragraphs/arguments)
- Other

These categories can easily be modified or expanded by changing the classification prompt to match your workflow or jurisdiction.

## Known Limitations & Warnings

- **Filing date accuracy:** The model got confused by some filing dates and made one up. This was a significant defect, but should be solveable. The prompt should give additional guidance or the process should implement a second review step to reliably select the filing date.
- **Multi-page categories:** The script needs to be modified so it can process information that comes from a document with multi-page captions page and TOCs. All of the images were self-contained, but if a caption page ran over one page, the model would treat it as two different documents.
- **Exhibits & context:** Because the script processes pages independently, it cannot distinguish between “new” pleadings and pleadings attached as exhibits. This should be less of an issue if images are being processed in per-document batches. Exhibits will need some finessing. 
- **Page type unfamiliarity:** Unusual or nonstandard pages may be misclassified. It failed to catch that a document was an "order" and not a proposed order. The judge annotated the page by adding a delete line through [proposed], which is a common practice.
- **No memory:** The script is stateless. This is intentional to reduce hallucination. Adding state or batch awareness (e.g., flagging subsequent pleadings as exhibits) is possible in a future version, but a better model would be needed and it would increase the risk of the model getting confused.
- **Not a drop-in replacement for layout-aware models:** This is an open source, lightweight alternative to models like LayoutLM, Donut, or DocTR (which may require expensive fine-tuning to work on legal pleadings).


## Model & Setup

- 100% open source: no closed API keys, cloud services, or paid resources required.
- Tested with Gemma-3-27B Q8 (run via LM Studio/OpenAI-compatible endpoint).
- Should work with any vision-capable OpenAI-compatible LLM that accepts image inputs and returns Markdown/text.

## Samples

Sample images and outputs:

- **pleading_cover.jpg**  
- **pleading_cover.txt**
- **Table_of_Authorities.jpg**
- **Table_of_Authorities.txt**
- **pleading_content.jpg**
- **form.jpg** 
- **classification error** 


## Quick Start

1. Place page images in `C:/vision_prechunking/images/`
2. Modify the the script for directory, API, and vision model.
3. Extracted metadata and TOC outputs will appear in `captions/` and `toc/` subfolders.
4. Improve process and share!


