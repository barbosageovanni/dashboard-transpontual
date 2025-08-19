#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço para geração de relatórios - Dashboard Baker Flask
"""

from io import BytesIO
import xlsxwriter
from datetime import datetime
from typing import List, Dict

class ReportService:
    """Serviço para geração de relatórios"""

    @staticmethod
    def gerar_relatorio_baixas_excel(ctes, estatisticas) -> BytesIO:
        """Gera relatório de baixas em Excel"""
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # Formatos
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#28a745',
            'font_color': 'white',
            'align': 'center'
        })

        currency_format = workbook.add_format({'num_format': 'R$ #,##0.00'})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})

        # Aba 1: Resumo
        worksheet1 = workbook.add_worksheet('Resumo de Baixas')
        
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        worksheet1.merge_range('A1:D1', f'Relatório de Baixas - {timestamp}', header_format)

        # Estatísticas
        row = 3
        worksheet1.write(row, 0, 'ESTATÍSTICAS DE BAIXAS', header_format)
        row += 2

        stats_lista = [
            ('Total de Baixas', estatisticas.get('total_baixas', 0)),
            ('Valor Baixado', estatisticas.get('valor_baixado', 0)),
            ('Baixas Pendentes', estatisticas.get('baixas_pendentes', 0)),
            ('Valor Pendente', estatisticas.get('valor_pendente', 0))
        ]

        for stat, valor in stats_lista:
            worksheet1.write(row, 0, stat)
            if 'Valor' in stat:
                worksheet1.write(row, 1, valor, currency_format)
            else:
                worksheet1.write(row, 1, valor)
            row += 1

        # Aba 2: Dados Detalhados
        if ctes:
            worksheet2 = workbook.add_worksheet('Dados Detalhados')
            
            # Cabeçalhos
            headers = ['CTE', 'Cliente', 'Valor', 'Emissão', 'Baixa', 'Status']
            for col, header in enumerate(headers):
                worksheet2.write(0, col, header, header_format)

            # Dados
            for row, cte in enumerate(ctes, 1):
                worksheet2.write(row, 0, cte.numero_cte)
                worksheet2.write(row, 1, cte.destinatario_nome or '')
                worksheet2.write(row, 2, float(cte.valor_total), currency_format)
                
                if cte.data_emissao:
                    worksheet2.write(row, 3, cte.data_emissao, date_format)
                
                if cte.data_baixa:
                    worksheet2.write(row, 4, cte.data_baixa, date_format)
                    worksheet2.write(row, 5, 'Baixado')
                else:
                    worksheet2.write(row, 5, 'Pendente')

        workbook.close()
        output.seek(0)
        return output

    @staticmethod
    def gerar_relatorio_baixas_html(ctes, estatisticas) -> str:
        """Gera relatório de baixas em HTML"""
        hoje = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Relatório de Baixas - {hoje}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; }}
                .header {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                           color: white; padding: 20px; text-align: center; border-radius: 8px; }}
                .metric-card {{ background: #f8f9fa; border-left: 4px solid #28a745; 
                               padding: 15px; margin: 10px 0; }}
                .metric-number {{ font-size: 20px; font-weight: bold; color: #28a745; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #28a745; color: white; }}
                .status-baixado {{ color: #28a745; font-weight: bold; }}
                .status-pendente {{ color: #dc3545; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>💳 Relatório de Baixas</h1>
                <p>Dashboard Baker - {hoje}</p>
            </div>

            <div class="metric-card">
                <div class="metric-number">{estatisticas.get('total_baixas', 0)}</div>
                <p><strong>Total de Baixas Realizadas</strong></p>
            </div>

            <div class="metric-card">
                <div class="metric-number">R$ {estatisticas.get('valor_baixado', 0):,.2f}</div>
                <p><strong>Valor Total Baixado</strong></p>
            </div>

            <div class="metric-card">
                <div class="metric-number">{estatisticas.get('baixas_pendentes', 0)}</div>
                <p><strong>Baixas Pendentes</strong></p>
            </div>

            <h2>📋 Detalhamento por CTE</h2>
            <table>
                <tr>
                    <th>CTE</th>
                    <th>Cliente</th>
                    <th>Valor (R$)</th>
                    <th>Data Emissão</th>
                    <th>Data Baixa</th>
                    <th>Status</th>
                </tr>
        """

        # Adicionar dados dos CTEs
        for cte in ctes[:100]:  # Máximo 100 registros no HTML
            data_emissao = cte.data_emissao.strftime('%d/%m/%Y') if cte.data_emissao else 'N/A'
            data_baixa = cte.data_baixa.strftime('%d/%m/%Y') if cte.data_baixa else 'N/A'
            status = 'Baixado' if cte.data_baixa else 'Pendente'
            status_class = 'status-baixado' if cte.data_baixa else 'status-pendente'
            
            html += f"""
                <tr>
                    <td>{cte.numero_cte}</td>
                    <td>{cte.destinatario_nome or 'N/A'}</td>
                    <td>R$ {float(cte.valor_total):,.2f}</td>
                    <td>{data_emissao}</td>
                    <td>{data_baixa}</td>
                    <td class="{status_class}">{status}</td>
                </tr>
            """

        html += """
            </table>
        </body>
        </html>
        """

        return html