import requests

# Test teacher PDF export
session = requests.Session()

print("=== TEACHER PDF EXPORT TEST ===")
print()

# Login as teacher (webdevaj)
login_data = {
    'username': 'webdevaj',
    'password': 'webdevaj123'
}

response = session.post('http://127.0.0.1:5000/login', data=login_data, allow_redirects=False)

if response.status_code == 302:
    print("✅ Teacher login successful!")
    
    # Get teacher results page to find result ID
    results_response = session.get('http://127.0.0.1:5000/teacher/results')
    
    if results_response.status_code == 200:
        content = results_response.text
        
        # Find PDF export link
        import re
        pdf_links = re.findall(r'href="/teacher/results/pdf/(\d+)"', content)
        
        if pdf_links:
            result_id = pdf_links[0]
            print(f"📄 Result ID: {result_id}")
            
            # Try to export PDF
            pdf_response = session.get(f'http://127.0.0.1:5000/teacher/results/pdf/{result_id}')
            
            print(f"PDF export status: {pdf_response.status_code}")
            
            if pdf_response.status_code == 200:
                # Check if it's a PDF
                content_type = pdf_response.headers.get('content-type', '')
                if 'pdf' in content_type:
                    print("✅ PDF export successful!")
                    print(f"Content-Type: {content_type}")
                    print(f"File size: {len(pdf_response.content)} bytes")
                else:
                    print("❌ Not a PDF file")
                    print(f"Content-Type: {content_type}")
                    print("Response preview:")
                    print(pdf_response.text[:200])
            else:
                print(f"❌ PDF export failed: {pdf_response.status_code}")
                print("Error content:")
                print(pdf_response.text[:500])
        else:
            print("❌ No PDF export link found")
    else:
        print(f"❌ Results page xato: {results_response.status_code}")
else:
    print("❌ Teacher login xato")
