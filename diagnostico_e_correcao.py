#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DIAGNÓSTICO E CORREÇÃO - Análise Financeira
Adicione estas rotas ao seu arquivo analise_financeira.py existente
"""

# ADICIONAR ESTAS ROTAS AO ARQUIVO analise_financeira.py:

@bp.route('/api/debug/base-dados')
@login_required  
def debug_base_dados():
    """API para debugar problemas na base de dados"""
    try:
        with db.engine.connect() as connection:
            # Verificar tabela existe
            sql_tabela = text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'dashboard_baker'")
            tabela_existe = connection.execute(sql_tabela).scalar()
            
            if not tabela_existe:
                return jsonify({
                    'success': False,
                    'error': 'Tabela dashboard_baker não encontrada',
                    'solucao': 'Verificar nome correto da tabela'
                })
            
            # Verificar registros totais
            sql_total = text("SELECT COUNT(*) FROM dashboard_baker")
            total_registros = connection.execute(sql_total).scalar()
            
            # Verificar registros últimos 180 dias
            data_limite = datetime.now().date() - timedelta(days=180)
            sql_periodo = text("SELECT COUNT(*) FROM dashboard_baker WHERE data_emissao >= :data_limite")
            registros_periodo = connection.execute(sql_periodo, {"data_limite": data_limite}).scalar()
            
            # Verificar campos importantes
            sql_campos = text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN envio_final IS NOT NULL THEN 1 END) as com_envio_final,
                    COUNT(CASE WHEN data_inclusao_fatura IS NOT NULL THEN 1 END) as com_inclusao_fatura,
                    COUNT(CASE WHEN numero_fatura IS NOT NULL AND numero_fatura != '' THEN 1 END) as com_numero_fatura,
                    COUNT(CASE WHEN data_baixa IS NOT NULL THEN 1 END) as com_baixa,
                    COUNT(CASE WHEN primeiro_envio IS NOT NULL THEN 1 END) as com_primeiro_envio,
                    COUNT(CASE WHEN destinatario_nome IS NOT NULL AND destinatario_nome != '' THEN 1 END) as com_cliente,
                    SUM(valor_total) as soma_valores
                FROM dashboard_baker 
                WHERE data_emissao >= :data_limite
            """)
            
            result_campos = connection.execute(sql_campos, {"data_limite": data_limite}).fetchone()
            
            # Verificar alguns registros de exemplo
            sql_exemplo = text("""
                SELECT 
                    numero_cte,
                    destinatario_nome,
                    valor_total,
                    data_emissao,
                    data_baixa,
                    envio_final,
                    data_inclusao_fatura
                FROM dashboard_baker 
                WHERE data_emissao >= :data_limite
                LIMIT 5
            """)
            
            exemplos_result = connection.execute(sql_exemplo, {"data_limite": data_limite}).fetchall()
            
            exemplos = []
            for row in exemplos_result:
                exemplos.append({
                    'numero_cte': row.numero_cte,
                    'cliente': row.destinatario_nome,
                    'valor': float(row.valor_total or 0),
                    'data_emissao': row.data_emissao.strftime('%d/%m/%Y') if row.data_emissao else None,
                    'tem_baixa': row.data_baixa is not None,
                    'tem_envio_final': row.envio_final is not None,
                    'tem_inclusao_fatura': row.data_inclusao_fatura is not None
                })
        
        diagnostico = {
            'total_registros_tabela': int(total_registros),
            'registros_ultimos_180_dias': int(registros_periodo),
            'campos_preenchidos': {
                'total': int(result_campos.total),
                'com_envio_final': int(result_campos.com_envio_final),
                'com_inclusao_fatura': int(result_campos.com_inclusao_fatura),
                'com_numero_fatura': int(result_campos.com_numero_fatura),
                'com_baixa': int(result_campos.com_baixa),
                'com_primeiro_envio': int(result_campos.com_primeiro_envio),
                'com_cliente': int(result_campos.com_cliente),
                'soma_valores': float(result_campos.soma_valores or 0)
            },
            'exemplos_registros': exemplos,
            'problemas_identificados': [],
            'recomendacoes': []
        }
        
        # Identificar problemas
        if registros_periodo == 0:
            diagnostico['problemas_identificados'].append("Nenhum registro nos últimos 180 dias")
            diagnostico['recomendacoes'].append("Verificar se há dados recentes na tabela")
        
        if result_campos.com_cliente == 0:
            diagnostico['problemas_identificados'].append("Nenhum registro com nome de cliente")
            diagnostico['recomendacoes'].append("Verificar campo destinatario_nome")
            
        if result_campos.soma_valores == 0:
            diagnostico['problemas_identificados'].append("Todos os valores estão zerados")
            diagnostico['recomendacoes'].append("Verificar campo valor_total")
        
        if result_campos.com_envio_final == 0 and result_campos.com_baixa == 0:
            diagnostico['problemas_identificados'].append("Sem dados de envio_final nem data_baixa")
            diagnostico['recomendacoes'].append("Receita faturada será 0 - preencher campos de controle")
            
        if result_campos.com_inclusao_fatura == 0 and result_campos.com_numero_fatura == 0:
            diagnostico['problemas_identificados'].append("Sem dados de faturas")
            diagnostico['recomendacoes'].append("Receita com faturas será 0 - preencher data_inclusao_fatura ou numero_fatura")
        
        return jsonify({
            'success': True,
            'diagnostico': diagnostico
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'tipo_erro': 'Erro de conexão ou SQL'
        }), 500

@bp.route('/api/metricas-forcadas')
@login_required
def api_metricas_forcadas():
    """API que força dados mesmo quando campos estão vazios"""
    try:
        filtro_dias = int(request.args.get('filtro_dias', 180))
        
        with db.engine.connect() as connection:
            data_limite = datetime.now().date() - timedelta(days=filtro_dias)
            
            # Query principal mais simples e robusta
            sql_principal = text("""
                SELECT 
                    COUNT(*) as total_ctes,
                    COALESCE(SUM(valor_total), 0) as receita_total,
                    COALESCE(AVG(valor_total), 0) as ticket_medio,
                    
                    -- Baixas (qualquer indicação de pagamento)
                    COUNT(CASE WHEN data_baixa IS NOT NULL THEN 1 END) as baixas_data_baixa,
                    COALESCE(SUM(CASE WHEN data_baixa IS NOT NULL THEN valor_total ELSE 0 END), 0) as valor_baixas_data_baixa,
                    
                    -- Envio final (faturamento)
                    COUNT(CASE WHEN envio_final IS NOT NULL THEN 1 END) as envio_final_count,
                    COALESCE(SUM(CASE WHEN envio_final IS NOT NULL THEN valor_total ELSE 0 END), 0) as envio_final_valor,
                    
                    -- Inclusão fatura
                    COUNT(CASE WHEN data_inclusao_fatura IS NOT NULL THEN 1 END) as inclusao_count,
                    COALESCE(SUM(CASE WHEN data_inclusao_fatura IS NOT NULL THEN valor_total ELSE 0 END), 0) as inclusao_valor,
                    
                    -- Número fatura (fallback)
                    COUNT(CASE WHEN numero_fatura IS NOT NULL AND numero_fatura != '' THEN 1 END) as numero_fatura_count,
                    COALESCE(SUM(CASE WHEN numero_fatura IS NOT NULL AND numero_fatura != '' THEN valor_total ELSE 0 END), 0) as numero_fatura_valor,
                    
                    -- Primeiro envio
                    COUNT(CASE WHEN primeiro_envio IS NOT NULL THEN 1 END) as primeiro_envio_count,
                    
                    -- Tempo médio cobrança
                    AVG(CASE WHEN data_baixa IS NOT NULL AND primeiro_envio IS NOT NULL 
                            THEN (data_baixa - primeiro_envio) 
                            ELSE NULL END) as tempo_medio_dias
                    
                FROM dashboard_baker 
                WHERE data_emissao >= :data_limite
                AND valor_total > 0
            """)
            
            result = connection.execute(sql_principal, {"data_limite": data_limite}).fetchone()
            
            # Top 5 clientes
            sql_clientes = text("""
                SELECT 
                    destinatario_nome,
                    COUNT(*) as qtd_ctes,
                    COALESCE(SUM(valor_total), 0) as receita_cliente
                FROM dashboard_baker 
                WHERE data_emissao >= :data_limite
                AND destinatario_nome IS NOT NULL 
                AND destinatario_nome != ''
                AND valor_total > 0
                GROUP BY destinatario_nome
                ORDER BY receita_cliente DESC
                LIMIT 5
            """)
            
            clientes_result = connection.execute(sql_clientes, {"data_limite": data_limite}).fetchall()
        
        # Processar resultados
        receita_total = float(result.receita_total or 0)
        total_ctes = int(result.total_ctes or 0)
        
        # Determinar receita faturada (usar envio_final, se não tiver usar data_baixa)
        if result.envio_final_count > 0:
            receita_faturada = float(result.envio_final_valor)
            ctes_faturados = int(result.envio_final_count)
            metodo_faturada = "envio_final"
        else:
            receita_faturada = float(result.valor_baixas_data_baixa)
            ctes_faturados = int(result.baixas_data_baixa)
            metodo_faturada = "data_baixa (fallback)"
        
        # Determinar receita com faturas (usar data_inclusao_fatura, se não tiver usar numero_fatura)
        if result.inclusao_count > 0:
            receita_com_faturas = float(result.inclusao_valor)
            ctes_com_faturas = int(result.inclusao_count)
            metodo_faturas = "data_inclusao_fatura"
        else:
            receita_com_faturas = float(result.numero_fatura_valor)
            ctes_com_faturas = int(result.numero_fatura_count)
            metodo_faturas = "numero_fatura (fallback)"
        
        # Calcular percentuais
        taxa_faturamento = (receita_faturada / receita_total * 100) if receita_total > 0 else 0
        taxa_com_faturas = (receita_com_faturas / receita_total * 100) if receita_total > 0 else 0
        taxa_baixas = (float(result.valor_baixas_data_baixa) / receita_total * 100) if receita_total > 0 else 0
        
        # Processar clientes
        top_clientes = []
        concentracao_top5 = 0
        
        if clientes_result:
            for i, row in enumerate(clientes_result, 1):
                receita_cliente = float(row.receita_cliente)
                percentual = (receita_cliente / receita_total * 100) if receita_total > 0 else 0
                
                top_clientes.append({
                    'posicao': i,
                    'nome': row.destinatario_nome,
                    'receita': receita_cliente,
                    'percentual': percentual,
                    'qtd_ctes': int(row.qtd_ctes)
                })
                
                if i <= 5:
                    concentracao_top5 += percentual
        
        # Tempo médio cobrança
        tempo_medio_cobranca = float(result.tempo_medio_dias or 0)
        
        # Impacto top cliente
        impacto_top_cliente = top_clientes[0]['percentual'] if top_clientes else 0
        
        return jsonify({
            'success': True,
            'debug_info': {
                'total_registros_encontrados': total_ctes,
                'metodo_receita_faturada': metodo_faturada,
                'metodo_receita_faturas': metodo_faturas,
                'periodo_analisado': f"Últimos {filtro_dias} dias"
            },
            'metricas_basicas': {
                'receita_mes_atual': receita_total,
                'total_ctes': total_ctes,
                'ticket_medio': float(result.ticket_medio or 0),
                'ctes_com_baixa': int(result.baixas_data_baixa),
                'valor_baixado': float(result.valor_baixas_data_baixa),
                'percentual_baixado': taxa_baixas
            },
            'receita_faturada': {
                'receita_total': receita_faturada,
                'quantidade_ctes': ctes_faturados,
                'percentual_total': taxa_faturamento,
                'metodo_usado': metodo_faturada
            },
            'receita_com_faturas': {
                'receita_total': receita_com_faturas,
                'quantidade_ctes': ctes_com_faturas,
                'percentual_cobertura': taxa_com_faturas,
                'metodo_usado': metodo_faturas
            },
            'status_sistema': {
                'total_registros': total_ctes,
                'taxa_faturamento': taxa_faturamento,
                'taxa_com_faturas': taxa_com_faturas,
                'tempo_medio_cobranca': tempo_medio_cobranca,
                'concentracao_top5': concentracao_top5,
                'impacto_top_cliente': impacto_top_cliente
            },
            'top_clientes': top_clientes
        })
        
    except Exception as e:
        logger.error(f"Erro nas métricas forçadas: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/graficos-simples')
@login_required
def api_graficos_simples():
    """API para gráficos com dados simplificados"""
    try:
        filtro_dias = int(request.args.get('filtro_dias', 180))
        
        with db.engine.connect() as connection:
            data_limite = datetime.now().date() - timedelta(days=filtro_dias)
            
            # 1. Receita mensal simples
            sql_mensal = text("""
                SELECT 
                    TO_CHAR(data_emissao, 'YYYY-MM') as mes,
                    COALESCE(SUM(valor_total), 0) as receita,
                    COUNT(*) as quantidade
                FROM dashboard_baker 
                WHERE data_emissao >= :data_limite
                AND valor_total > 0
                GROUP BY TO_CHAR(data_emissao, 'YYYY-MM')
                ORDER BY mes
            """)
            
            mensal_result = connection.execute(sql_mensal, {"data_limite": data_limite}).fetchall()
            
            # 2. Top clientes para concentração
            sql_concentracao = text("""
                SELECT 
                    COALESCE(destinatario_nome, 'Cliente não identificado') as cliente,
                    COALESCE(SUM(valor_total), 0) as receita
                FROM dashboard_baker 
                WHERE data_emissao >= :data_limite
                AND valor_total > 0
                GROUP BY destinatario_nome
                ORDER BY receita DESC
                LIMIT 5
            """)
            
            concentracao_result = connection.execute(sql_concentracao, {"data_limite": data_limite}).fetchall()
            
            # 3. Tempo cobrança simplificado
            sql_tempo = text("""
                SELECT 
                    CASE 
                        WHEN (data_baixa - data_emissao) <= 30 THEN '0-30 dias'
                        WHEN (data_baixa - data_emissao) <= 60 THEN '31-60 dias'
                        WHEN (data_baixa - data_emissao) <= 90 THEN '61-90 dias'
                        ELSE '90+ dias'
                    END as faixa,
                    COUNT(*) as quantidade
                FROM dashboard_baker 
                WHERE data_emissao >= :data_limite
                AND data_baixa IS NOT NULL
                AND data_emissao IS NOT NULL
                GROUP BY 
                    CASE 
                        WHEN (data_baixa - data_emissao) <= 30 THEN '0-30 dias'
                        WHEN (data_baixa - data_emissao) <= 60 THEN '31-60 dias'
                        WHEN (data_baixa - data_emissao) <= 90 THEN '61-90 dias'
                        ELSE '90+ dias'
                    END
            """)
            
            tempo_result = connection.execute(sql_tempo, {"data_limite": data_limite}).fetchall()
        
        # Processar dados mensais
        labels_mensal = []
        valores_mensal = []
        quantidade_mensal = []
        
        meses_nomes = {
            '01': 'Jan', '02': 'Fev', '03': 'Mar', '04': 'Abr',
            '05': 'Mai', '06': 'Jun', '07': 'Jul', '08': 'Ago', 
            '09': 'Set', '10': 'Out', '11': 'Nov', '12': 'Dez'
        }
        
        for row in mensal_result:
            if row.mes:
                ano, mes = row.mes.split('-')
                label = f"{meses_nomes.get(mes, mes)}/{ano}"
                labels_mensal.append(label)
                valores_mensal.append(float(row.receita))
                quantidade_mensal.append(int(row.quantidade))
        
        # Se não tem dados mensais, criar dados de exemplo
        if not labels_mensal:
            hoje = datetime.now()
            for i in range(6):
                data_exemplo = hoje - timedelta(days=30*i)
                mes_nome = meses_nomes[f"{data_exemplo.month:02d}"]
                labels_mensal.insert(0, f"{mes_nome}/{data_exemplo.year}")
                valores_mensal.insert(0, 0)
                quantidade_mensal.insert(0, 0)
        
        # Processar concentração
        labels_concentracao = []
        valores_concentracao = []
        
        for row in concentracao_result:
            labels_concentracao.append(row.cliente[:30])  # Limitar nome
            valores_concentracao.append(float(row.receita))
        
        # Se não tem dados de concentração, criar dados de exemplo
        if not labels_concentracao:
            labels_concentracao = ['Aguardando dados']
            valores_concentracao = [1]
        
        # Processar tempo cobrança
        labels_tempo = []
        valores_tempo = []
        
        for row in tempo_result:
            labels_tempo.append(row.faixa)
            valores_tempo.append(int(row.quantidade))
        
        # Se não tem dados de tempo, criar dados de exemplo
        if not labels_tempo:
            labels_tempo = ['0-30 dias', '31-60 dias', '61-90 dias', '90+ dias']
            valores_tempo = [0, 0, 0, 0]
        
        return jsonify({
            'success': True,
            'graficos': {
                'receita_mensal': {
                    'labels': labels_mensal,
                    'valores': valores_mensal,
                    'quantidades': quantidade_mensal
                },
                'concentracao_clientes': {
                    'labels': labels_concentracao,
                    'valores': valores_concentracao
                },
                'tempo_cobranca': {
                    'labels': labels_tempo,
                    'valores': valores_tempo
                },
                'tendencia_linear': {
                    'labels': labels_mensal,
                    'valores_reais': valores_mensal,
                    'valores_tendencia': valores_mensal  # Simplificado
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Erro nos gráficos simples: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500