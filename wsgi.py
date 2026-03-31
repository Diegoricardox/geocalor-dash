"""
Ponto de entrada WSGI para deploy no Render.
Importa o server do app.py evitando conflito com o diretório app/
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Importar diretamente do arquivo app.py (não do diretório app/)
import importlib.util
spec = importlib.util.spec_from_file_location("app_module", os.path.join(os.path.dirname(__file__), "app.py"))
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)

server = app_module.server
application = server
