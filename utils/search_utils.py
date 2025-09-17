import urllib.parse
import csv
import os
from datetime import datetime

def generate_search_links(keyword):
    encoded = urllib.parse.quote_plus(keyword)
    return {
        "amazon": f"https://www.amazon.co.jp/s?k={encoded}",
        "rakuten": f"https://search.rakuten.co.jp/search/mall/{encoded}/",
        "yahoo": f"https://shopping.yahoo.co.jp/search?p={encoded}",
        "mercari": f"https://www.mercari.com/jp/search/?keyword={encoded}",
        "paypay": f"https://paypayfleamarket.yahoo.co.jp/search/{encoded}",
        "1688": f"https://s.1688.com/selloffer/offer_search.htm?keywords={encoded}"
    }

def ai_predict_product_name(image_path):
    return "Anker モバイルバッテリー"

def save_search_history(keyword, method):
    filepath = 'data/search_history.csv'
    os.makedirs('data', exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filepath, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([now, keyword, method])
