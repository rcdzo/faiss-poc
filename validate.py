"""
Script de validação: verifica se todos os componentes estão funcionando
"""
import sys
from pathlib import Path

def validate_imports():
    """Valida se todas as importações funcionam"""
    print("Validando importações...")
    
    try:
        import pandas
        print("✓ pandas")
    except ImportError as e:
        print(f"✗ pandas: {e}")
        return False
    
    try:
        import numpy
        print("✓ numpy")
    except ImportError as e:
        print(f"✗ numpy: {e}")
        return False
    
    try:
        import faiss
        print("✓ faiss-cpu")
    except ImportError as e:
        print(f"✗ faiss-cpu: {e}")
        return False
    
    try:
        from sentence_transformers import SentenceTransformer
        print("✓ sentence-transformers")
    except ImportError as e:
        print(f"✗ sentence-transformers: {e}")
        return False
    
    try:
        from unidecode import unidecode
        print("✓ unidecode")
    except ImportError as e:
        print(f"✗ unidecode: {e}")
        return False
    
    try:
        import torch
        print("✓ torch")
    except ImportError as e:
        print(f"✗ torch: {e}")
        return False
    
    try:
        from transformers import AutoModel
        print("✓ transformers")
    except ImportError as e:
        print(f"✗ transformers: {e}")
        return False
    
    return True


def validate_modules():
    """Valida se os módulos do projeto funcionam"""
    print("\nValidando módulos do projeto...")
    
    try:
        from src.embedding_service import EmbeddingService
        print("✓ src.embedding_service")
    except ImportError as e:
        print(f"✗ src.embedding_service: {e}")
        return False
    
    try:
        from src.index_builder import IndexBuilder
        print("✓ src.index_builder")
    except ImportError as e:
        print(f"✗ src.index_builder: {e}")
        return False
    
    try:
        from src.search_engine import SearchEngine
        print("✓ src.search_engine")
    except ImportError as e:
        print(f"✗ src.search_engine: {e}")
        return False
    
    return True


def validate_structure():
    """Valida estrutura de diretórios"""
    print("\nValidando estrutura de diretórios...")
    
    base_path = Path(__file__).parent
    
    required_dirs = [
        'src',
        'notebooks',
        'data',
        'data/indices'
    ]
    
    all_ok = True
    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        if dir_path.exists():
            print(f"✓ {dir_name}/")
        else:
            print(f"✗ {dir_name}/ (não encontrado)")
            all_ok = False
    
    return all_ok


def validate_files():
    """Valida arquivos essenciais"""
    print("\nValidando arquivos essenciais...")
    
    base_path = Path(__file__).parent
    
    required_files = [
        'src/__init__.py',
        'src/embedding_service.py',
        'src/index_builder.py',
        'src/search_engine.py',
        'notebooks/generate_synthetic_dne.ipynb',
        'notebooks/busca_vetorial_poc.ipynb',
        'requirements.txt',
        'config.py',
        'README.md'
    ]
    
    all_ok = True
    for file_name in required_files:
        file_path = base_path / file_name
        if file_path.exists():
            print(f"✓ {file_name}")
        else:
            print(f"✗ {file_name} (não encontrado)")
            all_ok = False
    
    return all_ok


def main():
    print("="*70)
    print("VALIDAÇÃO DA POC - Busca Vetorial DNE")
    print("="*70)
    print()
    
    # Valida importações
    if not validate_imports():
        print("\n❌ Erro nas importações. Execute: pip install -r requirements.txt")
        return False
    
    # Valida módulos do projeto
    if not validate_modules():
        print("\n❌ Erro nos módulos do projeto")
        return False
    
    # Valida estrutura
    if not validate_structure():
        print("\n⚠ Estrutura de diretórios incompleta")
    
    # Valida arquivos
    if not validate_files():
        print("\n⚠ Alguns arquivos estão faltando")
    
    print("\n" + "="*70)
    print("✅ VALIDAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*70)
    print("\nPróximos passos:")
    print("1. Execute: jupyter notebook")
    print("2. Abra: notebooks/generate_synthetic_dne.ipynb")
    print("3. Execute todas as células para gerar o dataset sintético")
    print("4. Abra: notebooks/busca_vetorial_poc.ipynb")
    print("5. Execute todas as células para validar a POC")
    print()
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
