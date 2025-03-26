import os
import aiohttp
from app.helpers.formatter_input import format_currency, fullfillment_information, get_today_time, number_to_vietnamese_words, transform_purchase_details
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.responses import JSONResponse
import json
from app.services.document_service import generate_and_clean_document
from app.services.order_service_lark import retrieve_order_details, retrieve_order_details_for_invoices
from app.utils.logging_config import logger
from app.config import config

router = APIRouter()

@router.post("/processing-data")
async def process_processing_data(request: Request):
    try:
        request_data = await request.json()
        # Extract necessary fields
        reason_for_purchase = request_data.get("reason_for_purchase", "")
        purchase_details = request_data.get("purchase_details", [])
        token_retrieve_detail = request_data.get("token_retrieve_detail", "")
        deposit_money = request_data.get("deposit_money", "")
        total_order_value = request_data.get("total_order_value", "")
        order_supply_code = request_data.get("order_supply_code", "")
        order_id = request_data.get("order_id", "")

        # Gọi API để lấy thông tin đơn hàng
        order_data = await retrieve_order_details(token_retrieve_detail, order_id)
        
        reason_for_purchase = fullfillment_information(reason_for_purchase, order_data, deposit_money, total_order_value)
        purchase_details = transform_purchase_details(order_data)
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

@router.post("/processing-invoice-data")
async def process_processing_data_invoice(request: Request):
    try:
        request_data = await request.json()
        # Extract necessary fields
        reason_for_purchase = request_data.get("reason_for_purchase", "")
        purchase_details = request_data.get("purchase_details", [])
        token_retrieve_detail = request_data.get("token_retrieve_detail", "")
        token_lark = request_data.get("token_lark", "")
        customer_deposit_money = request_data.get("customer_deposit_money", "")
        total_order_value = request_data.get("total_order_value", "")
        customer_name = request_data.get("customer_name", "")
        order_id = request_data.get("order_id", "")

        # Gọi API để lấy thông tin đơn hàng
        order_data = await retrieve_order_details_for_invoices(token_retrieve_detail, order_id)
        reason_for_purchase = fullfillment_information(reason_for_purchase, order_data, customer_deposit_money, total_order_value)
        purchase_details = transform_purchase_details(order_data)
        if customer_deposit_money != total_order_value:
            template_used = config.TEMPLATE_PATH_2_DOT
        else:
            template_used = config.TEMPLATE_PATH

        tam_ung_don_hang = format_currency(customer_deposit_money)
        con_lai_don_hang = format_currency(total_order_value - customer_deposit_money)
        products = [
            {
                "STT": index + 1,
                "MaHang": item[1]["value"], 
                "DonVi": "Unit", 
                "SoLuong": item[2]["value"],
                "DonGia": int(round(item[3]["value"] / 1.1, 0)),  
                "ThanhTien": int(round(item[2]["value"] * (item[3]["value"] / 1.1), 0)),
                "TTHH": "", 
                "BH": "",
            }
            for index, item in enumerate(purchase_details)
        ]
        
        processed_data = {
            "Products": products,
            "TongDonHang": format_currency(float(total_order_value)),
            "VAT": format_currency(float(total_order_value / 1.1) * 0.1),
            "TongGiaTri": format_currency(float(total_order_value / 1.1)),
            "TongDonHangBangChu": number_to_vietnamese_words(int(float(total_order_value / 1.1) * 1000)),
            "ThanhToanDot1": int((customer_deposit_money / total_order_value) * 100),
            "ThanhToanDot2": 100 - int((customer_deposit_money / total_order_value) * 100),
            "TamUngDonHang": tam_ung_don_hang,
            "ConLaiDonHang": con_lai_don_hang,
        }
        # Generate document
        document_io = generate_and_clean_document(template_used, processed_data)
        document_io.seek(0)


        upload_url = "https://www.larksuite.com/approval/openapi/v2/file/upload"
        form_data = aiohttp.FormData()
        form_data.add_field("name", f"{customer_name}.docx")
        form_data.add_field("type", "attachment")
        form_data.add_field("content", document_io, filename=f"{customer_name}.docx", content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {token_lark}",
            }
            async with session.post(upload_url, data=form_data, headers=headers) as response:
                upload_result = await response.json()
                
                if upload_result.get("code") != 0:
                    raise HTTPException(status_code=500, detail="Failed to upload document to LarkSuite")

                file_code = upload_result["data"]["code"]
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
                },
                {
                    "id":"widget15828096955850001",
                    "type":"attachmentV2",
                    "value": [file_code]
                }
            ], ensure_ascii=False)
        }

        return JSONResponse(
            content={
                "status": "success",
                "message": "Data processed successfully",
                "final_data": final_data,
            },
            status_code=200
        )

    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")