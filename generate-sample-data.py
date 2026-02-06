"""
Script para gerar dados de exemplo para o laboratório Small Files Problem
Gera arquivos JSON pequenos (~30kb) simulando dados de dispositivos e assinaturas
"""

import json
import os
import random
from datetime import datetime, timedelta
import uuid

def generate_device_record():
    """Gera um registro único de dispositivo"""
    device_types = ['smartphone', 'tablet', 'smartwatch', 'laptop', 'desktop']
    os_types = ['iOS', 'Android', 'Windows', 'MacOS', 'Linux']
    manufacturers = ['Apple', 'Samsung', 'Huawei', 'Xiaomi', 'LG', 'Dell', 'HP', 'Lenovo']
    
    return {
        'device_id': str(uuid.uuid4()),
        'device_type': random.choice(device_types),
        'manufacturer': random.choice(manufacturers),
        'os': random.choice(os_types),
        'os_version': f"{random.randint(8, 15)}.{random.randint(0, 9)}",
        'screen_size': round(random.uniform(4.5, 15.6), 1),
        'ram_gb': random.choice([2, 4, 8, 16, 32, 64]),
        'storage_gb': random.choice([32, 64, 128, 256, 512, 1024]),
        'battery_mah': random.randint(2000, 6000),
        'registration_date': (datetime.now() - timedelta(days=random.randint(0, 730))).isoformat(),
        'last_active': (datetime.now() - timedelta(hours=random.randint(0, 168))).isoformat(),
        'is_active': random.choice([True, True, True, False]),  # 75% ativo
        'location': {
            'country': random.choice(['BR', 'US', 'UK', 'DE', 'JP', 'IN', 'CA', 'AU']),
            'city': random.choice(['São Paulo', 'Rio de Janeiro', 'New York', 'London', 'Tokyo']),
            'timezone': random.choice(['America/Sao_Paulo', 'America/New_York', 'Europe/London', 'Asia/Tokyo'])
        },
        'settings': {
            'notifications_enabled': random.choice([True, False]),
            'dark_mode': random.choice([True, False]),
            'language': random.choice(['pt-BR', 'en-US', 'es-ES', 'de-DE', 'ja-JP'])
        }
    }

def generate_subscription_record():
    """Gera um registro único de assinatura"""
    plans = ['free', 'basic', 'premium', 'enterprise']
    statuses = ['active', 'active', 'active', 'cancelled', 'expired']  # 60% ativo
    payment_methods = ['credit_card', 'debit_card', 'paypal', 'bank_transfer']
    
    plan = random.choice(plans)
    price_map = {'free': 0, 'basic': 9.99, 'premium': 19.99, 'enterprise': 49.99}
    
    return {
        'subscription_id': str(uuid.uuid4()),
        'device_id': str(uuid.uuid4()),  # Simula relação com dispositivo
        'plan': plan,
        'status': random.choice(statuses),
        'price': price_map[plan],
        'currency': random.choice(['USD', 'BRL', 'EUR', 'GBP', 'JPY']),
        'payment_method': random.choice(payment_methods),
        'start_date': (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat(),
        'end_date': (datetime.now() + timedelta(days=random.randint(30, 365))).isoformat() if random.random() > 0.3 else None,
        'auto_renew': random.choice([True, False]),
        'trial_period': random.choice([True, False]) if plan != 'free' else False,
        'billing_cycle': random.choice(['monthly', 'quarterly', 'yearly']) if plan != 'free' else None,
        'features': {
            'storage_gb': {'free': 5, 'basic': 50, 'premium': 200, 'enterprise': 1000}[plan],
            'max_devices': {'free': 1, 'basic': 3, 'premium': 5, 'enterprise': 999}[plan],
            'support_level': {'free': 'community', 'basic': 'email', 'premium': 'priority', 'enterprise': '24/7'}[plan],
            'ads_free': plan in ['premium', 'enterprise']
        },
        'metadata': {
            'referral_code': str(uuid.uuid4())[:8] if random.random() > 0.7 else None,
            'promo_code': f"PROMO{random.randint(1000, 9999)}" if random.random() > 0.8 else None,
            'customer_since_days': random.randint(30, 1000)
        }
    }

def generate_file(file_type, date_str, target_size_kb=30, output_dir='files'):
    """
    Gera um arquivo JSON com múltiplos registros
    
    Args:
        file_type: 'device' ou 'subscription'
        date_str: string de data para o nome do arquivo (ex: '2022_fev_27')
        target_size_kb: tamanho alvo do arquivo em KB
        output_dir: diretório de saída
    """
    
    # Criar diretório se não existir
    os.makedirs(f"{output_dir}/{file_type}", exist_ok=True)
    
    records = []
    current_size = 0
    target_size_bytes = target_size_kb * 1024
    
    # Gerar registros até atingir o tamanho alvo
    generator = generate_device_record if file_type == 'device' else generate_subscription_record
    
    while current_size < target_size_bytes:
        record = generator()
        records.append(record)
        current_size = len(json.dumps(records, indent=2).encode('utf-8'))
    
    # Salvar arquivo
    filename = f"{output_dir}/{file_type}/{file_type}_{date_str}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    
    actual_size_kb = os.path.getsize(filename) / 1024
    print(f"[OK] Gerado: {filename} ({actual_size_kb:.2f} KB, {len(records)} registros)")
    
    return filename, actual_size_kb, len(records)

def generate_sample_dataset(num_files_per_type=10, avg_size_kb=30):
    """
    Gera um dataset completo de exemplo
    
    Args:
        num_files_per_type: número de arquivos a gerar para cada tipo
        avg_size_kb: tamanho médio dos arquivos em KB
    """
    
    print("=" * 60)
    print("Gerando Dataset de Exemplo para Laboratório Small Files")
    print("=" * 60)
    print()
    
    # Gerar datas de exemplo
    base_date = datetime(2022, 2, 27)
    dates = [(base_date + timedelta(days=i)).strftime("%Y_%b_%d").lower() 
             for i in range(num_files_per_type)]
    
    total_files = 0
    total_size_kb = 0
    total_records = 0
    
    # Gerar arquivos de device
    print(f"Gerando {num_files_per_type} arquivos de DEVICE...")
    for date in dates:
        _, size, records = generate_file('device', date, target_size_kb=avg_size_kb)
        total_files += 1
        total_size_kb += size
        total_records += records
    
    print()
    
    # Gerar arquivos de subscription
    print(f"Gerando {num_files_per_type} arquivos de SUBSCRIPTION...")
    for date in dates:
        _, size, records = generate_file('subscription', date, target_size_kb=avg_size_kb)
        total_files += 1
        total_size_kb += size
        total_records += records
    
    print()
    print("=" * 60)
    print("Resumo da Geração")
    print("=" * 60)
    print(f"Total de arquivos gerados: {total_files}")
    print(f"Total de registros: {total_records:,}")
    print(f"Tamanho total: {total_size_kb:.2f} KB ({total_size_kb/1024:.2f} MB)")
    print(f"Tamanho médio por arquivo: {total_size_kb/total_files:.2f} KB")
    print(f"Registros médios por arquivo: {total_records//total_files}")
    print()
    print("[OK] Dataset gerado com sucesso!")
    print()
    print("Próximos passos:")
    print("1. Execute o script: python small-files-problem.py")
    print("2. Observe as métricas de performance")
    print("3. Experimente diferentes configurações")
    print("=" * 60)

def create_gitkeep_files():
    """Cria arquivos .gitkeep para manter estrutura de pastas no git"""
    os.makedirs("files/device", exist_ok=True)
    os.makedirs("files/subscription", exist_ok=True)
    
    with open("files/device/.gitkeep", 'w') as f:
        f.write("")
    
    with open("files/subscription/.gitkeep", 'w') as f:
        f.write("")

if __name__ == '__main__':
    # Criar estrutura de pastas
    create_gitkeep_files()
    
    # Configurações
    NUM_FILES = 100  # Número de arquivos por tipo (device e subscription)
    AVG_SIZE_KB = 30  # Tamanho médio desejado em KB
    
    # Gerar dataset
    generate_sample_dataset(num_files_per_type=NUM_FILES, avg_size_kb=AVG_SIZE_KB)
    
    # Instruções adicionais
    print("\nDica: Para gerar mais arquivos, modifique as variáveis NUM_FILES e AVG_SIZE_KB")
    print("   Exemplo: NUM_FILES = 100 para simular cenário com mais small files")
