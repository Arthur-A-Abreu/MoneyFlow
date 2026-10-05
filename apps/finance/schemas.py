from pydantic import BaseModel, Field
from typing import List, Literal


class TransacaoExtrato(BaseModel):
    data: str = Field(description="Data da transação no formato YYYY-MM-DD")
    descricao: str = Field(description="Nome do estabelecimento, recebedor ou descrição da movimentação")
    valor: float = Field(description="Valor numérico decimal positivo da transação, ex: 45.90")
    tipo: Literal["receita", "despesa"] = Field(description="Tipo: 'receita' para entradas/salários/PIX recebidos, 'despesa' para saídas/compras/pagamentos")
    categoria: str = Field(description="Nome da categoria sugerida em português (ex: Alimentação, Transporte, Moradia, Lazer, etc.)")


class ExtratoSchema(BaseModel):
    transacoes: List[TransacaoExtrato] = Field(description="Lista de todas as transações individuais identificadas no documento")
