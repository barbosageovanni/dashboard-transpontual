# Models
from .user import User
from .cte import CTE
from .permissions import UserPermission, UserProfile
from .frotas import Veiculo, Motorista, ChecklistModelo, ChecklistItem, Checklist, ChecklistResposta

__all__ = [
    'User', 'CTE', 'UserPermission', 'UserProfile',
    'Veiculo', 'Motorista', 'ChecklistModelo', 'ChecklistItem', 'Checklist', 'ChecklistResposta'
]
