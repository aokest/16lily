
import os
import django
import sys

# 设置项目根目录
sys.path.append('/Users/aoke/code test/商机跟进及业绩统计/16lily')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.services.ai_service import AIService

def test_polish():
    service = AIService()
    text = "今天完成了需求评审，准备开始写代码。"
    print(f"Original: {text}")
    try:
        result = service.polish_daily_report(text)
        print(f"Polished: {result}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_polish()
