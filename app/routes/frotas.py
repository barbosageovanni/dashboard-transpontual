#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rotas do Sistema de Frotas
app/routes/frotas.py
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.frotas import Veiculo, Motorista, ChecklistModelo, ChecklistItem, Checklist, ChecklistResposta
from app.models.user import User
from datetime import datetime, date

bp = Blueprint('frotas_local', __name__, url_prefix='/frotas')

@bp.route('/')
@login_required
def index():
    """Dashboard principal de frotas"""
    # Estatísticas gerais
    total_veiculos = Veiculo.query.count()
    veiculos_ativos = Veiculo.query.filter_by(ativo=True).count()
    veiculos_manutencao = Veiculo.query.filter_by(em_manutencao=True).count()

    total_motoristas = Motorista.query.count()
    motoristas_ativos = Motorista.query.filter_by(ativo=True).count()

    total_checklists = Checklist.query.count()
    checklists_pendentes = Checklist.query.filter_by(status='aguardando_aprovacao').count()

    stats = {
        'veiculos': {
            'total': total_veiculos,
            'ativos': veiculos_ativos,
            'manutencao': veiculos_manutencao
        },
        'motoristas': {
            'total': total_motoristas,
            'ativos': motoristas_ativos
        },
        'checklists': {
            'total': total_checklists,
            'pendentes': checklists_pendentes
        }
    }

    return render_template('frotas/dashboard.html', stats=stats)

@bp.route('/veiculos')
@login_required
def veiculos():
    """Lista de veículos"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Veiculo.query

    # Filtros
    if request.args.get('status') == 'ativo':
        query = query.filter_by(ativo=True)
    elif request.args.get('status') == 'inativo':
        query = query.filter_by(ativo=False)
    elif request.args.get('status') == 'manutencao':
        query = query.filter_by(em_manutencao=True)

    if request.args.get('search'):
        search = f"%{request.args.get('search')}%"
        query = query.filter(
            db.or_(
                Veiculo.placa.like(search),
                Veiculo.marca.like(search),
                Veiculo.modelo.like(search)
            )
        )

    veiculos_pag = query.order_by(Veiculo.criado_em.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('frotas/veiculos.html', veiculos=veiculos_pag)

@bp.route('/veiculos/novo', methods=['GET', 'POST'])
@login_required
def novo_veiculo():
    """Cadastrar novo veículo"""
    if request.method == 'POST':
        try:
            veiculo = Veiculo(
                placa=request.form['placa'].upper().strip(),
                renavam=request.form.get('renavam', '').strip() or None,
                ano=int(request.form['ano']) if request.form.get('ano') else None,
                marca=request.form.get('marca', '').strip(),
                tipo=request.form.get('tipo', '').strip(),
                modelo=request.form.get('modelo', '').strip(),
                km_atual=int(request.form.get('km_atual', 0) or 0),
                ativo=request.form.get('ativo') == 'on'
            )

            db.session.add(veiculo)
            db.session.commit()

            flash(f'Veículo {veiculo.placa} cadastrado com sucesso!', 'success')
            return redirect(url_for('frotas.veiculos'))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar veículo: {str(e)}', 'error')

    return render_template('frotas/veiculo_form.html', veiculo=None)

@bp.route('/motoristas')
@login_required
def motoristas():
    """Lista de motoristas"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Motorista.query

    # Filtros
    if request.args.get('status') == 'ativo':
        query = query.filter_by(ativo=True)
    elif request.args.get('status') == 'inativo':
        query = query.filter_by(ativo=False)

    if request.args.get('search'):
        search = f"%{request.args.get('search')}%"
        query = query.filter(Motorista.nome.like(search))

    motoristas_pag = query.order_by(Motorista.criado_em.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('frotas/motoristas.html', motoristas=motoristas_pag)

@bp.route('/motoristas/novo', methods=['GET', 'POST'])
@login_required
def novo_motorista():
    """Cadastrar novo motorista"""
    if request.method == 'POST':
        try:
            # Verificar se já existe usuário com o email
            email = request.form.get('email', '').strip()
            user = None

            if email:
                user = User.query.filter_by(email=email).first()
                if not user:
                    # Criar usuário automaticamente
                    success, result = User.criar_usuario(
                        username=email.split('@')[0],
                        email=email,
                        password='motorista123',  # Senha padrão
                        nome_completo=request.form['nome'],
                        tipo_usuario='user'
                    )
                    if success:
                        user = User.buscar_por_email(email)
                    else:
                        flash(f'Erro ao criar usuário: {result}', 'error')
                        return render_template('frotas/motorista_form.html', motorista=None)

            # Processar data de validade da CNH
            validade_cnh = None
            if request.form.get('validade_cnh'):
                try:
                    validade_cnh = datetime.strptime(request.form['validade_cnh'], '%Y-%m-%d').date()
                except ValueError:
                    pass

            motorista = Motorista(
                nome=request.form['nome'].strip(),
                cnh=request.form.get('cnh', '').strip() or None,
                categoria=request.form.get('categoria', '').strip() or None,
                validade_cnh=validade_cnh,
                observacoes=request.form.get('observacoes', '').strip(),
                user_id=user.id if user else None,
                ativo=request.form.get('ativo') == 'on'
            )

            db.session.add(motorista)
            db.session.commit()

            flash(f'Motorista {motorista.nome} cadastrado com sucesso!', 'success')
            return redirect(url_for('frotas.motoristas'))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar motorista: {str(e)}', 'error')

    return render_template('frotas/motorista_form.html', motorista=None)

@bp.route('/checklists')
@login_required
def checklists():
    """Lista de checklists"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Checklist.query.options(
        db.joinedload(Checklist.veiculo),
        db.joinedload(Checklist.motorista),
        db.joinedload(Checklist.modelo)
    )

    # Filtros
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)

    tipo = request.args.get('tipo')
    if tipo:
        query = query.filter_by(tipo=tipo)

    checklists_pag = query.order_by(Checklist.dt_inicio.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('frotas/checklists.html', checklists=checklists_pag)

@bp.route('/checklists/novo')
@login_required
def novo_checklist():
    """Iniciar novo checklist"""
    veiculos = Veiculo.query.filter_by(ativo=True).all()
    motoristas = Motorista.query.filter_by(ativo=True).all()
    modelos = ChecklistModelo.query.filter_by(ativo=True).all()

    return render_template('frotas/checklist_inicio.html',
                         veiculos=veiculos,
                         motoristas=motoristas,
                         modelos=modelos)

# API Routes para integração
@bp.route('/api/veiculos')
@login_required
def api_veiculos():
    """API: Lista de veículos"""
    veiculos = Veiculo.query.filter_by(ativo=True).all()
    return jsonify([v.to_dict() for v in veiculos])

@bp.route('/api/motoristas')
@login_required
def api_motoristas():
    """API: Lista de motoristas"""
    motoristas = Motorista.query.filter_by(ativo=True).all()
    return jsonify([m.to_dict() for m in motoristas])

@bp.route('/api/stats')
@login_required
def api_stats():
    """API: Estatísticas para widgets"""
    return jsonify({
        'veiculos_total': Veiculo.query.count(),
        'veiculos_ativos': Veiculo.query.filter_by(ativo=True).count(),
        'motoristas_total': Motorista.query.count(),
        'motoristas_ativos': Motorista.query.filter_by(ativo=True).count(),
        'checklists_hoje': Checklist.query.filter(
            Checklist.dt_inicio >= date.today()
        ).count(),
        'checklists_pendentes': Checklist.query.filter_by(
            status='aguardando_aprovacao'
        ).count()
    })