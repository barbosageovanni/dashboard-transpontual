#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migração para adicionar tabelas de frotas
migrate_frotas.py
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório da aplicação ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app, db
from app.models.frotas import Veiculo, Motorista, ChecklistModelo, ChecklistItem, Checklist, ChecklistResposta

def criar_tabelas_frotas():
    """Criar tabelas de frotas no banco existente"""
    app = create_app()

    with app.app_context():
        print("[INFO] Criando tabelas de frotas...")

        try:
            # Criar apenas as tabelas de frotas
            Veiculo.__table__.create(db.engine, checkfirst=True)
            print("[OK] Tabela 'veiculos' criada")

            Motorista.__table__.create(db.engine, checkfirst=True)
            print("[OK] Tabela 'motoristas' criada")

            ChecklistModelo.__table__.create(db.engine, checkfirst=True)
            print("[OK] Tabela 'checklist_modelos' criada")

            ChecklistItem.__table__.create(db.engine, checkfirst=True)
            print("[OK] Tabela 'checklist_itens' criada")

            Checklist.__table__.create(db.engine, checkfirst=True)
            print("[OK] Tabela 'checklists' criada")

            ChecklistResposta.__table__.create(db.engine, checkfirst=True)
            print("[OK] Tabela 'checklist_respostas' criada")

            print("\n[SUCCESS] Todas as tabelas de frotas foram criadas com sucesso!")
            return True

        except Exception as e:
            print(f"[ERROR] Erro ao criar tabelas: {e}")
            return False

def popular_dados_iniciais():
    """Popular dados iniciais de exemplo"""
    app = create_app()

    with app.app_context():
        print("\n[INFO] Populando dados iniciais...")

        try:
            # Verificar se já existem dados
            if ChecklistModelo.query.count() > 0:
                print("[INFO] Dados já existem, pulando...")
                return True

            # Criar modelos de checklist padrão
            modelo_pre = ChecklistModelo(
                nome="Checklist Pré-Viagem Padrão",
                tipo="pre",
                versao=1
            )
            db.session.add(modelo_pre)
            db.session.flush()  # Para obter o ID

            modelo_pos = ChecklistModelo(
                nome="Checklist Pós-Viagem Padrão",
                tipo="pos",
                versao=1
            )
            db.session.add(modelo_pos)
            db.session.flush()

            # Itens do checklist pré-viagem
            itens_pre = [
                ("Pneus (pressão e estado)", "pneus", 1),
                ("Freios (pedal e funcionamento)", "freios", 2),
                ("Luzes (faróis, lanternas, pisca)", "luzes", 3),
                ("Fluidos (óleo, água, freio)", "fluidos", 4),
                ("Documentação do veículo", "documentos", 5),
                ("Equipamentos obrigatórios", "equipamentos", 6),
                ("Limpeza geral", "limpeza", 7),
            ]

            for desc, cat, ordem in itens_pre:
                item = ChecklistItem(
                    modelo_id=modelo_pre.id,
                    ordem=ordem,
                    descricao=desc,
                    categoria=cat,
                    tipo_resposta='ok_nok',
                    severidade='media',
                    exige_foto=False,
                    bloqueia_viagem=True
                )
                db.session.add(item)

            # Itens do checklist pós-viagem
            itens_pos = [
                ("Estado geral do veículo", "geral", 1),
                ("Combustível restante", "combustivel", 2),
                ("Quilometragem final", "km", 3),
                ("Avarias encontradas", "avarias", 4),
                ("Limpeza realizada", "limpeza", 5),
            ]

            for desc, cat, ordem in itens_pos:
                item = ChecklistItem(
                    modelo_id=modelo_pos.id,
                    ordem=ordem,
                    descricao=desc,
                    categoria=cat,
                    tipo_resposta='ok_nok',
                    severidade='baixa',
                    exige_foto=False,
                    bloqueia_viagem=False
                )
                db.session.add(item)

            db.session.commit()
            print("[OK] Dados iniciais criados com sucesso!")
            return True

        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Erro ao popular dados: {e}")
            return False

def main():
    """Função principal"""
    print("Migracao do Sistema de Frotas")
    print("=" * 50)

    # Criar tabelas
    if not criar_tabelas_frotas():
        sys.exit(1)

    # Popular dados iniciais
    if not popular_dados_iniciais():
        print("[WARNING] Dados iniciais não foram criados, mas tabelas estão prontas")

    print("\n[SUCCESS] Migração concluída! O sistema de frotas está pronto para uso.")
    print("\nPróximos passos:")
    print("1. Acesse o dashboard em: http://localhost:5000")
    print("2. Vá em 'Sistema de Frotas' no menu")
    print("3. Cadastre veículos e motoristas")
    print("4. Realize checklists!")

if __name__ == "__main__":
    main()