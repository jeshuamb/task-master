from .dev import DevelopmentConfig
from .prod import ProductionConfig
from .default import DefaultConfig

config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DefaultConfig
}
