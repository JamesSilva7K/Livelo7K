function handleCarteira7Error(error) {
    if (error.response) {
        const status = error.response.status;
        const code = error.response.data?.code || 'unknown_error';
        
        switch (status) {
            case 400: return { status: 400, message: "Dados inválidos", code };
            case 401: return { status: 401, message: "Falha de autenticação ou assinatura", code };
            case 404: return { status: 404, message: "Recurso não encontrado", code };
            case 429: return { status: 429, message: "Limite de requisições excedido", code };
            case 500: return { status: 500, message: "Erro interno do servidor da API", code };
            case 502:
            case 503:
            case 504: return { status: 502, message: "Indisponibilidade do gateway", code };
            default: return { status, message: "Erro desconhecido na API", code };
        }
    }
    return { status: 500, message: "Falha na comunicação com a API", code: 'network_error' };
}

module.exports = { handleCarteira7Error };
