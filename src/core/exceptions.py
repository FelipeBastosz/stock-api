from typing import Any, Optional


class AppException(Exception):
    """Exceção base da aplicação para padronizar status HTTP e mensagens de erro."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class EntityNotFoundException(AppException):
    """Recurso não encontrado no banco (404)."""

    def __init__(self, entity_name: str, identifier: Any) -> None:
        super().__init__(
            message=f"{entity_name} com identificador '{identifier}' não foi encontrado(a).",
            status_code=404,
        )


class BusinessRuleException(AppException):
    """Violação de regra de negócio (400).
    Ex: tentar excluir categoria com produtos vinculados.
    """

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__(message=message, status_code=400, details=details)


class ConflictException(AppException):
    """Conflito de unicidade (409), como duplicidade de CNPJ, email ou SKU."""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__(message=message, status_code=409, details=details)


class InsufficientStockException(BusinessRuleException):
    """Tentativa de saída maior do que a quantidade disponível em estoque."""

    def __init__(
        self,
        product_name: str,
        current_stock: int,
        requested_quantity: int,
    ) -> None:
        super().__init__(
            message=(
                f"Estoque insuficiente para o produto '{product_name}'. "
                f"Disponível: {current_stock}, Solicitado: {requested_quantity}."
            ),
            details={
                "current_stock": current_stock,
                "requested_quantity": requested_quantity,
            },
        )


class UnauthorizedException(AppException):
    """Falha de autenticação ou token ausente/expirado (401)."""

    def __init__(self, message: str = "Credenciais inválidas ou token ausente/expirado.") -> None:
        super().__init__(message=message, status_code=401)


class ForbiddenException(AppException):
    """Acesso negado por permissões de perfil insuficientes (403)."""

    def __init__(self, message: str = "Acesso negado: permissões insuficientes.") -> None:
        super().__init__(message=message, status_code=403)

