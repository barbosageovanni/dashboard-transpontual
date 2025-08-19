#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de Exportação - Dashboard Baker Flask
app/services/exportacao_service.py
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any
from io import BytesIO, StringIO
import xlsxwriter
import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import logging

class ExportacaoService:
    """Serviço para exportação de relatórios em múltiplos formatos"""
    
    @staticmethod
    def exportar_json(dados_analise: Dict, metadata: Dict = None) -> str:
        """
        Exporta dados de análise em formato JSON
        
        Args:
            dados_analise: Dados da análise financeira
            metadata: Metadados adicionais
            
        Returns:
            str: JSON formatado
        """
        try:
            export_data = {
                'analise_financeira': dados_analise,
                'metadata': metadata or {
                    'gerado_em': datetime.now().isoformat(),
                    'versao': '1.0',
                    'fonte': 'Dashboard Baker'
                },
                'resumo_executivo': ExportacaoService._gerar_resumo_executivo(dados_analise)
            }
            
            return json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
            
        except Exception as e:
            logging.error(f"Erro na exportação JSON: {str(e)}")
            return json.dumps({'erro': str(e)}, indent=2)
    
    @staticmethod
    def exportar_excel(dados_analise: Dict, metadata: Dict = None) -> BytesIO:
        """
        Exporta dados em formato Excel com múltiplas abas
        
        Args:
            dados_analise: Dados da análise financeira
            metadata: Metadados adicionais
            
        Returns:
            BytesIO: Arquivo Excel em memória
        """
        try:
            output = BytesIO()
            
            # Criar workbook
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            
            # Definir formatos
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#28a745',
                'font_color': 'white',
                'align': 'center',
                'border': 1
            })
            
            currency_format = workbook.add_format({
                'num_format': 'R$ #,##0.00',
                'align': 'right'
            })
            
            percentage_format = workbook.add_format({
                'num_format': '0.00%',
                'align': 'right'
            })
            
            date_format = workbook.add_format({
                'num_format': 'dd/mm/yyyy',
                'align': 'center'
            })
            
            # Aba 1: Resumo Executivo
            ExportacaoService._criar_aba_resumo_excel(
                workbook, dados_analise, header_format, currency_format, percentage_format
            )
            
            # Aba 2: Receita Mensal
            ExportacaoService._criar_aba_receita_mensal_excel(
                workbook, dados_analise, header_format, currency_format
            )
            
            # Aba 3: Top Clientes
            ExportacaoService._criar_aba_top_clientes_excel(
                workbook, dados_analise, header_format, currency_format, percentage_format
            )
            
            # Aba 4: Métricas Detalhadas
            ExportacaoService._criar_aba_metricas_excel(
                workbook, dados_analise, header_format, currency_format
            )
            
            # Aba 5: Dados Brutos (se houver)
            if 'dados_brutos' in dados_analise:
                ExportacaoService._criar_aba_dados_brutos_excel(
                    workbook, dados_analise['dados_brutos'], header_format
                )
            
            workbook.close()
            output.seek(0)
            
            return output
            
        except Exception as e:
            logging.error(f"Erro na exportação Excel: {str(e)}")
            # Retornar arquivo mínimo em caso de erro
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet('Erro')
            worksheet.write('A1', f'Erro na exportação: {str(e)}')
            workbook.close()
            output.seek(0)
            return output
    
    @staticmethod
    def exportar_csv(dados_analise: Dict, aba: str = 'resumo') -> str:
        """
        Exporta dados específicos em formato CSV
        
        Args:
            dados_analise: Dados da análise financeira
            aba: Qual conjunto de dados exportar ('resumo', 'clientes', 'receita')
            
        Returns:
            str: Conteúdo CSV
        """
        try:
            if aba == 'resumo':
                return ExportacaoService._csv_resumo_executivo(dados_analise)
            elif aba == 'clientes':
                return ExportacaoService._csv_top_clientes(dados_analise)
            elif aba == 'receita':
                return ExportacaoService._csv_receita_mensal(dados_analise)
            else:
                return ExportacaoService._csv_resumo_executivo(dados_analise)
                
        except Exception as e:
            logging.error(f"Erro na exportação CSV: {str(e)}")
            return f"Erro na exportação CSV: {str(e)}"
    
    @staticmethod
    def exportar_pdf(dados_analise: Dict, metadata: Dict = None) -> BytesIO:
        """
        Exporta relatório completo em PDF
        
        Args:
            dados_analise: Dados da análise financeira
            metadata: Metadados adicionais
            
        Returns:
            BytesIO: Arquivo PDF em memória
        """
        try:
            output = BytesIO()
            doc = SimpleDocTemplate(
                output,
                pagesize=A4,
                topMargin=72,
                bottomMargin=72,
                leftMargin=72,
                rightMargin=72
            )
            
            # Estilos
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.HexColor('#28a745'),
                alignment=1  # Center
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=12,
                textColor=colors.HexColor('#495057')
            )
            
            # Conteúdo do PDF
            story = []
            
            # Título
            story.append(Paragraph("📊 Relatório de Análise Financeira", title_style))
            story.append(Paragraph(f"Dashboard Baker - {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Resumo Executivo
            story.extend(ExportacaoService._pdf_resumo_executivo(dados_analise, heading_style, styles))
            
            # Métricas Principais
            story.extend(ExportacaoService._pdf_metricas_principais(dados_analise, heading_style, styles))
            
            # Top Clientes
            story.extend(ExportacaoService._pdf_top_clientes(dados_analise, heading_style, styles))
            
            # Análise de Tendência
            story.extend(ExportacaoService._pdf_tendencia(dados_analise, heading_style, styles))
            
            # Stress Test
            story.extend(ExportacaoService._pdf_stress_test(dados_analise, heading_style, styles))
            
            # Rodapé
            story.append(Spacer(1, 30))
            story.append(Paragraph(
                "Relatório gerado automaticamente pelo Dashboard Baker",
                styles['Normal']
            ))
            
            # Gerar PDF
            doc.build(story)
            output.seek(0)
            
            return output
            
        except Exception as e:
            logging.error(f"Erro na exportação PDF: {str(e)}")
            # PDF mínimo em caso de erro
            output = BytesIO()
            doc = SimpleDocTemplate(output, pagesize=letter)
            styles = getSampleStyleSheet()
            story = [Paragraph(f"Erro na geração do PDF: {str(e)}", styles['Normal'])]
            doc.build(story)
            output.seek(0)
            return output
    
    # Métodos auxiliares para Excel
    @staticmethod
    def _criar_aba_resumo_excel(workbook, dados, header_format, currency_format, percentage_format):
        """Cria aba de resumo executivo no Excel"""
        worksheet = workbook.add_worksheet('Resumo Executivo')
        
        # Cabeçalho
        worksheet.merge_range('A1:D1', 'RESUMO EXECUTIVO - ANÁLISE FINANCEIRA', header_format)
        worksheet.write('A2', f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}')
        
        row = 4
        
        # Receita Mensal
        if 'receita_mensal' in dados:
            receita = dados['receita_mensal']
            worksheet.write(row, 0, 'RECEITA MENSAL', header_format)
            row += 1
            worksheet.write(row, 0, 'Receita Mês Corrente')
            worksheet.write(row, 1, receita.get('receita_mes_corrente', 0), currency_format)
            row += 1
            worksheet.write(row, 0, 'Variação Mensal')
            worksheet.write(row, 1, receita.get('variacao_percentual', 0) / 100, percentage_format)
            row += 2
        
        # Receita por Inclusão Fatura (NOVA MÉTRICA)
        if 'receita_por_inclusao_fatura' in dados:
            inclusao = dados['receita_por_inclusao_fatura']
            worksheet.write(row, 0, 'RECEITA POR INCLUSÃO FATURA', header_format)
            row += 1
            worksheet.write(row, 0, 'Receita Total Período')
            worksheet.write(row, 1, inclusao.get('receita_total_periodo', 0), currency_format)
            row += 1
            worksheet.write(row, 0, 'Cobertura (%)')
            worksheet.write(row, 1, inclusao.get('percentual_cobertura', 0) / 100, percentage_format)
            row += 1
            worksheet.write(row, 0, 'Status')
            worksheet.write(row, 1, inclusao.get('status', 'N/A'))
            row += 2
        
        # Concentração
        if 'concentracao_clientes' in dados:
            concentracao = dados['concentracao_clientes']
            worksheet.write(row, 0, 'CONCENTRAÇÃO DE CLIENTES', header_format)
            row += 1
            worksheet.write(row, 0, 'Top 5 Clientes (%)')
            worksheet.write(row, 1, concentracao.get('percentual_top5', 0) / 100, percentage_format)
            row += 2
        
        # Ajustar larguras das colunas
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 15)
    
    @staticmethod
    def _criar_aba_receita_mensal_excel(workbook, dados, header_format, currency_format):
        """Cria aba com evolução da receita mensal"""
        worksheet = workbook.add_worksheet('Receita Mensal')
        
        if 'graficos' in dados and 'receita_mensal' in dados['graficos']:
            grafico_dados = dados['graficos']['receita_mensal']
            
            # Cabeçalhos
            headers = ['Mês', 'Receita', 'Quantidade CTEs']
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_format)
            
            # Dados
            labels = grafico_dados.get('labels', [])
            valores = grafico_dados.get('valores', [])
            qtds = grafico_dados.get('quantidade_ctes', [])
            
            for row, (label, valor, qtd) in enumerate(zip(labels, valores, qtds), 1):
                worksheet.write(row, 0, label)
                worksheet.write(row, 1, valor, currency_format)
                worksheet.write(row, 2, qtd)
        
        # Ajustar larguras
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
    
    @staticmethod
    def _criar_aba_top_clientes_excel(workbook, dados, header_format, currency_format, percentage_format):
        """Cria aba com top clientes"""
        worksheet = workbook.add_worksheet('Top Clientes')
        
        if 'concentracao_clientes' in dados and 'top_clientes' in dados['concentracao_clientes']:
            top_clientes = dados['concentracao_clientes']['top_clientes']
            
            # Cabeçalhos
            headers = ['Posição', 'Cliente', 'Receita', 'Percentual']
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_format)
            
            # Dados
            for row, cliente in enumerate(top_clientes, 1):
                worksheet.write(row, 0, cliente.get('posicao', row))
                worksheet.write(row, 1, cliente.get('nome', ''))
                worksheet.write(row, 2, cliente.get('receita', 0), currency_format)
                worksheet.write(row, 3, cliente.get('percentual', 0) / 100, percentage_format)
        
        # Ajustar larguras
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 12)
    
    @staticmethod
    def _criar_aba_metricas_excel(workbook, dados, header_format, currency_format):
        """Cria aba com todas as métricas detalhadas"""
        worksheet = workbook.add_worksheet('Métricas Detalhadas')
        
        row = 0
        
        # Todas as métricas
        metricas = [
            ('Ticket Médio', dados.get('ticket_medio', {})),
            ('Tempo Médio Cobrança', dados.get('tempo_medio_cobranca', {})),
            ('Tendência Linear', dados.get('tendencia_linear', {}))
        ]
        
        for nome_metrica, metrica_dados in metricas:
            worksheet.write(row, 0, nome_metrica, header_format)
            row += 1
            
            for key, value in metrica_dados.items():
                worksheet.write(row, 0, key.replace('_', ' ').title())
                if isinstance(value, (int, float)):
                    if 'valor' in key.lower() or 'receita' in key.lower():
                        worksheet.write(row, 1, value, currency_format)
                    else:
                        worksheet.write(row, 1, value)
                else:
                    worksheet.write(row, 1, str(value))
                row += 1
            
            row += 1  # Espaço entre métricas
    
    # Métodos auxiliares para CSV
    @staticmethod
    def _csv_resumo_executivo(dados):
        """Gera CSV do resumo executivo"""
        linhas = ['Métrica,Valor']
        
        if 'receita_mensal' in dados:
            receita = dados['receita_mensal']
            linhas.append(f"Receita Mês Corrente,{receita.get('receita_mes_corrente', 0)}")
            linhas.append(f"Variação Mensal (%),{receita.get('variacao_percentual', 0)}")
        
        if 'receita_por_inclusao_fatura' in dados:
            inclusao = dados['receita_por_inclusao_fatura']
            linhas.append(f"Receita Inclusão Fatura,{inclusao.get('receita_total_periodo', 0)}")
            linhas.append(f"Cobertura Inclusão (%),{inclusao.get('percentual_cobertura', 0)}")
        
        return '\n'.join(linhas)
    
    @staticmethod
    def _csv_top_clientes(dados):
        """Gera CSV dos top clientes"""
        linhas = ['Posição,Cliente,Receita,Percentual']
        
        if 'concentracao_clientes' in dados:
            top_clientes = dados['concentracao_clientes'].get('top_clientes', [])
            for cliente in top_clientes:
                linhas.append(f"{cliente.get('posicao', '')},{cliente.get('nome', '')},{cliente.get('receita', 0)},{cliente.get('percentual', 0)}")
        
        return '\n'.join(linhas)
    
    @staticmethod
    def _csv_receita_mensal(dados):
        """Gera CSV da receita mensal"""
        linhas = ['Mês,Receita,Quantidade_CTEs']
        
        if 'graficos' in dados and 'receita_mensal' in dados['graficos']:
            grafico = dados['graficos']['receita_mensal']
            labels = grafico.get('labels', [])
            valores = grafico.get('valores', [])
            qtds = grafico.get('quantidade_ctes', [])
            
            for label, valor, qtd in zip(labels, valores, qtds):
                linhas.append(f"{label},{valor},{qtd}")
        
        return '\n'.join(linhas)
    
    # Métodos auxiliares para PDF
    @staticmethod
    def _pdf_resumo_executivo(dados, heading_style, styles):
        """Gera seção de resumo executivo para PDF"""
        story = []
        story.append(Paragraph("💰 Resumo Executivo", heading_style))
        
        resumo_data = []
        
        if 'receita_mensal' in dados:
            receita = dados['receita_mensal']
            resumo_data.extend([
                ['Receita Mês Corrente', f"R$ {receita.get('receita_mes_corrente', 0):,.2f}"],
                ['Variação Mensal', f"{receita.get('variacao_percentual', 0):.2f}%"]
            ])
        
        # NOVA MÉTRICA no PDF
        if 'receita_por_inclusao_fatura' in dados:
            inclusao = dados['receita_por_inclusao_fatura']
            resumo_data.extend([
                ['Receita por Inclusão Fatura', f"R$ {inclusao.get('receita_total_periodo', 0):,.2f}"],
                ['Cobertura Inclusão', f"{inclusao.get('percentual_cobertura', 0):.2f}%"],
                ['Status Inclusão', inclusao.get('status', 'N/A')]
            ])
        
        if resumo_data:
            table = Table(resumo_data, colWidths=[3*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
        
        story.append(Spacer(1, 20))
        return story
    
    @staticmethod
    def _pdf_metricas_principais(dados, heading_style, styles):
        """Gera seção de métricas principais para PDF"""
        story = []
        story.append(Paragraph("📊 Métricas Principais", heading_style))
        
        metricas_data = []
        
        if 'ticket_medio' in dados:
            ticket = dados['ticket_medio']
            metricas_data.append(['Ticket Médio', f"R$ {ticket.get('valor', 0):,.2f}"])
        
        if 'tempo_medio_cobranca' in dados:
            tempo = dados['tempo_medio_cobranca']
            metricas_data.append(['Tempo Médio Cobrança', f"{tempo.get('dias_medio', 0)} dias"])
        
        if 'concentracao_clientes' in dados:
            concentracao = dados['concentracao_clientes']
            metricas_data.append(['Concentração Top 5', f"{concentracao.get('percentual_top5', 0):.2f}%"])
        
        if metricas_data:
            table = Table(metricas_data, colWidths=[3*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#17a2b8')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
        
        story.append(Spacer(1, 20))
        return story
    
    @staticmethod
    def _pdf_top_clientes(dados, heading_style, styles):
        """Gera seção de top clientes para PDF"""
        story = []
        story.append(Paragraph("👑 Top 5 Clientes", heading_style))
        
        if 'concentracao_clientes' in dados and 'top_clientes' in dados['concentracao_clientes']:
            top_clientes = dados['concentracao_clientes']['top_clientes']
            
            clientes_data = [['Pos.', 'Cliente', 'Receita', '%']]
            
            for cliente in top_clientes[:5]:
                clientes_data.append([
                    str(cliente.get('posicao', '')),
                    cliente.get('nome', '')[:30] + '...' if len(cliente.get('nome', '')) > 30 else cliente.get('nome', ''),
                    f"R$ {cliente.get('receita', 0):,.0f}",
                    f"{cliente.get('percentual', 0):.1f}%"
                ])
            
            table = Table(clientes_data, colWidths=[0.5*inch, 3*inch, 1.2*inch, 0.8*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ffc107')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 9)
            ]))
            story.append(table)
        
        story.append(Spacer(1, 20))
        return story
    
    @staticmethod
    def _pdf_tendencia(dados, heading_style, styles):
        """Gera seção de análise de tendência para PDF"""
        story = []
        story.append(Paragraph("📈 Análise de Tendência", heading_style))
        
        if 'tendencia_linear' in dados:
            tendencia = dados['tendencia_linear']
            
            tendencia_data = [
                ['Inclinação', f"{tendencia.get('inclinacao', 0):.2f}"],
                ['R²', f"{tendencia.get('r_squared', 0):.3f}"],
                ['Previsão Próximo Mês', f"R$ {tendencia.get('previsao_proximo_mes', 0):,.2f}"]
            ]
            
            table = Table(tendencia_data, colWidths=[2.5*inch, 2.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc3545')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
        
        story.append(Spacer(1, 20))
        return story
    
    @staticmethod
    def _pdf_stress_test(dados, heading_style, styles):
        """Gera seção de stress test para PDF"""
        story = []
        story.append(Paragraph("⚠️ Stress Test", heading_style))
        
        if 'stress_test_receita' in dados and 'cenarios' in dados['stress_test_receita']:
            cenarios = dados['stress_test_receita']['cenarios']
            
            if cenarios:
                stress_data = [['Cenário', 'Receita Perdida', 'Impacto %', 'Receita Restante']]
                
                for cenario in cenarios:
                    stress_data.append([
                        cenario.get('cenario', ''),
                        f"R$ {cenario.get('receita_perdida', 0):,.0f}",
                        f"{cenario.get('percentual_impacto', 0):.1f}%",
                        f"R$ {cenario.get('receita_restante', 0):,.0f}"
                    ])
                
                table = Table(stress_data, colWidths=[1.5*inch, 1.3*inch, 1*inch, 1.7*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6c757d')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 0), (-1, -1), 8)
                ]))
                story.append(table)
        
        return story
    
    @staticmethod
    def _gerar_resumo_executivo(dados_analise: Dict) -> Dict:
        """Gera resumo executivo dos dados"""
        try:
            resumo = {
                'metricas_principais': {},
                'alertas': [],
                'recomendacoes': []
            }
            
            # Métricas principais
            if 'receita_mensal' in dados_analise:
                receita = dados_analise['receita_mensal']
                resumo['metricas_principais']['receita_mes_corrente'] = receita.get('receita_mes_corrente', 0)
                resumo['metricas_principais']['variacao_mensal'] = receita.get('variacao_percentual', 0)
            
            # NOVA MÉTRICA no resumo
            if 'receita_por_inclusao_fatura' in dados_analise:
                inclusao = dados_analise['receita_por_inclusao_fatura']
                resumo['metricas_principais']['receita_inclusao_fatura'] = inclusao.get('receita_total_periodo', 0)
                resumo['metricas_principais']['cobertura_inclusao'] = inclusao.get('percentual_cobertura', 0)
                
                # Alertas baseados na cobertura
                cobertura = inclusao.get('percentual_cobertura', 0)
                if cobertura < 50:
                    resumo['alertas'].append('Baixa cobertura de inclusão de faturas - completar dados para análise mais precisa')
            
            # Concentração
            if 'concentracao_clientes' in dados_analise:
                concentracao = dados_analise['concentracao_clientes']['percentual_top5']
                resumo['metricas_principais']['concentracao_top5'] = concentracao
                
                if concentracao > 70:
                    resumo['alertas'].append('Alta concentração de receita - risco de dependência')
                    resumo['recomendacoes'].append('Diversificar base de clientes')
            
            # Tendência
            if 'tendencia_linear' in dados_analise:
                inclinacao = dados_analise['tendencia_linear']['inclinacao']
                if inclinacao < 0:
                    resumo['alertas'].append('Tendência de declínio na receita')
                    resumo['recomendacoes'].append('Implementar estratégias de recuperação')
            
            return resumo
            
        except Exception as e:
            logging.error(f"Erro ao gerar resumo executivo: {str(e)}")
            return {'erro': str(e)}