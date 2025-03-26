import io
from docx import Document
from docxtpl import DocxTemplate

def generate_and_clean_document(template_path, data):
    """Tạo tài liệu và làm sạch nội dung trống"""
    doc = DocxTemplate(template_path)
    doc.render(data)

    # Chuyển đổi thành Document object để làm sạch
    doc_io = io.BytesIO()
    doc.save(doc_io)
    doc_io.seek(0)
    doc = Document(doc_io)

    # Xóa các dòng trống trong bảng
    for table in doc.tables:
        rows_to_delete = [row for row in table.rows if all(cell.text.strip() == "" for cell in row.cells)]
        for row in rows_to_delete:
            table._element.remove(row._element)

    # Lưu lại file đã xử lý
    cleaned_io = io.BytesIO()
    doc.save(cleaned_io)
    cleaned_io.seek(0)
    
    return cleaned_io
