import exifread
import PyPDF2
import json
import os

def extract_metadata(file_path):
    metadata = {}
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext in ['.jpg', '.jpeg', '.png', '.tiff']:
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f)
                for tag in tags.keys():
                    if tag not in ['JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote']:
                        metadata[tag] = str(tags[tag])
        
        elif ext == '.pdf':
            with open(file_path, 'rb') as f:
                pdf = PyPDF2.PdfReader(f)
                info = pdf.metadata
                if info:
                    for key in info.keys():
                        metadata[key] = str(info[key])
                metadata['Pages'] = len(pdf.pages)

        # Add basic file info
        metadata['File Size'] = os.path.getsize(file_path)
        metadata['Extension'] = ext

    except Exception as e:
        metadata['Error'] = str(e)

    return json.dumps(metadata)
