#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelos para Sistema de Gestão de Frotas
app/models/frotas.py
"""

from app import db
from sqlalchemy import text
from datetime import datetime, date
from typing import Dict, List, Optional

class Veiculo(db.Model):
    """Modelo para veículos da frota"""
    __tablename__ = "veiculos"

    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(8), unique=True, index=True, nullable=False)
    renavam = db.Column(db.String(11))
    ano = db.Column(db.Integer)
    marca = db.Column(db.String(100))
    tipo = db.Column(db.String(50))
    modelo = db.Column(db.String(100))
    km_atual = db.Column(db.BigInteger, default=0, nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    em_manutencao = db.Column(db.Boolean, default=False, nullable=False)
    observacoes_manutencao = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamentos
    checklists = db.relationship("Checklist", back_populates="veiculo", lazy='dynamic')

    def __repr__(self):
        return f'<Veiculo {self.placa}>'

    def to_dict(self):
        return {
            'id': self.id,
            'placa': self.placa,
            'renavam': self.renavam,
            'ano': self.ano,
            'marca': self.marca,
            'tipo': self.tipo,
            'modelo': self.modelo,
            'km_atual': self.km_atual,
            'ativo': self.ativo,
            'em_manutencao': self.em_manutencao,
            'observacoes_manutencao': self.observacoes_manutencao,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }

class Motorista(db.Model):
    """Modelo para motoristas"""
    __tablename__ = "motoristas"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    cnh = db.Column(db.String(11))
    categoria = db.Column(db.String(5))
    validade_cnh = db.Column(db.Date)
    observacoes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamentos
    user = db.relationship("User", backref="motorista_profile")
    checklists = db.relationship("Checklist", back_populates="motorista", lazy='dynamic')

    def __repr__(self):
        return f'<Motorista {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'cnh': self.cnh,
            'categoria': self.categoria,
            'validade_cnh': self.validade_cnh.isoformat() if self.validade_cnh else None,
            'observacoes': self.observacoes,
            'user_id': self.user_id,
            'ativo': self.ativo,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'email': self.user.email if self.user else None
        }

class ChecklistModelo(db.Model):
    """Modelo para templates de checklist"""
    __tablename__ = "checklist_modelos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # pre, pos, extra
    versao = db.Column(db.Integer, default=1, nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamentos
    itens = db.relationship("ChecklistItem", back_populates="modelo", lazy='dynamic', cascade="all, delete-orphan")
    checklists = db.relationship("Checklist", back_populates="modelo", lazy='dynamic')

    def __repr__(self):
        return f'<ChecklistModelo {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'tipo': self.tipo,
            'versao': self.versao,
            'ativo': self.ativo,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }

class ChecklistItem(db.Model):
    """Modelo para itens do checklist"""
    __tablename__ = "checklist_itens"

    id = db.Column(db.Integer, primary_key=True)
    modelo_id = db.Column(db.Integer, db.ForeignKey("checklist_modelos.id"), nullable=False)
    ordem = db.Column(db.Integer, nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String(50))
    tipo_resposta = db.Column(db.String(20), default='ok_nok')  # ok_nok, sim_nao, texto
    severidade = db.Column(db.String(10), default='baixa')     # baixa, media, alta
    exige_foto = db.Column(db.Boolean, default=False)
    bloqueia_viagem = db.Column(db.Boolean, default=False)

    # Relacionamentos
    modelo = db.relationship("ChecklistModelo", back_populates="itens")
    respostas = db.relationship("ChecklistResposta", back_populates="item", lazy='dynamic')

    def __repr__(self):
        return f'<ChecklistItem {self.descricao[:50]}>'

    def to_dict(self):
        return {
            'id': self.id,
            'modelo_id': self.modelo_id,
            'ordem': self.ordem,
            'descricao': self.descricao,
            'categoria': self.categoria,
            'tipo_resposta': self.tipo_resposta,
            'severidade': self.severidade,
            'exige_foto': self.exige_foto,
            'bloqueia_viagem': self.bloqueia_viagem
        }

class Checklist(db.Model):
    """Modelo para checklists realizados"""
    __tablename__ = "checklists"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, index=True)
    veiculo_id = db.Column(db.Integer, db.ForeignKey("veiculos.id"), nullable=False)
    motorista_id = db.Column(db.Integer, db.ForeignKey("motoristas.id"), nullable=False)
    modelo_id = db.Column(db.Integer, db.ForeignKey("checklist_modelos.id"), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # pre, pos, extra
    status = db.Column(db.String(30), default='em_andamento')  # em_andamento, finalizado, aprovado, reprovado

    # Dados do checklist
    odometro_ini = db.Column(db.Integer, default=0)
    odometro_fim = db.Column(db.Integer)
    dt_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    dt_fim = db.Column(db.DateTime)
    observacoes_gerais = db.Column(db.Text)

    # Aprovação
    aprovado_por = db.Column(db.String(200))
    dt_aprovacao = db.Column(db.DateTime)
    reprovado_por = db.Column(db.String(200))
    dt_reprovacao = db.Column(db.DateTime)
    motivo_reprovacao = db.Column(db.Text)

    # Relacionamentos
    veiculo = db.relationship("Veiculo", back_populates="checklists")
    motorista = db.relationship("Motorista", back_populates="checklists")
    modelo = db.relationship("ChecklistModelo", back_populates="checklists")
    respostas = db.relationship("ChecklistResposta", back_populates="checklist", lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Checklist {self.codigo or self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'veiculo_id': self.veiculo_id,
            'motorista_id': self.motorista_id,
            'modelo_id': self.modelo_id,
            'tipo': self.tipo,
            'status': self.status,
            'odometro_ini': self.odometro_ini,
            'odometro_fim': self.odometro_fim,
            'dt_inicio': self.dt_inicio.isoformat() if self.dt_inicio else None,
            'dt_fim': self.dt_fim.isoformat() if self.dt_fim else None,
            'observacoes_gerais': self.observacoes_gerais,
            'veiculo': self.veiculo.to_dict() if self.veiculo else None,
            'motorista': self.motorista.to_dict() if self.motorista else None,
            'modelo': self.modelo.to_dict() if self.modelo else None
        }

class ChecklistResposta(db.Model):
    """Modelo para respostas dos itens do checklist"""
    __tablename__ = "checklist_respostas"

    id = db.Column(db.Integer, primary_key=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey("checklists.id"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("checklist_itens.id"), nullable=False)
    valor = db.Column(db.String(100), nullable=False)  # ok, nao_ok, sim, nao, texto livre
    observacao = db.Column(db.Text)
    foto_url = db.Column(db.String(500))
    dt_resposta = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    checklist = db.relationship("Checklist", back_populates="respostas")
    item = db.relationship("ChecklistItem", back_populates="respostas")

    def __repr__(self):
        return f'<ChecklistResposta {self.checklist_id}-{self.item_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'checklist_id': self.checklist_id,
            'item_id': self.item_id,
            'valor': self.valor,
            'observacao': self.observacao,
            'foto_url': self.foto_url,
            'dt_resposta': self.dt_resposta.isoformat() if self.dt_resposta else None
        }