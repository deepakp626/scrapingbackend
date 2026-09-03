
import io
import os
import shutil
import time
import pymupdf
from PIL import Image
import pytesseract

# Auto-configure tesseract path if found on Windows
_TESSERACT_CANDIDATES = [
    os.environ.get("TESSERACT_PATH"),
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
    os.path.expanduser(r"~\AppData\Local\Tesseract-OCR\tesseract.exe"),
]

for _path in _TESSERACT_CANDIDATES:
    if _path and os.path.exists(_path):
        pytesseract.pytesseract.tesseract_cmd = _path
        break


class PDFTextExtractor:

    async def extract_pdf_text(self, file_bytes: bytes) -> dict:
        """
        Extract text from PDF with hybrid native + OCR support and detailed page breakdown.

        Returns:
        {
            "success": bool,
            "text": str,
            "total_pages": int,
            "word_count": int,
            "char_count": int,
            "pages": list[dict],
            "stats": dict,
            "normal_pdf_time": float,
            "ocr_time": float,
            "total_time": float,
            "ocr_used": bool
        }
        """
        total_start = time.time()
        normal_pdf_time = 0.0
        ocr_time = 0.0
        ocr_used_total = False
        pages_data = []

        try:
            # 1. Open PDF document
            doc = pymupdf.open(stream=file_bytes, filetype="pdf")

            if doc.is_encrypted:
                doc.close()
                raise ValueError("This PDF is password-protected. Please unlock it before extracting text.")

            total_pages = len(doc)
            if total_pages == 0:
                doc.close()
                raise ValueError("PDF contains no pages.")

            # 2. Extract page by page
            for page_num in range(total_pages):
                page = doc.load_page(page_num)

                # Step A: Native text extraction
                n_start = time.time()
                raw_page_text = page.get_text("text").strip()
                n_end = time.time()
                normal_pdf_time += (n_end - n_start)

                page_text = raw_page_text
                page_ocr_used = False

                # Step B: If page text is sparse (< 30 chars), attempt OCR
                if len(raw_page_text) < 30:
                    o_start = time.time()
                    try:
                        ocr_result = self._ocr_page(page)
                        if len(ocr_result.strip()) > len(raw_page_text):
                            page_text = ocr_result.strip()
                            page_ocr_used = True
                            ocr_used_total = True
                    except Exception as ocr_err:
                        # Graceful fallback if tesseract binary is not installed or errors
                        pass
                    o_end = time.time()
                    ocr_time += (o_end - o_start)

                words = [w for w in page_text.split() if w]
                pages_data.append({
                    "page": page_num + 1,
                    "text": page_text,
                    "word_count": len(words),
                    "char_count": len(page_text),
                    "ocr_used": page_ocr_used
                })

            doc.close()

            # Combine full text preserving page separations
            combined_text = "\n\n".join(p["text"] for p in pages_data if p["text"]).strip()
            total_words = sum(p["word_count"] for p in pages_data)
            total_chars = len(combined_text)
            total_end = time.time()

            stats = {
                "normal_pdf_time": round(normal_pdf_time, 3),
                "ocr_time": round(ocr_time, 3),
                "total_time": round(total_end - total_start, 3),
                "ocr_used": ocr_used_total
            }

            return {
                "success": True,
                "text": combined_text,
                "total_pages": total_pages,
                "word_count": total_words,
                "char_count": total_chars,
                "pages": pages_data,
                "stats": stats,
                "normal_pdf_time": stats["normal_pdf_time"],
                "ocr_time": stats["ocr_time"],
                "total_time": stats["total_time"],
                "ocr_used": ocr_used_total
            }

        except Exception as e:
            raise e

    def _ocr_page(self, page) -> str:
        """Render page as image and run OCR."""
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("L")
        return pytesseract.image_to_string(
            img,
            lang="eng",
            config="--oem 3 --psm 6"
        )