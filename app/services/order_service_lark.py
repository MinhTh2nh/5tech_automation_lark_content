import locale
import httpx
from app.utils.logging_config import logger
from app.config import config

async def retrieve_order_details(token, order_id):
    """Gọi API để lấy thông tin đơn hàng"""
    url = f"{config.BASE_URL}/OrderSuppliers/{order_id}/details?format=json&%24inlinecount=allpages&Includes=Product&isFilter=true&%24top=10"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Branchid": config.BRANCH_ID,
        "Retailer": config.RETAILER,
        "Accept": "application/json, text/plain, */*",
        "Accept-encoding": "gzip, deflate, br, zstd",
        "Accept-language": "en-US,en;q=0.9",
        "Referer": "https://wifioss.kiotviet.vn/",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to retrieve order details: {response.status_code}")
            return []
        return response.json().get("Data", [])

async def retrieve_order_details_for_invoices(token, order_id):
    """Gọi API để lấy thông tin đơn hàng"""
    url = f"{config.BASE_URL}/orders/{order_id}/details?format=json&Includes=Product&Includes=ProductFormulaHistory&%24inlinecount=allpages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Branchid": config.BRANCH_ID,
        "Retailer": config.RETAILER,
        "Accept": "application/json, text/plain, */*",
        "Accept-encoding": "gzip, deflate, br, zstd",
        "Accept-language": "en-US,en;q=0.9",
        "Referer": "https://wifioss.kiotviet.vn/",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to retrieve order details: {response.status_code}")
            return []
        return response.json().get("Data", [])
