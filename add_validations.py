import os

js_path = r"d:\Paginas ADS\Livelo\static\js\main.js"

with open(js_path, "r", encoding="utf-8") as f:
    js = f.read()

validations = """
// --- Real Validations ---
// Only letters in Name
const inputName = $id('input-name');
if(inputName) {
    inputName.addEventListener('input', function(e) {
        this.value = this.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚâêîôûÂÊÎÔÛãõÃÕçÇ\\s]/g, '');
    });
}

// Ensure proper validations for address
const inputRua = $id('input-rua');
if(inputRua) {
    inputRua.addEventListener('input', function(e) {
        this.value = this.value.replace(/[^a-zA-Z0-9áéíóúÁÉÍÓÚâêîôûÂÊÎÔÛãõÃÕçÇ\\s,-]/g, '');
    });
}
const inputCidade = $id('input-cidade');
if(inputCidade) {
    inputCidade.addEventListener('input', function(e) {
        this.value = this.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚâêîôûÂÊÎÔÛãõÃÕçÇ\\s-]/g, '');
    });
}
const inputBairro = $id('input-bairro');
if(inputBairro) {
    inputBairro.addEventListener('input', function(e) {
        this.value = this.value.replace(/[^a-zA-Z0-9áéíóúÁÉÍÓÚâêîôûÂÊÎÔÛãõÃÕçÇ\\s-]/g, '');
    });
}

// Validar CPF rigorosamente
function isCPFValid(cpf) {
    cpf = cpf.replace(/\\D/g, '');
    if(cpf.length !== 11 || /^(\\d)\\1+$/.test(cpf)) return false;
    let sum = 0, rest;
    for (let i = 1; i <= 9; i++) sum = sum + parseInt(cpf.substring(i-1, i)) * (11 - i);
    rest = (sum * 10) % 11;
    if ((rest == 10) || (rest == 11))  rest = 0;
    if (rest != parseInt(cpf.substring(9, 10)) ) return false;
    sum = 0;
    for (let i = 1; i <= 10; i++) sum = sum + parseInt(cpf.substring(i-1, i)) * (12 - i);
    rest = (sum * 10) % 11;
    if ((rest == 10) || (rest == 11))  rest = 0;
    if (rest != parseInt(cpf.substring(10, 11) ) ) return false;
    return true;
}
"""

if "// --- Real Validations ---" not in js:
    js = js + "\n" + validations

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js)

print("Validations added to main.js")
