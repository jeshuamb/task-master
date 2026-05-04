from .default import DefaultConfig

class DevelopmentConfig(DefaultConfig):
    DEBUG = True
    SESSION_COOKIE_SECURE = False  
