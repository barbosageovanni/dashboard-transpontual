#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✅ Utilitários de Validação - Previne erro 'cannot unpack'
"""

def validar_retorno_metodo(resultado):
    """
    Garante que métodos sempre retornem tupla
    Previne erro 'cannot unpack non-iterable bool object'
    """
    
    # Se já é tupla, retorna como está
    if isinstance(resultado, tuple) and len(resultado) == 2:
        return resultado
    
    # Se é apenas bool True
    if resultado is True:
        return True, "Operação realizada com sucesso"
    
    # Se é apenas bool False
    if resultado is False:
        return False, "Operação falhou"
    
    # Se é None
    if resultado is None:
        return False, "Resultado indefinido"
    
    # Se é string (provável mensagem de erro)
    if isinstance(resultado, str):
        return False, resultado
    
    # Caso não identificado
    return False, f"Resultado inesperado: {type(resultado)}"

def executar_metodo_seguro(metodo, *args, **kwargs):
    """
    Executa método e garante retorno em tupla
    """
    try:
        resultado = metodo(*args, **kwargs)
        return validar_retorno_metodo(resultado)
    except Exception as e:
        return False, f"Erro na execução: {str(e)}"
