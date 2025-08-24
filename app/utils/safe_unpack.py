#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✅ Wrapper de Segurança - Previne erro 'cannot unpack'
"""

def safe_unpack(resultado, default_message="Operação concluída"):
    """
    Garante que qualquer resultado seja retornado como tupla (sucesso, mensagem)
    Previne o erro 'cannot unpack non-iterable bool object'
    
    Args:
        resultado: Resultado de uma função que pode retornar bool, tupla ou dict
        default_message: Mensagem padrão se não houver mensagem específica
    
    Returns:
        tuple: Sempre retorna (bool, str)
    """
    
    # Se já é uma tupla válida
    if isinstance(resultado, tuple) and len(resultado) >= 2:
        return bool(resultado[0]), str(resultado[1])
    
    # Se é apenas um boolean
    if isinstance(resultado, bool):
        if resultado:
            return True, default_message
        else:
            return False, "Operação falhou"
    
    # Se é um dicionário com 'success' ou 'sucesso'
    if isinstance(resultado, dict):
        sucesso = resultado.get('success', resultado.get('sucesso', False))
        mensagem = resultado.get('message', resultado.get('mensagem', resultado.get('erro', default_message)))
        return bool(sucesso), str(mensagem)
    
    # Se é None
    if resultado is None:
        return False, "Resultado indefinido"
    
    # Se é string (provável mensagem de erro)
    if isinstance(resultado, str):
        return False, resultado
    
    # Caso não identificado - assumir falha
    return False, f"Resultado inesperado: {type(resultado)}"

def execute_safe(func, *args, **kwargs):
    """
    Executa uma função e garante retorno em tupla
    
    Args:
        func: Função a ser executada
        *args: Argumentos posicionais
        **kwargs: Argumentos nomeados
    
    Returns:
        tuple: Sempre (bool, str)
    """
    try:
        resultado = func(*args, **kwargs)
        return safe_unpack(resultado)
    except Exception as e:
        return False, f"Erro na execução: {str(e)}"

# Decorator para garantir retorno em tupla
def ensure_tuple(default_success_msg="Operação realizada com sucesso"):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                resultado = func(*args, **kwargs)
                return safe_unpack(resultado, default_success_msg)
            except Exception as e:
                return False, f"Erro: {str(e)}"
        return wrapper
    return decorator
