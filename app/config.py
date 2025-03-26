import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TEMPLATE_PATH = "app/templates/template_hop_dong.docx"
    TEMPLATE_PATH_2_DOT = "app/templates/template_hop_dong_2_dot.docx"
    BASE_URL = "https://api-man1.kiotviet.vn/api"
    BRANCH_ID = "406785"
    RETAILER = "wifioss"

config = Config()
