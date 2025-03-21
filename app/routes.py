import io
import asyncio
import logging
import json
import os
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, Response
from docx import Document
from dotenv import load_dotenv
from docxtpl import DocxTemplate
from docxtpl import RichText
import locale
import httpx
from fastapi import APIRouter, Request
from datetime import datetime, timezone

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

router = APIRouter()
TEMPLATE_PATH = "template/template_hop_dong.docx"
TEMPLATE_PATH_2_DOT = "template/template_hop_dong_2_dot.docx"

def get_today_time():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def number_to_vietnamese_words(n):
    units = ["", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
    teens = ["mười", "mười một", "mười hai", "mười ba", "mười bốn", "mười lăm", "mười sáu", "mười bảy", "mười tám", "mười chín"]
    tens = ["", "", "hai mươi", "ba mươi", "bốn mươi", "năm mươi", "sáu mươi", "bảy mươi", "tám mươi", "chín mươi"]
    
    def convert_hundred(num):
        hundred = num // 100
        remainder = num % 100
        result = ""

        if hundred > 0:
            result += units[hundred] + " trăm"
            if remainder > 0:
                result += " "

        if remainder >= 10 and remainder <= 19:
            result += teens[remainder - 10]
        else:
            ten = remainder // 10
            unit = remainder % 10
            if ten > 0:
                result += tens[ten]
                if unit > 0:
                    result += " "
            if unit > 0:
                result += units[unit]
        
        return result.strip()

    def convert_thousands(num):
        if num == 0:
            return "không"

        parts = []
        billions = num // 1_000_000_000
        millions = (num % 1_000_000_000) // 1_000_000
        thousands = (num % 1_000_000) // 1_000
        remainder = num % 1_000

        if billions > 0:
            parts.append(convert_hundred(billions) + " tỷ")
        if millions > 0:
            parts.append(convert_hundred(millions) + " triệu")
        if thousands > 0:
            parts.append(convert_hundred(thousands) + " nghìn")
        if remainder > 0:
            parts.append(convert_hundred(remainder))

        return " ".join(parts).capitalize() + " đồng"

    return convert_thousands(n)

def format_currency(value):
    return f"{float(value) * 1000:,.0f} VNĐ"

def generate_and_clean_document(template_path, data):
    """Generates and cleans the document in-memory."""
    doc = DocxTemplate(template_path)
    doc.render(data)

    # Convert to a normal Document object for cleaning
    doc_io = io.BytesIO()
    doc.save(doc_io)
    doc_io.seek(0)
    doc = Document(doc_io)

    # Remove empty rows from tables
    for table in doc.tables:
        rows_to_delete = [row for row in table.rows if all(cell.text.strip() == "" for cell in row.cells)]
        for row in rows_to_delete:
            table._element.remove(row._element)

    # Save the cleaned document back into memory
    cleaned_io = io.BytesIO()
    doc.save(cleaned_io)
    cleaned_io.seek(0)
    
    return cleaned_io

def fullfillment_information(reason_for_purchase, purchase_details, deposit_money, total_order_value):
    """Append formatted purchase details to the existing reason_for_purchase."""
    locale.setlocale(locale.LC_ALL, 'vi_VN.UTF-8')  
    reason_text = reason_for_purchase.strip()  
    reason_text += "\n\nĐơn hàng gồm các sản phẩm:\n"
    for item in purchase_details:
        product = item.get("Product", {}) 
        ma_hang = product.get("Code", "N/A") 
        ten_san_pham = product.get("Name", "N/A") 
        so_luong = item.get("Quantity", 1)
        don_gia = int(item.get("Price", 0))  
        reason_text += f"- Mã hàng: {ma_hang}\n Tên sản phẩm: {ten_san_pham}\n Số lượng: {so_luong}\n Giá: {don_gia:,.0f} VNĐ/c \n"
    deposit_money = int(deposit_money)  # hoặc float(deposit_money)
    remain_price_str = f"{(total_order_value - deposit_money):,.0f} VNĐ".replace(",", ".")    
    reason_text += f"\nChưa thanh toán số tiền: {remain_price_str} đã bao gồm VAT\n"
    return reason_text

def transform_purchase_details(purchase_details):
    transformed_details = []
    for item in purchase_details:
        product = item.get("Product", {}) 
        transformed_details.append([
            {"id": "widget4", "type": "input", "value": product.get("Code", "N/A") },
            {"id": "widget5", "type": "input", "value": product.get("Code", "N/A") },
            {"id": "widget6", "type": "number", "value": item.get("Quantity", 1)},
            {"id": "widget7", "type": "amount", "value": item.get("SubTotal", 0)},  
        ])
    return transformed_details

@router.post("/processing-data")
async def process_processing_data(request: Request):
    print("Processing data")
    try:
        request_data = await request.json()
        # Extract necessary fields
        reason_for_purchase = request_data.get("reason_for_purchase", "")
        purchase_details = request_data.get("purchase_details", [])
        token_retrieve_detail = request_data.get("token_retrieve_detail", "")
        deposit_money = request_data.get("deposit_money", "")
        total_order_value = request_data.get("total_order_value", "")
        order_supply_code = request_data.get("order_supply_code", "")

        #URL for retrieve order details
        url_for_retrieve_order_details = (
            f"https://api-man1.kiotviet.vn/api/OrderSuppliers/{purchase_details}/details"
            f"?format=json&%24inlinecount=allpages&Includes=Product&isFilter=true&%24top=10"
        )
        headers = {
            "Authorization": f"Bearer {token_retrieve_detail}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Accept-encoding": "gzip, deflate, br, zstd",
            "Accept-language": "en-US,en;q=0.9",
            "Branchid": "406785",
            "Retailer": "wifioss",
            "Referer": "https://wifioss.kiotviet.vn/",
        }
        # Retrieve order details
        async with httpx.AsyncClient() as client:
            response = await client.get(url_for_retrieve_order_details, headers=headers)
            if response.status_code != 200:
                return {"error": "Failed to retrieve order details", "status_code": response.status_code}
            flattened_products = response.json().get("Data", [])
            reason_for_purchase = fullfillment_information(reason_for_purchase, flattened_products, deposit_money, total_order_value)
        # Ensure JSON formatting
        purchase_details = transform_purchase_details(flattened_products)
        final_data = {
            "form": json.dumps([  # Correctly format `form` as a JSON string
                {
                    "id": "widget0",
                    "type": "textarea",
                    "value": reason_for_purchase
                },
                {
                    "id": "widget15754430770720001",
                    "type": "radioV2",
                    "value": "k3qy4q8h-ssvnqr2zmyl-0"
                },
                {
                    "id": "widget2",
                    "type": "date",
                    "value": f"{get_today_time()}"
                },
                {
                    "id": "widget3",
                    "type": "fieldList",
                    "value": purchase_details
                }
            ], ensure_ascii=False)
        }

        return JSONResponse(
            content={
                "status": "success",
                "message": "Data processed successfully",
                "final_data": final_data,
                "order_supply_code": order_supply_code
            },
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
# @router.post("/processing-data-form")
# async def process_processing_data(request: Request):
#     print("processing-data-form")
#     try:
#         request_data = await request.json()
#         formatted_data = request_data["form_content"]
#         def clean_data(data):
#             if isinstance(data, str):
#                 return data.strip() if data.strip() else None
#             elif isinstance(data, list):
#                 return [clean_data(item) for item in data if clean_data(item) is not None]
#             elif isinstance(data, dict):
#                 return {key: clean_data(value) for key, value in data.items() if clean_data(value) is not None}
#             return data

#         # cleaned_data = clean_data(formatted_data)

#         cleaned_data["approval_code"] = "87DF5DF5-72F4-4D7C-B726-5831F97BB865"
#         cleaned_data["user_id"] = "b1g22611"
#         cleaned_data["open_id"] = "ou_b5cad580bf31bb0124f5948e8a168c6d"

#         # formatted_data = json.dumps(cleaned_data)

#         # return PlainTextResponse(content=formatted_data, status_code=200)
#         return cleaned_data

#     except Exception as e:
#         print(f"Error processing data: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
# @router.post("/generate-quotation")
# async def process_generate_quotation(request: Request):
#     try:
#         data = await request.json()
#         data_list = data["data"]

#         total_price = sum(item["Thành tiền"] for item in data_list["Hàng hóa"])
#         vat = total_price * 0.1
#         grand_total = total_price + vat

#         thanh_toan_dot_1 = data_list["Thanh toán tối thiểu %"]
#         if int(thanh_toan_dot_1) == 100:
#             template_used = TEMPLATE_PATH
#         else:
#             template_used = TEMPLATE_PATH_2_DOT
#         grand_total = float(grand_total) 
#         tam_ung_don_hang = format_currency(grand_total * float(thanh_toan_dot_1) / 100)
#         con_lai_don_hang = format_currency(grand_total * (100 - float(thanh_toan_dot_1)) / 100)
#         print(f"grand_total: {grand_total}")
#         print(f"tam_ung_don_hang: {tam_ung_don_hang}")
#         print(f"con_lai_don_hang: {con_lai_don_hang}")

#         processed_data = {
#             "Products": [
#                 {
#                     "STT": index + 1,
#                     "MaHang": item["Mã Hàng"],
#                     "DonVi": item["Đơn Vị"],
#                     "SoLuong": item["Số Lượng"],
#                     "DonGia": item["Đơn giá"],
#                     "ThanhTien": item["Thành tiền"],
#                     "TTHH": item["TTHH"],
#                     "BH": item["BH"],
#                 }
#                 for index, item in enumerate(data_list["Hàng hóa"])
#             ],
#             "TongGiaTri": format_currency(total_price),
#             "VAT": format_currency(vat),
#             "TongDonHang": format_currency(grand_total),
#             "TongDonHangBangChu": number_to_vietnamese_words(int(grand_total * 1000)),
#             "BenMua_TenCongTy": data_list["Bên Mua - Tên Công Ty"],
#             "BenMua_TenDaiDien": data_list["Bên Mua - Tên Đại diện"],
#             "BenMua_ChucVu": data_list["Bên Mua - Chức vụ"],
#             "BenMua_DiaChi": data_list["Bên Mua - Địa Chỉ"],
#             "BenMua_MaSoThue": data_list["Bên Mua - Mã Số Thuế"],
#             "BenMua_SoTaiKhoan": data_list["Bên Mua - Số Tài Khoản"],
#             "thanh_toan_dot_1": thanh_toan_dot_1,
#             "ThanhToanDot1": thanh_toan_dot_1,
#             "ThanhToanDot2": (100 - int(thanh_toan_dot_1)), 
#             "TamUngDonHang": tam_ung_don_hang,
#             "ConLaiDonHang": con_lai_don_hang,
#         }

#         # Generate and clean document
#         document_io = generate_and_clean_document(template_used, processed_data)

#         return Response(
#             document_io.read(),
#             media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
#             headers={"Content-Disposition": "attachment; filename=quotation.docx"},
#         )
#     except Exception as e:
#         logger.error(f"Error generating quotation: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
