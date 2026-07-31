import urllib.request
import urllib.parse
from html.parser import HTMLParser
import sys
import os

BASE_URL = "http://localhost:8000"

class ImageAndLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
        self.links = []
        self.slide_ids = []
        self.lang_zh_count = 0
        self.lang_en_count = 0

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == "img" and "src" in attr_dict:
            self.images.append(attr_dict["src"])
        if tag == "a" and "href" in attr_dict:
            self.links.append(attr_dict["href"])
        if tag == "section" and "id" in attr_dict:
            if attr_dict["id"].startswith("slide-"):
                self.slide_ids.append(attr_dict["id"])
        
        # Check classes for language tags
        classes = attr_dict.get("class", "").split()
        if "lang-zh" in classes:
            self.lang_zh_count += 1
        if "lang-en" in classes:
            self.lang_en_count += 1

def test_endpoint(path):
    url = f"{BASE_URL}/{path.lstrip('/')}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'E2E-Tester'})
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            content = resp.read()
            return status, content
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return None, None

def run_e2e_tests():
    print("=" * 60)
    print("🚀 RUNNING END-TO-END (E2E) TEST SUITE FOR NOVASTARS PORTFOLIO")
    print("=" * 60)

    passed_tests = 0
    total_tests = 0

    # Test 1: Server and Main Index Page
    total_tests += 1
    print("\n[TEST 1] Server Health & Main Portfolio Page (index.html)")
    status, html_index = test_endpoint("index.html")
    if status == 200 and html_index:
        print("  ✓ PASS: index.html returned 200 OK")
        passed_tests += 1
    else:
        print(f"  ❌ FAIL: index.html failed with status {status}")

    # Test 2: Improvement Proposals Page
    total_tests += 1
    print("\n[TEST 2] Improvement Proposals Page (improvement.html)")
    status, html_improvement = test_endpoint("improvement.html")
    if status == 200 and html_improvement:
        print("  ✓ PASS: improvement.html returned 200 OK")
        passed_tests += 1
    else:
        print(f"  ❌ FAIL: improvement.html failed with status {status}")

    # Test 3: CSS Stylesheet
    total_tests += 1
    print("\n[TEST 3] Stylesheet Integrity (index.css)")
    status, css_content = test_endpoint("index.css")
    if status == 200 and b"--accent-orange" in css_content:
        print("  ✓ PASS: index.css returned 200 OK and contains brand color variables")
        passed_tests += 1
    else:
        print(f"  ❌ FAIL: index.css issue (status={status})")

    # Test 4: Slide Structure & Count in index.html
    total_tests += 1
    print("\n[TEST 4] 7-Slide Presentation Structure")
    parser_index = ImageAndLinkParser()
    if html_index:
        parser_index.feed(html_index.decode("utf-8"))
        print(f"  Info: Detected slides -> {parser_index.slide_ids}")
        if len(parser_index.slide_ids) == 7:
            print("  ✓ PASS: Exactly 7 slides configured (slide-0 through slide-6)")
            passed_tests += 1
        else:
            print(f"  ❌ FAIL: Expected 7 slides, found {len(parser_index.slide_ids)}")
    else:
        print("  ❌ FAIL: Could not parse index.html")

    # Test 5: Image Assets Verification (index.html)
    total_tests += 1
    print("\n[TEST 5] Image Assets Verification in index.html")
    img_failures_index = 0
    if html_index:
        for img_src in parser_index.images:
            if img_src.startswith("http"):
                img_url = img_src
            else:
                img_url = f"{BASE_URL}/{img_src.lstrip('/')}"
            
            try:
                req = urllib.request.Request(img_url, headers={'User-Agent': 'E2E-Tester'})
                with urllib.request.urlopen(req) as resp:
                    if resp.status != 200:
                        print(f"  ❌ FAIL: Image {img_src} returned status {resp.status}")
                        img_failures_index += 1
            except Exception as e:
                print(f"  ❌ FAIL: Image {img_src} failed to load: {e}")
                img_failures_index += 1
        
        if img_failures_index == 0:
            print(f"  ✓ PASS: All {len(parser_index.images)} images in index.html loaded cleanly with 200 OK")
            passed_tests += 1
        else:
            print(f"  ❌ FAIL: {img_failures_index} broken images found in index.html")

    # Test 6: Image Assets Verification (improvement.html)
    total_tests += 1
    print("\n[TEST 6] Image Assets Verification in improvement.html")
    parser_imp = ImageAndLinkParser()
    img_failures_imp = 0
    if html_improvement:
        parser_imp.feed(html_improvement.decode("utf-8"))
        for img_src in parser_imp.images:
            if img_src.startswith("http"):
                img_url = img_src
            else:
                img_url = f"{BASE_URL}/{img_src.lstrip('/')}"
            
            try:
                req = urllib.request.Request(img_url, headers={'User-Agent': 'E2E-Tester'})
                with urllib.request.urlopen(req) as resp:
                    if resp.status != 200:
                        print(f"  ❌ FAIL: Image {img_src} returned status {resp.status}")
                        img_failures_imp += 1
            except Exception as e:
                print(f"  ❌ FAIL: Image {img_src} failed to load: {e}")
                img_failures_imp += 1
        
        if img_failures_imp == 0:
            print(f"  ✓ PASS: All {len(parser_imp.images)} images in improvement.html loaded cleanly with 200 OK")
            passed_tests += 1
        else:
            print(f"  ❌ FAIL: {img_failures_imp} broken images found in improvement.html")

    # Test 7: Bilingual Support Coverage
    total_tests += 1
    print("\n[TEST 7] Bilingual Markup Verification (Chinese & English)")
    zh_cnt = parser_index.lang_zh_count + parser_imp.lang_zh_count
    en_cnt = parser_index.lang_en_count + parser_imp.lang_en_count
    print(f"  Info: Detected {zh_cnt} Chinese elements and {en_cnt} English elements across pages")
    if zh_cnt > 20 and en_cnt > 20:
        print("  ✓ PASS: Robust dual-language markup confirmed across all pages")
        passed_tests += 1
    else:
        print(f"  ❌ FAIL: Low language element count (zh={zh_cnt}, en={en_cnt})")

    # Test Summary
    print("\n" + "=" * 60)
    print(f"📊 E2E TEST SUMMARY: {passed_tests}/{total_tests} TESTS PASSED")
    print("=" * 60)

    if passed_tests == total_tests:
        print("🎉 ALL END-TO-END TESTS PASSED SUCCESSFULLY!")
        return 0
    else:
        print("❌ SOME TESTS FAILED. PLEASE REVIEW LOGS.")
        return 1

if __name__ == "__main__":
    sys.exit(run_e2e_tests())
