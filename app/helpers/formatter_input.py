from datetime import datetime, timezone

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


def get_today_time():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def fullfillment_information(reason_for_purchase, purchase_details, deposit_money, total_order_value):
    """Append formatted purchase details to the existing reason_for_purchase."""
    reason_text = reason_for_purchase.strip()  
    reason_text += "\n\nĐơn hàng gồm các sản phẩm:\n"
    for item in purchase_details:
        product = item.get("Product", {}) 
        ma_hang = product.get("Code", "N/A") 
        ten_san_pham = product.get("Name", "N/A") 
        so_luong = item.get("Quantity", 1)
        reason_text += f"- Mã hàng: {ma_hang}\n Tên sản phẩm: {ten_san_pham}\n Số lượng: {so_luong}\n"
    deposit_money = int(deposit_money)  # hoặc float(deposit_money)
    remain_price_str = f"{(total_order_value - deposit_money):,.0f} VNĐ".replace(",", ".")    
    reason_text += f"\nChưa thanh toán số tiền: {remain_price_str}\n"
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

def format_currency(value):
    return f"{float(value):,.0f} VNĐ"