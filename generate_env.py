import secrets

secret_key = secrets.token_hex(32)  # 64 belgili xavfsiz kalit yaratish
env_file = ".env"

# Avval mavjud .env faylni o‘qib olamiz
try:
    with open(env_file, "r") as f:
        lines = f.readlines()
except FileNotFoundError:
    lines = []  # Agar .env fayl bo‘lmasa, bo‘sh ro‘yxat hosil qilamiz

# Mavjud o‘zgaruvchilarni saqlab, SECRET_KEY ni yangilaymiz yoki qo‘shamiz
env_vars = {}
for line in lines:
    key_value = line.strip().split("=", 1)  # Qatorni = bilan ikkiga bo'lamiz
    if len(key_value) == 2:
        env_vars[key_value[0]] = key_value[1]

# SECRET_KEY ni yangilash
env_vars["SECRET_KEY"] = f'"{secret_key}"'  # yangi kalit qo'shiladi
env_vars.setdefault("ALGORITHM", '"HS256"')  # Agar yo'q bo'ladigan bo'lsa, ALGORITHMni yaratamiz
env_vars.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")  # Agar yo'q bo'ladigan bo'lsa, uni yaratamiz

# Yangilangan ma'lumotlarni .env faylga qayta yozamiz
with open(env_file, "w") as f:
    for key, value in env_vars.items():
        f.write(f"{key}={value}\n")

print(f"SECRET_KEY yangilandi va .env faylga saqlandi:\n{secret_key}")

# from passlib.context import CryptContext
#
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#
# hashed_password = pwd_context.hash("java0411")
# print(f"hashed_password: {hashed_password}")