#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitários para correção de formatação de datas
app/utils/date_utils.py - CORREÇÃO DOS PROBLEMAS DE DATAS
"""

from datetime import datetime, date
from typing import Optional, Union
import re
import logging

class DateParser:
    """Parser robusto para datas em múltiplos formatos brasileiros"""
    
    # Mapeamento de meses em português para números
    MESES_PORTUGUES = {
        'jan': 1, 'janeiro': 1,
        'fev': 2, 'fevereiro': 2,
        'mar': 3, 'março': 3, 'marco': 3,
        'abr': 4, 'abril': 4,
        'mai': 5, 'maio': 5,
        'jun': 6, 'junho': 6,
        'jul': 7, 'julho': 7,
        'ago': 8, 'agosto': 8,
        'set': 9, 'setembro': 9,
        'out': 10, 'outubro': 10,
        'nov': 11, 'novembro': 11,
        'dez': 12, 'dezembro': 12
    }
    
    @classmethod
    def parse_date_br(cls, data_str: Union[str, date, datetime, None]) -> Optional[date]:
        """
        Parser robusto para datas brasileiras
        
        Formatos suportados:
        - DD/MM/YYYY, DD-MM-YYYY
        - DD/ago (29/ago) -> converte para ano atual
        - YYYY-MM-DD (ISO)
        - date e datetime objects
        
        Args:
            data_str: String ou objeto de data para converter
            
        Returns:
            date object ou None se não conseguir converter
        """
        if not data_str:
            return None
            
        try:
            # Se já é um objeto date/datetime
            if isinstance(data_str, date):
                return data_str
            elif isinstance(data_str, datetime):
                return data_str.date()
            
            # Converter para string e limpar
            data_str = str(data_str).strip().lower()
            
            if not data_str or data_str in ['', 'null', 'none', 'nan']:
                return None
            
            # 1. Formato DD/MMM (ex: 29/ago) - assumir ano atual
            padrao_mes_abrev = r'^(\d{1,2})[\/\-]([a-z]{3})$'
            match = re.match(padrao_mes_abrev, data_str)
            if match:
                dia = int(match.group(1))
                mes_str = match.group(2)
                ano = datetime.now().year
                
                if mes_str in cls.MESES_PORTUGUES:
                    mes = cls.MESES_PORTUGUES[mes_str]
                    try:
                        return date(ano, mes, dia)
                    except ValueError as e:
                        logging.warning(f"Data inválida: {dia}/{mes}/{ano} - {e}")
                        return None
                else:
                    logging.warning(f"Mês não reconhecido: {mes_str}")
                    return None
            
            # 2. Formato DD/MM/YYYY ou DD-MM-YYYY
            padrao_br = r'^(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})$'
            match = re.match(padrao_br, data_str)
            if match:
                dia = int(match.group(1))
                mes = int(match.group(2))
                ano = int(match.group(3))
                try:
                    return date(ano, mes, dia)
                except ValueError as e:
                    logging.warning(f"Data inválida: {dia}/{mes}/{ano} - {e}")
                    return None
            
            # 3. Formato ISO (YYYY-MM-DD)
            padrao_iso = r'^(\d{4})-(\d{1,2})-(\d{1,2})$'
            match = re.match(padrao_iso, data_str)
            if match:
                ano = int(match.group(1))
                mes = int(match.group(2))
                dia = int(match.group(3))
                try:
                    return date(ano, mes, dia)
                except ValueError as e:
                    logging.warning(f"Data ISO inválida: {ano}-{mes}-{dia} - {e}")
                    return None
            
            # 4. Tentar parsing automático do datetime
            try:
                dt = datetime.strptime(data_str, '%d/%m/%Y')
                return dt.date()
            except ValueError:
                pass
            
            try:
                dt = datetime.strptime(data_str, '%Y-%m-%d')
                return dt.date()
            except ValueError:
                pass
            
            logging.warning(f"Formato de data não reconhecido: '{data_str}'")
            return None
            
        except Exception as e:
            logging.error(f"Erro ao converter data '{data_str}': {e}")
            return None
    
    @classmethod
    def format_date_br(cls, data_obj: Union[date, datetime, None]) -> Optional[str]:
        """
        Formata data para padrão brasileiro DD/MM/YYYY
        
        Args:
            data_obj: Objeto date ou datetime
            
        Returns:
            String formatada ou None
        """
        if not data_obj:
            return None
            
        try:
            if isinstance(data_obj, datetime):
                data_obj = data_obj.date()
            elif isinstance(data_obj, date):
                pass
            else:
                return None
                
            return data_obj.strftime('%d/%m/%Y')
            
        except Exception as e:
            logging.error(f"Erro ao formatar data {data_obj}: {e}")
            return None
    
    @classmethod
    def format_date_iso(cls, data_obj: Union[date, datetime, None]) -> Optional[str]:
        """
        Formata data para padrão ISO YYYY-MM-DD
        
        Args:
            data_obj: Objeto date ou datetime
            
        Returns:
            String formatada ou None
        """
        if not data_obj:
            return None
            
        try:
            if isinstance(data_obj, datetime):
                data_obj = data_obj.date()
            elif isinstance(data_obj, date):
                pass
            else:
                return None
                
            return data_obj.strftime('%Y-%m-%d')
            
        except Exception as e:
            logging.error(f"Erro ao formatar data ISO {data_obj}: {e}")
            return None


# ==================== FUNÇÕES DE CONVENIÊNCIA ====================

def parse_date_safe(data_input: Union[str, date, datetime, None]) -> Optional[date]:
    """Função de conveniência para parsing seguro de datas"""
    return DateParser.parse_date_br(data_input)

def format_date_display(data_obj: Union[date, datetime, None]) -> str:
    """Formata data para exibição (formato brasileiro ou vazio)"""
    formatted = DateParser.format_date_br(data_obj)
    return formatted if formatted else ''

def format_date_json(data_obj: Union[date, datetime, None]) -> Optional[str]:
    """Formata data para JSON (formato ISO ou None)"""
    return DateParser.format_date_iso(data_obj)

def is_valid_date_string(data_str: str) -> bool:
    """Verifica se uma string pode ser convertida em data válida"""
    return DateParser.parse_date_br(data_str) is not None


# ==================== TESTE DAS FUNÇÕES ====================

if __name__ == "__main__":
    # Testes das funções de parsing
    test_dates = [
        "29/ago",
        "15/12/2024",
        "2024-08-29",
        "01/jan",
        "31/dez/2023",
        "",
        None,
        "data inválida"
    ]
    
    print("🧪 Testando parser de datas:")
    for test_date in test_dates:
        resultado = parse_date_safe(test_date)
        print(f"'{test_date}' -> {resultado} ({format_date_display(resultado)})")