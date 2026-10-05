import re
def sanitize(val: str, max_len: int = 200) -> str:
    if not isinstance(val, str):
        val = str(val)
    return re.sub(r"[<>\"\\'`;]", "", val).strip()[:max_len]

def validate_cpf(cpf: str) -> bool:
    cpf = re.sub(r"\D", "", cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    def _d(digits, n):
        s = sum(int(d) * (n - i) for i, d in enumerate(digits))
        r = (s * 10) % 11
        return 0 if r >= 10 else r
    return _d(cpf[:9], 10) == int(cpf[9]) and _d(cpf[:10], 11) == int(cpf[10])

def format_cpf(cpf: str) -> str:
    cpf = re.sub(r"\D", "", cpf)
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

# Mock inputs
cpf_input = "085.679.430-85" # valid CPF structure
cpf_digits = re.sub(r"\D", "", cpf_input)

# /api/cpf process
cpf_raw1 = sanitize(cpf_digits, 14)
cpf1 = re.sub(r"\D", "", cpf_raw1)
val1 = validate_cpf(cpf1)
fmt = format_cpf(cpf1)
print(f"api_cpf: {cpf1} -> valid? {val1}, fmt: {fmt}")

# /api/lead process
cpf_raw2 = sanitize(fmt, 14)
cpf2 = re.sub(r"\D", "", cpf_raw2)
val2 = validate_cpf(cpf2)
print(f"api_lead: {cpf2} -> valid? {val2}")
