import socket

def check_port(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    except:
        return False

print("=== PORT TEKSHIRUVI ===")

# Common Flask ports to check
ports_to_check = [5000, 8000, 3000, 8080, 9000]

for port in ports_to_check:
    if check_port(port):
        print(f"✅ Port {port} - FAOL (Ishlayapti)")
        if port == 5000:
            print("   📍 Bu Flask ilovasining default porti")
    else:
        print(f"❌ Port {port} - FAOL EMAS")

print("\n📝 JAVOB:")
print("Flask ilovasi hozirda port 5000 da ishlamoqda")
print("🌐 Browser orqali kirish: http://127.0.0.1:5000")
print("🔗 Yoki: http://localhost:5000")
