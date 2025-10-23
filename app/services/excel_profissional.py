"""
Módulo para geração de Excel Profissional com Dashboard Executivo
Transpontual - Sistema de Análise Financeira
"""

import io
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def gerar_excel_profissional(dados, filtros):
    """
    Gera Excel profissional com dashboard executivo, análises e gráficos

    Args:
        dados: Lista de dicts com dados dos CTEs
        filtros: Dict com filtros aplicados (cliente, dias, datas)

    Returns:
        BytesIO: Buffer com arquivo Excel completo
    """
    try:
        df = pd.DataFrame(dados)

        # Calcular métricas
        total_ctes = len(df)
        receita_total = df['Valor Total'].sum()
        ticket_medio = df['Valor Total'].mean() if total_ctes > 0 else 0
        ctes_baixados = len(df[df['Status'] == 'Baixado'])
        valor_baixado = df[df['Status'] == 'Baixado']['Valor Total'].sum()
        taxa_baixa = (ctes_baixados / total_ctes * 100) if total_ctes > 0 else 0

        # Análises por cliente
        analise_clientes = df.groupby('Cliente').agg({
            'Valor Total': ['sum', 'count', 'mean']
        }).round(2)
        analise_clientes.columns = ['Receita Total', 'Qtd CTEs', 'Ticket Médio']
        analise_clientes = analise_clientes.sort_values('Receita Total', ascending=False)
        analise_clientes['% do Total'] = (analise_clientes['Receita Total'] / receita_total * 100).round(2)
        analise_clientes = analise_clientes.reset_index()

        # Análise temporal
        df['Mes_Emissao'] = pd.to_datetime(df['Data Emissão'], format='%d/%m/%Y', errors='coerce').dt.to_period('M')
        evolucao_mensal = df.groupby('Mes_Emissao').agg({
            'Valor Total': 'sum',
            'Número CTE': 'count'
        }).reset_index()
        evolucao_mensal.columns = ['Mês', 'Receita', 'Quantidade']
        evolucao_mensal['Mês'] = evolucao_mensal['Mês'].astype(str)

        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            workbook = writer.book

            # Criar formatos
            formats = _criar_formatos(workbook)

            # Aba 1: Dashboard Executivo
            _criar_dashboard(workbook, df, formats, {
                'total_ctes': total_ctes,
                'receita_total': receita_total,
                'ticket_medio': ticket_medio,
                'taxa_baixa': taxa_baixa,
                'ctes_baixados': ctes_baixados,
                'valor_baixado': valor_baixado
            }, filtros)

            # Aba 2: Análise por Cliente
            _criar_aba_clientes(writer, analise_clientes, formats)

            # Aba 3: Evolução Mensal
            _criar_aba_evolucao(writer, evolucao_mensal, formats, workbook)

            # Aba 4: Dados Completos com Filtros
            _criar_aba_dados(writer, df, formats)

        buffer.seek(0)
        return buffer

    except Exception as e:
        logger.error(f"Erro ao gerar Excel profissional: {str(e)}")
        raise


def _criar_formatos(workbook):
    """Cria todos os formatos necessários"""
    return {
        'titulo_dash': workbook.add_format({
            'bold': True,
            'font_size': 24,
            'font_color': '#2c3e50',
            'align': 'center',
            'valign': 'vcenter'
        }),
        'kpi_label': workbook.add_format({
            'bold': True,
            'font_size': 10,
            'font_color': '#7f8c8d',
            'align': 'center',
            'valign': 'top',
            'text_wrap': True
        }),
        'kpi_blue': workbook.add_format({
            'bold': True,
            'font_size': 20,
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#3498db',
            'border': 2,
            'border_color': '#2980b9'
        }),
        'kpi_green': workbook.add_format({
            'bold': True,
            'font_size': 20,
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#27ae60',
            'border': 2,
            'border_color': '#229954'
        }),
        'kpi_orange': workbook.add_format({
            'bold': True,
            'font_size': 20,
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#e67e22',
            'border': 2,
            'border_color': '#d35400'
        }),
        'header': workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'vcenter',
            'align': 'center',
            'fg_color': '#2c3e50',
            'font_color': 'white',
            'border': 1,
            'font_size': 11
        }),
        'money': workbook.add_format({
            'num_format': 'R$ #,##0.00',
            'border': 1,
            'align': 'right'
        }),
        'percent': workbook.add_format({
            'num_format': '0.00"%"',
            'border': 1,
            'align': 'right'
        }),
        'cell': workbook.add_format({
            'border': 1,
            'valign': 'vcenter'
        }),
        'status_baixado': workbook.add_format({
            'bg_color': '#d4edda',
            'font_color': '#155724',
            'bold': True,
            'border': 1,
            'align': 'center'
        }),
        'status_pendente': workbook.add_format({
            'bg_color': '#fff3cd',
            'font_color': '#856404',
            'bold': True,
            'border': 1,
            'align': 'center'
        }),
        'subtitle': workbook.add_format({
            'bold': True,
            'font_size': 14,
            'font_color': '#2c3e50',
            'bottom': 2,
            'bottom_color': '#3498db'
        })
    }


def _criar_dashboard(workbook, df, formats, metricas, filtros):
    """Cria aba de Dashboard Executivo"""
    dash_ws = workbook.add_worksheet('📊 Dashboard')
    dash_ws.set_column('A:P', 8)

    # Título
    dash_ws.merge_range('A1:P2', '📊 DASHBOARD EXECUTIVO - ANÁLISE FINANCEIRA', formats['titulo_dash'])
    dash_ws.set_row(0, 30)
    dash_ws.set_row(1, 10)

    # Info geração
    dash_ws.merge_range('A3:P3', f'Gerado em: {datetime.now().strftime("%d/%m/%Y às %H:%M:%S")} | '
                                  f'Período: {filtros.get("filtro_dias", 180)} dias | '
                                  f'Cliente: {filtros.get("filtro_cliente", "Todos")}',
                        workbook.add_format({'align': 'center', 'font_color': '#7f8c8d', 'font_size': 9}))

    # KPIs - Linha 5
    kpis_row = 4

    # KPI 1: Total CTEs
    dash_ws.merge_range(kpis_row, 0, kpis_row+2, 2, metricas['total_ctes'], formats['kpi_blue'])
    dash_ws.merge_range(kpis_row+3, 0, kpis_row+3, 2, 'TOTAL CTEs', formats['kpi_label'])

    # KPI 2: Receita Total
    dash_ws.merge_range(kpis_row, 3, kpis_row+2, 5,
                       f'R$ {metricas["receita_total"]:,.0f}'.replace(',', '.'), formats['kpi_green'])
    dash_ws.merge_range(kpis_row+3, 3, kpis_row+3, 5, 'RECEITA TOTAL', formats['kpi_label'])

    # KPI 3: Ticket Médio
    dash_ws.merge_range(kpis_row, 6, kpis_row+2, 8,
                       f'R$ {metricas["ticket_medio"]:,.0f}'.replace(',', '.'), formats['kpi_orange'])
    dash_ws.merge_range(kpis_row+3, 6, kpis_row+3, 8, 'TICKET MÉDIO', formats['kpi_label'])

    # KPI 4: Taxa de Baixa
    dash_ws.merge_range(kpis_row, 9, kpis_row+2, 11, f'{metricas["taxa_baixa"]:.1f}%', formats['kpi_blue'])
    dash_ws.merge_range(kpis_row+3, 9, kpis_row+3, 11, 'TAXA DE BAIXA', formats['kpi_label'])

    # Top 5 Clientes - Linha 10
    dash_ws.merge_range('A11:P11', 'TOP 5 CLIENTES POR RECEITA', formats['subtitle'])

    top5 = df.groupby('Cliente')['Valor Total'].sum().sort_values(ascending=False).head(5)

    # Criar gráfico de barras horizontais
    chart_top5 = workbook.add_chart({'type': 'bar'})

    # Escrever dados para o gráfico
    start_row = 12
    dash_ws.write(start_row, 0, 'Cliente', formats['header'])
    dash_ws.write(start_row, 1, 'Receita', formats['header'])

    for idx, (cliente, receita) in enumerate(top5.items(), start=1):
        dash_ws.write(start_row + idx, 0, cliente[:30])  # Limitar nome
        dash_ws.write(start_row + idx, 1, receita, formats['money'])

    # Configurar gráfico
    chart_top5.add_series({
        'name': 'Receita',
        'categories': ['📊 Dashboard', start_row+1, 0, start_row+len(top5), 0],
        'values': ['📊 Dashboard', start_row+1, 1, start_row+len(top5), 1],
        'fill': {'color': '#27ae60'},
        'data_labels': {'value': True, 'num_format': 'R$ #,##0'}
    })

    chart_top5.set_title({'name': 'Top 5 Clientes', 'name_font': {'size': 14, 'bold': True}})
    chart_top5.set_x_axis({'name': 'Receita (R$)'})
    chart_top5.set_size({'width': 480, 'height': 300})
    chart_top5.set_legend({'none': True})

    dash_ws.insert_chart('D12', chart_top5)

    # Status dos CTEs - Pizza
    chart_status = workbook.add_chart({'type': 'pie'})

    status_counts = df['Status'].value_counts()
    status_row = 12
    dash_ws.write(status_row, 9, 'Status', formats['header'])
    dash_ws.write(status_row, 10, 'Quantidade', formats['header'])

    for idx, (status, count) in enumerate(status_counts.items(), 1):
        dash_ws.write(status_row + idx, 9, status)
        dash_ws.write(status_row + idx, 10, count)

    chart_status.add_series({
        'name': 'Distribuição',
        'categories': ['📊 Dashboard', status_row+1, 9, status_row+len(status_counts), 9],
        'values': ['📊 Dashboard', status_row+1, 10, status_row+len(status_counts), 10],
        'data_labels': {'percentage': True},
        'points': [
            {'fill': {'color': '#27ae60'}},  # Baixado
            {'fill': {'color': '#e67e22'}}   # Pendente
        ]
    })

    chart_status.set_title({'name': 'Status dos CTEs', 'name_font': {'size': 14, 'bold': True}})
    chart_status.set_size({'width': 360, 'height': 300})

    dash_ws.insert_chart('K12', chart_status)


def _criar_aba_clientes(writer, analise_clientes, formats):
    """Cria aba de análise por cliente com ranking"""
    analise_clientes.to_excel(writer, sheet_name='👥 Análise Clientes', index=False, startrow=1)

    ws = writer.sheets['👥 Análise Clientes']

    # Título
    ws.merge_range('A1:E1', 'ANÁLISE DETALHADA POR CLIENTE', formats['subtitle'])

    # Formatar cabeçalhos
    for col_num, value in enumerate(analise_clientes.columns):
        ws.write(1, col_num, value, formats['header'])

    # Aplicar formato de dinheiro e porcentagem
    for row_num in range(len(analise_clientes)):
        ws.write(row_num + 2, 1, analise_clientes.iloc[row_num]['Receita Total'], formats['money'])
        ws.write(row_num + 2, 3, analise_clientes.iloc[row_num]['Ticket Médio'], formats['money'])
        ws.write(row_num + 2, 4, analise_clientes.iloc[row_num]['% do Total'] / 100, formats['percent'])

    # Autoajustar colunas
    ws.set_column('A:A', 40)  # Cliente
    ws.set_column('B:B', 15)  # Receita
    ws.set_column('C:C', 12)  # Qtd
    ws.set_column('D:D', 15)  # Ticket
    ws.set_column('E:E', 12)  # %

    # Filtros automáticos
    ws.autofilter('A1:E{}'.format(len(analise_clientes) + 1))

    # Formatação condicional - Barras de dados na receita
    ws.conditional_format(2, 1, len(analise_clientes) + 1, 1, {
        'type': 'data_bar',
        'bar_color': '#27ae60',
        'bar_only': False
    })


def _criar_aba_evolucao(writer, evolucao_mensal, formats, workbook):
    """Cria aba de evolução temporal"""
    evolucao_mensal.to_excel(writer, sheet_name='📈 Evolução Mensal', index=False, startrow=1)

    ws = writer.sheets['📈 Evolução Mensal']

    # Título
    ws.merge_range('A1:C1', 'EVOLUÇÃO MENSAL DA RECEITA', formats['subtitle'])

    # Formatar cabeçalhos
    for col_num, value in enumerate(evolucao_mensal.columns):
        ws.write(1, col_num, value, formats['header'])

    # Aplicar formatos
    for row_num in range(len(evolucao_mensal)):
        ws.write(row_num + 2, 1, evolucao_mensal.iloc[row_num]['Receita'], formats['money'])

    ws.set_column('A:A', 12)
    ws.set_column('B:B', 15)
    ws.set_column('C:C', 12)

    # Gráfico de linha
    chart_linha = workbook.add_chart({'type': 'line'})
    chart_linha.add_series({
        'name': 'Receita Mensal',
        'categories': ['📈 Evolução Mensal', 2, 0, len(evolucao_mensal) + 1, 0],
        'values': ['📈 Evolução Mensal', 2, 1, len(evolucao_mensal) + 1, 1],
        'line': {'color': '#3498db', 'width': 2.5},
        'marker': {'type': 'circle', 'size': 6, 'fill': {'color': '#2980b9'}}
    })

    chart_linha.set_title({'name': 'Evolução da Receita', 'name_font': {'size': 14, 'bold': True}})
    chart_linha.set_x_axis({'name': 'Mês'})
    chart_linha.set_y_axis({'name': 'Receita (R$)', 'num_format': 'R$ #,##0'})
    chart_linha.set_size({'width': 720, 'height': 400})

    ws.insert_chart('E2', chart_linha)


def _criar_aba_dados(writer, df, formats):
    """Cria aba de dados completos com filtros"""
    # Remover coluna auxiliar de análise
    df_export = df.drop(columns=['Mes_Emissao'], errors='ignore')

    df_export.to_excel(writer, sheet_name='📋 Dados Completos', index=False, startrow=1)

    ws = writer.sheets['📋 Dados Completos']

    # Título
    ws.merge_range('A1:O1', 'DADOS COMPLETOS - TODOS OS CTEs', formats['subtitle'])

    # Formatar cabeçalhos
    for col_num, value in enumerate(df_export.columns):
        ws.write(1, col_num, value, formats['header'])

    # Congelar primeira linha
    ws.freeze_panes(2, 0)

    # Filtros automáticos
    ws.autofilter('A1:O{}'.format(len(df_export) + 1))

    # Aplicar formatação nas colunas
    for col_num, col_name in enumerate(df_export.columns):
        if col_name == 'Valor Total':
            for row_num in range(len(df_export)):
                ws.write(row_num + 2, col_num, df_export.iloc[row_num][col_name], formats['money'])
        elif col_name == 'Status':
            for row_num in range(len(df_export)):
                status = df_export.iloc[row_num][col_name]
                fmt = formats['status_baixado'] if status == 'Baixado' else formats['status_pendente']
                ws.write(row_num + 2, col_num, status, fmt)

    # Autoajustar largura
    for i, col in enumerate(df_export.columns):
        max_length = max(df_export[col].astype(str).map(len).max(), len(str(col)))
        ws.set_column(i, i, min(max_length + 2, 50))
