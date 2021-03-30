# extract link from pdf using pdf2xml in Windows
## Use Introduction
        python extract_from_pdf.py --input_path pdf_path  
Then you will get a jsonl file in pdf_path, and the meaining of the fields are as follows:

        pos_flag (int)：Resource Location Marker                        
                0-bodytext; 1-footnote
        index (int)：Resource ID
                if pos_flag=0, ID from smallest to largest according to the order in which they appear in the text; 
                if pos_flag=1, ID is equal to the serial number of footnote
        link (str)：Resource Hyperlinks
        context (list)：Resource context

## Tool Introduction
This project mainly uses the open source tool PDF2XML to extract the sentences containing the resource citations and the corresponding hyperlinks in the PDF format of literature, which is currently the Windows version.

### pdf2xml in Windows verion：
function：convert pdf to xml

more details in https://github.com/kermitt2/pdf2xml

We provide the pdf2xml and its requirements in the tool file, which is currently the Windows version. 

To run pdftoxml, simply type:

tool\pdftoxml.exe -noImage -noImageInline ./input.pdf ./input.html