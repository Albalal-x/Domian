import os
import sys
import zipfile
import shutil
from io import BytesIO
from PIL import Image
import requests
from seleniumbase import SB

SAVE_DIR = "downloads"
os.makedirs(SAVE_DIR, exist_ok=True)
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def create_zip(zip_name, files_to_zip):
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files_to_zip:
            if os.path.exists(file):
                zipf.write(file, os.path.basename(file))
                os.remove(file)  # حذف الـ PDF الأصلي لتوفير المساحة بعد ضغطه
    print(f"📦 Created Bundle: {zip_name}")

def download_chapter(sb, url, ch_num, slug):
    sb.uc_open_with_reconnect(url, reconnect_time=5)
    if "Just a moment" in sb.get_page_title():
        sb.uc_gui_click_captcha()
        sb.sleep(5)
    
    img_elements = sb.find_elements("img")
    img_links = list(dict.fromkeys([
        el.get_attribute("src") or el.get_attribute("data-src") 
        for el in img_elements if el.get_attribute("src") or el.get_attribute("data-src")
    ]))
    
    images = []
    for link in img_links:
        if any(x in link.lower() for x in [".jpg", ".png", ".webp", ".jpeg"]) and "logo" not in link.lower():
            try:
                r = requests.get(link, headers=HEADERS, timeout=10)
                img = Image.open(BytesIO(r.content)).convert('RGB')
                images.append(img)
            except: continue
            
    if images:
        pdf_path = os.path.join(SAVE_DIR, f"{slug}_ch_{ch_num}.pdf")
        images[0].save(pdf_path, save_all=True, append_images=images[1:])
        for i in images: i.close()
        return pdf_path
    return None

def run():
    base_url = sys.argv[1] # https://.../slug/1
    start_ch = int(sys.argv[2])
    end_ch = int(sys.argv[3])
    
    parts = base_url.strip("/").split("/")
    slug = parts[-2]
    main_url = "/".join(parts[:-1])

    current_batch_files = []
    
    with SB(uc=True, headless=True) as sb:
        for ch in range(start_ch, end_ch + 1):
            pdf = download_chapter(sb, f"{main_url}/{ch}", ch, slug)
            if pdf:
                current_batch_files.append(pdf)
            
            # إذا وصلنا لـ 10 فصول أو وصلنا لنهاية العدد المطلوب
            if len(current_batch_files) == 10 or (ch == end_ch and current_batch_files):
                batch_start = ch - len(current_batch_files) + 1
                zip_name = os.path.join(SAVE_DIR, f"{slug}_chapters_{batch_start}_to_{ch}.zip")
                create_zip(zip_name, current_batch_files)
                current_batch_files = [] # تصفير القائمة للمجموعة التالية

if __name__ == "__main__":
    run()
