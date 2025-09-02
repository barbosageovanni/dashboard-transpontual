#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.services.atualizacao_service import AtualizacaoService

print("=== TESTE DOS NOVOS TEMPLATES ===")

print("\n1. Testando CSV template melhorado...")
csv_content = AtualizacaoService.template_csv()
print(f"Tamanho: {len(csv_content)} caracteres")

# Salvar e mostrar conteúdo
with open("template_melhorado.csv", "w", encoding="utf-8-sig") as f:
    f.write(csv_content)

print("Conteúdo do CSV:")
lines = csv_content.split('\n')
for i, line in enumerate(lines[:6]):  # Mostra primeiras 6 linhas
    print(f"  Linha {i+1}: {line}")

print("\n2. Testando Excel template melhorado...")
excel_buffer = AtualizacaoService.template_excel()
print(f"Tamanho: {excel_buffer.getbuffer().nbytes} bytes")

with open("template_melhorado.xlsx", "wb") as f:
    f.write(excel_buffer.getvalue())

print("\n3. Testando funções de limpeza...")

# Teste de valores monetários
valores_teste = [
    "R$ 3.998,97",
    "1.500,50", 
    "2300.75",
    "1,234.56",
    "R$ 1.234,56",
    "",
    None
]

print("\nTeste de limpeza de valores monetários:")
for valor in valores_teste:
    limpo = AtualizacaoService._limpar_valor_monetario(valor)
    print(f"  '{valor}' -> {limpo}")

# Teste de datas
datas_teste = [
    "13/08/2025",
    "13/08/25", 
    "2025-08-13",
    "07/08/2025",
    "",
    None
]

print("\nTeste de limpeza de datas:")
for data in datas_teste:
    limpa = AtualizacaoService._limpar_data(data)
    print(f"  '{data}' -> '{limpa}'")

print("\n4. Testando normalização de linha completa...")
dados_teste = {
    "numero_cte": "22454",
    "destinatario_nome": "BAKER HUGHES DO BRASIL LTDA",
    "veiculo_placa": "KYE1I22",
    "valor_total": "R$ 3.998,97",
    "data_emissao": "13/08/2025",
    "data_baixa": "",
    "numero_fatura": "",
    "data_inclusao_fatura": "",
    "primeiro_envio": "14/08/2025",
    "observacao": "Carga agendada #: 524682509"
}

dados_normalizados = AtualizacaoService._normalizar_dados_linha(dados_teste)
print("Dados originais vs normalizados:")
for campo in dados_teste:
    original = dados_teste[campo]
    normalizado = dados_normalizados.get(campo)
    print(f"  {campo}: '{original}' -> '{normalizado}'")

print("\n🎉 Testes de templates e limpeza concluídos!")
