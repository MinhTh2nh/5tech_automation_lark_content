from app.helpers.formatter_input import format_currency, number_to_vietnamese_words
from fastapi import APIRouter, Request, HTTPException, Response
from app.services.document_service import generate_and_clean_document
from app.utils.logging_config import logger
from app.config import config

router = APIRouter()

@router.post("/generate-quotation")
async def process_generate_quotation(request: Request):
    try:
        data = await request.json()
        data_list = data["data"]

        total_price = sum(item["Thành tiền"] for item in data_list["Hàng hóa"])
        vat = total_price * 0.1
        grand_total = total_price + vat
        thanh_toan_dot_1 = data_list["Thanh toán tối thiểu %"]

        if int(thanh_toan_dot_1) == 100:
            template_used = config.TEMPLATE_PATH
        else:
            template_used = config.TEMPLATE_PATH_2_DOT

        grand_total = float(grand_total) 
        tam_ung_don_hang = format_currency(grand_total * float(thanh_toan_dot_1) / 100)
        con_lai_don_hang = format_currency(grand_total * (100 - float(thanh_toan_dot_1)) / 100)

        processed_data = {
            "Products": [
                {
                    "STT": index + 1,
                    "MaHang": item["Mã Hàng"],
                    "DonVi": item["Đơn Vị"],
                    "SoLuong": item["Số Lượng"],
                    "DonGia": item["Đơn giá"],
                    "ThanhTien": item["Thành tiền"],
                    "TTHH": item["TTHH"],
                    "BH": item["BH"],
                }
                for index, item in enumerate(data_list["Hàng hóa"])
            ],
            "TongGiaTri": format_currency(total_price),
            "VAT": format_currency(vat),
            "TongDonHang": format_currency(grand_total),
            "TongDonHangBangChu": number_to_vietnamese_words(int(grand_total * 1000)),
            "BenMua_TenCongTy": data_list["Bên Mua - Tên Công Ty"],
            "BenMua_TenDaiDien": data_list["Bên Mua - Tên Đại diện"],
            "BenMua_ChucVu": data_list["Bên Mua - Chức vụ"],
            "BenMua_DiaChi": data_list["Bên Mua - Địa Chỉ"],
            "BenMua_MaSoThue": data_list["Bên Mua - Mã Số Thuế"],
            "BenMua_SoTaiKhoan": data_list["Bên Mua - Số Tài Khoản"],
            "thanh_toan_dot_1": thanh_toan_dot_1,
            "ThanhToanDot1": thanh_toan_dot_1,
            "ThanhToanDot2": (100 - int(thanh_toan_dot_1)), 
            "TamUngDonHang": tam_ung_don_hang,
            "ConLaiDonHang": con_lai_don_hang,
        }

        # Generate and clean document
        document_io = generate_and_clean_document(template_used, processed_data)

        return Response(
            document_io.read(),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=quotation.docx"},
        )
    except Exception as e:
        logger.error(f"Error generating quotation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
