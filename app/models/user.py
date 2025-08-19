from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    """Modelo de usuário compatível com estrutura Supabase"""
    __tablename__ = 'users'
    
    # Campos principais
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Campos customizados (existem na tabela)
    nome_completo = db.Column(db.String(200))
    tipo_usuario = db.Column(db.String(20), default='user')
    ativo = db.Column(db.Boolean, default=True)
    ultimo_login = db.Column(db.DateTime)
    total_logins = db.Column(db.Integer, default=0)
    
    # Campo que existe (sem updated_at que causa problema)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Define senha com hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica senha"""
        return check_password_hash(self.password_hash, password)
    
    def registrar_login(self):
        """Registra login do usuário"""
        self.ultimo_login = datetime.utcnow()
        self.total_logins = (self.total_logins or 0) + 1
        # Não usar db.session.commit() aqui para evitar conflitos
        db.session.flush()
    
    def reset_security_flags(self):
        """✅ MÉTODO ADICIONADO - Reset flags de segurança"""
        if hasattr(self, 'failed_login_attempts'):
            self.failed_login_attempts = 0
        if hasattr(self, 'locked_until'):
            self.locked_until = None
        db.session.flush()
    
    def is_locked(self):
        """Verifica se a conta está bloqueada"""
        if hasattr(self, 'locked_until') and self.locked_until:
            return datetime.utcnow() < self.locked_until
        return False
    
    
    @property
    def is_admin(self):
        """Verifica se é administrador"""
        return self.tipo_usuario == 'admin'
    
    @property
    def tempo_desde_login(self):
        """Tempo desde último login"""
        if self.ultimo_login:
            delta = datetime.utcnow() - self.ultimo_login
            return delta.days
        return None
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nome_completo': self.nome_completo or '',
            'tipo_usuario': self.tipo_usuario or 'user',
            'ativo': self.ativo if self.ativo is not None else True,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'ultimo_login': self.ultimo_login.isoformat() if self.ultimo_login else None,
            'total_logins': self.total_logins or 0
        }
    
    @staticmethod
    def buscar_por_username(username):
        """Busca usuário por username"""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def buscar_por_email(email):
        """Busca usuário por email"""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def criar_usuario(username, email, password, nome_completo='', tipo_usuario='user'):
        """Cria novo usuário"""
        if User.buscar_por_username(username):
            return False, "Usuário já existe"
        
        if User.buscar_por_email(email):
            return False, "Email já cadastrado"
        
        try:
            user = User(
                username=username,
                email=email,
                nome_completo=nome_completo,
                tipo_usuario=tipo_usuario,
                ativo=True,
                total_logins=0
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            return True, "Usuário criado com sucesso"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Erro ao criar usuário: {str(e)}"
        # ARQUIVO: app/models/user.py
# Adicionar/Melhorar métodos no modelo User existente

# Adicionar no final da classe User:

    @property
    def is_admin(self):
        """Verifica se o usuário é administrador"""
        return self.tipo_usuario == 'admin'
    
    @property
    def is_moderator(self):
        """Verifica se o usuário é moderador"""
        return self.tipo_usuario in ['admin', 'moderator']
    
    @property
    def role_label(self):
        """Retorna o label do tipo de usuário"""
        roles = {
            'admin': 'Administrador',
            'moderator': 'Moderador', 
            'user': 'Usuário'
        }
        return roles.get(self.tipo_usuario, 'Usuário')
    
    @property
    def avatar_letter(self):
        """Retorna a primeira letra para avatar"""
        nome = self.nome_completo or self.username
        return nome[0].upper() if nome else 'U'
    
    @property
    def tempo_desde_login(self):
        """Calcula tempo desde o último login"""
        if not self.ultimo_login:
            return "Primeiro acesso"
        
        from datetime import datetime
        delta = datetime.utcnow() - self.ultimo_login
        
        if delta.days > 0:
            return f"{delta.days} dia{'s' if delta.days > 1 else ''} atrás"
        elif delta.seconds > 3600:
            horas = delta.seconds // 3600
            return f"{horas} hora{'s' if horas > 1 else ''} atrás"
        else:
            minutos = delta.seconds // 60 or 1
            return f"{minutos} minuto{'s' if minutos > 1 else ''} atrás"
    
    @property
    def dias_na_plataforma(self):
        """Calcula quantos dias o usuário está na plataforma"""
        if not self.created_at:
            return 0
        from datetime import datetime
        delta = datetime.utcnow() - self.created_at
        return delta.days
    
    @property
    def last_login_formatted(self):
        """Retorna último login formatado"""
        if not self.ultimo_login:
            return "Nunca"
        return self.ultimo_login.strftime('%d/%m/%Y %H:%M')
    
    def to_dict(self):
        """Converte o usuário para dicionário"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nome_completo': self.nome_completo,
            'tipo_usuario': self.tipo_usuario,
            'ativo': self.ativo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'ultimo_login': self.ultimo_login.isoformat() if self.ultimo_login else None,
            'total_logins': self.total_logins or 0,
            'role_label': self.role_label,
            'avatar_letter': self.avatar_letter,
            'tempo_desde_login': self.tempo_desde_login,
            'dias_na_plataforma': self.dias_na_plataforma,
            'last_login_formatted': self.last_login_formatted,
            'is_admin': self.is_admin,
            'is_moderator': self.is_moderator
        }
    
    def registrar_atividade(self, acao, detalhes=None):
        """Registra uma atividade do usuário (para futuras implementações)"""
        try:
            # Placeholder para logging de atividades
            # Pode ser implementado com uma tabela de logs futuramente
            import logging
            logging.info(f"Usuário {self.username} - {acao}: {detalhes}")
        except Exception:
            pass
    
    def atualizar_ultimo_login(self):
        """Atualiza estatísticas de login"""
        from datetime import datetime
        self.ultimo_login = datetime.utcnow()
        self.total_logins = (self.total_logins or 0) + 1
        
        # Registrar atividade
        self.registrar_atividade('Login realizado')
    
    def pode_acessar_admin(self):
        """Verifica se o usuário pode acessar área administrativa"""
        return self.ativo and self.is_admin
    
    def resetar_senha_temporaria(self):
        """Gera uma senha temporária (para reset de senha)"""
        import string
        import random
        
        # Gerar senha aleatória de 8 caracteres
        chars = string.ascii_letters + string.digits
        senha_temp = ''.join(random.choice(chars) for _ in range(8))
        
        # Definir nova senha
        self.set_password(senha_temp)
        
        return senha_temp
    
    @staticmethod
    def criar_usuario_admin(username, email, senha):
        """Método utilitário para criar usuário admin"""
        from app import db
        
        admin = User(
            username=username,
            email=email,
            nome_completo='Administrador do Sistema',
            tipo_usuario='admin',
            ativo=True
        )
        admin.set_password(senha)
        
        db.session.add(admin)
        db.session.commit()
        
        return admin