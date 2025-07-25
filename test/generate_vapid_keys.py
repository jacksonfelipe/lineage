from pywebpush import generate_vapid_private_key, generate_vapid_public_key

private_key = generate_vapid_private_key()
public_key = generate_vapid_public_key(private_key)

print(f"VAPID_PRIVATE_KEY={private_key}")
print(f"VAPID_PUBLIC_KEY={public_key}") 