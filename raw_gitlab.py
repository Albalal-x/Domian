from seleniumbase import SB

with SB(uc=True, test=True, locale_code="en") as sb:
    url = "https://arabshentai.com"

    sb.activate_cdp_mode(url)

    # انتظار تحميل الصفحة
    sb.sleep(3)

    # محاولة حل Cloudflare / Turnstile captcha
    sb.uc_gui_click_captcha()

    # انتظار تجاوز التحقق
    sb.sleep(3)

    # التأكد من تحميل الصفحة
    sb.assert_element("body", timeout=10)

    # تمييز بعض العناصر
    sb.highlight("a")

    sb.post_message("Page Loaded Successfully", duration=4)

    # استخراج HTML
    html = sb.get_page_source()

    print("\n===== PAGE HTML START =====\n")
    print(html)
    print("\n===== PAGE HTML END =====\n")

    print("Success! Page HTML extracted.")
