# VMCAS Data Extraction and CSV Generation

## Project Overview
This Python project aims to extract relevant data from VMCAS (Veterinary Medical College Application Service) PDF files and generate corresponding CSV files for further analysis and processing. The VMCAS application process involves submitting various documents, including transcripts, GRE scores, and personal statements. This project streamlines the extraction of essential applicant data from these documents, facilitating data organization and analysis for admission committees or researchers.

## Script Description

### read_vmcas.py

#### Description
The `read_vmcas.py` script is responsible for extracting data from a single VMCAS PDF file. It utilizes the `pdfplumber` library to parse PDF content and extract relevant information such as applicant name, GRE scores, high school details, college history, and GPA.

#### Usage
```python
from read_vmcas import extract_data

# Example usage
pdf_file_path = 'path_to_your_PDF_file.pdf'
data = extract_data(pdf_file_path)
print(data)
```

#### Dependencies
- `pdfplumber`
- `re`

### read_all_vmcas.py

#### Description
The `read_all_vmcas.py` script iterates through a folder containing multiple VMCAS PDF files. It imports the `extract_data` function from `read_vmcas.py` and applies it to each PDF file in the folder. Subsequently, it generates three CSV files for student information, GRE scores, and college details.

#### Usage
```python
from read_all_vmcas import iterate_files, generate_csv

# Example usage
folder_path = 'path_to_your_folder_containing_PDF_files'
file_paths = iterate_files(folder_path)

student_id = 1

for path in file_paths:
    data_lines = extract_data(path)
    student_id = generate_csv(data_lines, student_id, 'VMCAS_data/student_info.csv', 'VMCAS_data/gre_scores.csv', 'VMCAS_data/college_info.csv')
```

#### Dependencies
- `os`
- `csv`
- `re`
- `read_vmcas` (module from `read_vmcas.py`)

---

This README.md provides an overview of the entire project, followed by detailed descriptions of each script's functionality, usage instructions, and dependencies. Ensure to replace `'path_to_your_PDF_file.pdf'` and `'path_to_your_folder_containing_PDF_files'` with the actual paths to your PDF files or folder containing PDF files, respectively.
