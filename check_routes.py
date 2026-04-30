from app import app

print("=== FLASK ROUTES TEKSHIRUVI ===")
print()

# Barcha routelarni chiqarish
for rule in app.url_map.iter_rules():
    if 'student' in rule.rule or 'test' in rule.rule:
        print(f"Route: {rule.rule}")
        print(f"  Methods: {rule.methods}")
        print(f"  Endpoint: {rule.endpoint}")
        print()
