# Посібник з використання mcp-gsuite-server для оновлення Google Docs (v4 - BATTLE-TESTED)

Цей документ є стандартною операційною процедурою (SOP) для агента Cursor AI.

## Робочий процес

1.  **Отримай параметри:** Архітектор надасть `DOCUMENT_ID` та `TASK_TYPE`.
2.  **Скопіюй шаблон:** Повністю скопіюй Python-скрипт з розділу "Шаблон Python-скрипта v4".
3.  **Створи та виконай:** Створи тимчасовий файл `temp_gdoc_update.py`, встав у нього шаблон, заміни плейсхолдери, виконай та видали.

---

## 🚨 Важливі примітки (з бойового досвіду)

### ⚠️ **Поширені проблеми та їх вирішення:**

1. **Помилка 'DocsService' object has no attribute 'logger'**
   - Причина: Відсутність logger в DocsService
   - Статус: Виправлено в коді сервера (заміна на print)

2. **Дублікати при повторному запуску**
   - Причина: Повторний запуск без перевірки існування
   - Рішення: Використовуй діагностичний скрипт перед основним

3. **Помилка "Невідома помилка" при великих batch операціях**
   - Причина: Занадто багато операцій одночасно (>5)
   - Рішення: Партійна обробка по 3 операції

4. **Неправильні параметри API**
   - `docs_append_formatted_text` потребує `text_content`, не `content`
   - `docs_batch_update` потребує `requests` як массив

---

## 🔧 Діагностичний шаблон (перед основною роботою)

```python
# Діагностичний скрипт - завжди виконуй перед основним
import asyncio
import httpx

DOCUMENT_ID = "[[DOCUMENT_ID]]"
GSUITE_SERVER_URL = "https://mcp-gsuite-server-778416671000.us-central1.run.app"
EXPECTED_CONTENT = "[[CONTENT_TO_CHECK]]"  # Наприклад, заголовок L2-підсумку

async def main():
    async with httpx.AsyncClient(timeout=90.0) as client:
        # Перевірити стан документа
        response = await client.post(
            f"{GSUITE_SERVER_URL}/invoke-tool",
            json={"tool_name": "docs_get_content", "params": {"document_id": DOCUMENT_ID}}
        )
        content = response.json().get("result", {}).get("content", "")
        
        count = content.count(EXPECTED_CONTENT)
        print(f"🔍 Знайдено {count} копій '{EXPECTED_CONTENT}'")
        print(f"📊 Розмір документа: {len(content)} символів")
        
        # Тест простої операції
        test_response = await client.post(
            f"{GSUITE_SERVER_URL}/invoke-tool",
            json={"tool_name": "docs_batch_update", "params": {
                "document_id": DOCUMENT_ID,
                "requests": [{"replaceAllText": {"containsText": {"text": "test", "matchCase": False}, "replaceText": "test"}}]
            }}
        )
        
        if test_response.status_code == 200:
            print("✅ docs_batch_update працює")
        else:
            print(f"❌ docs_batch_update не працює: {test_response.status_code}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Шаблон Python-скрипта v4 (спрощений і стабільний)

```python
# === ШАБЛОН v4 - BATTLE-TESTED ===
import asyncio
import httpx
import json
from typing import List

# --- Плейсхолдери для заміни ---
DOCUMENT_ID = "[[DOCUMENT_ID]]"
TASK_TYPE = "[[TASK_TYPE]]"  # "APPEND_SUMMARY", "BATCH_TAG_L1_RECORDS"
CONTENT_TO_APPEND = """[[CONTENT_TO_APPEND]]"""
L1_HEADINGS_TO_TAG: List[str] = [[L1_SUMMARY_HEADINGS_TO_TAG]]
TAG_TO_APPLY = "[[TAG_TO_APPLY]]"

# --- Конфігурація ---
GSUITE_SERVER_URL = "https://mcp-gsuite-server-778416671000.us-central1.run.app"
BATCH_SIZE = 3  # Максимум операцій в одній партії

async def main():
    print(f"🚀 Запуск завдання '{TASK_TYPE}' для документа ID: {DOCUMENT_ID[:10]}...")
    async with httpx.AsyncClient(timeout=90.0) as client:
        try:
            if TASK_TYPE == "APPEND_SUMMARY":
                # Крок 1: Додати L2-підсумок
                print("📝 Додавання L2-підсумку...")
                append_response = await client.post(
                    f"{GSUITE_SERVER_URL}/invoke-tool",
                    json={"tool_name": "docs_append_formatted_text", "params": {
                        "document_id": DOCUMENT_ID,
                        "text_content": CONTENT_TO_APPEND
                    }}
                )
                
                if append_response.status_code == 200 and append_response.json().get("result", {}).get("success"):
                    print("✅ L2-підсумок успішно додано")
                else:
                    print(f"❌ Помилка додавання L2-підсумку: {append_response.text}")
                    return
                    
            elif TASK_TYPE == "BATCH_TAG_L1_RECORDS":
                # Крок 2: Тегування L1-записів партіями
                print("🏷️  Додавання тегів до L1-записів...")
                
                for i in range(0, len(L1_HEADINGS_TO_TAG), BATCH_SIZE):
                    batch = L1_HEADINGS_TO_TAG[i:i + BATCH_SIZE]
                    print(f"  Обробка партії {i//BATCH_SIZE + 1}: {batch}")
                    
                    # Створити операції тегування для цієї партії
                    requests = []
                    for heading in batch:
                        requests.append({
                            "replaceAllText": {
                                "containsText": {"text": heading, "matchCase": False},
                                "replaceText": f"{TAG_TO_APPLY} {heading}"
                            }
                        })
                    
                    # Виконати партію операцій
                    batch_response = await client.post(
                        f"{GSUITE_SERVER_URL}/invoke-tool",
                        json={"tool_name": "docs_batch_update", "params": {
                            "document_id": DOCUMENT_ID,
                            "requests": requests
                        }}
                    )
                    
                    if batch_response.status_code == 200:
                        result = batch_response.json()
                        if result.get("result", {}).get("success"):
                            print(f"    ✅ Партія {i//BATCH_SIZE + 1} успішно оброблена")
                        else:
                            print(f"    ❌ Помилка партії {i//BATCH_SIZE + 1}: {result}")
                            return
                    else:
                        print(f"    ❌ HTTP помилка партії {i//BATCH_SIZE + 1}: {batch_response.status_code}")
                        return
                        
                    # Пауза між партіями
                    await asyncio.sleep(1)
            
            elif TASK_TYPE == "FULL_ROLLUP":
                # Комбінований режим: спочатку додати підсумок, потім теги
                print("📝 Крок 1: Додавання L2-підсумку...")
                append_response = await client.post(
                    f"{GSUITE_SERVER_URL}/invoke-tool",
                    json={"tool_name": "docs_append_formatted_text", "params": {
                        "document_id": DOCUMENT_ID,
                        "text_content": CONTENT_TO_APPEND
                    }}
                )
                
                if not (append_response.status_code == 200 and append_response.json().get("result", {}).get("success")):
                    print(f"❌ Помилка додавання L2-підсумку: {append_response.text}")
                    return
                print("✅ L2-підсумок додано")
                
                # Тегування L1-записів
                print("🏷️  Крок 2: Додавання тегів до L1-записів...")
                for i in range(0, len(L1_HEADINGS_TO_TAG), BATCH_SIZE):
                    batch = L1_HEADINGS_TO_TAG[i:i + BATCH_SIZE]
                    print(f"  Обробка партії {i//BATCH_SIZE + 1}: {batch}")
                    
                    requests = []
                    for heading in batch:
                        requests.append({
                            "replaceAllText": {
                                "containsText": {"text": heading, "matchCase": False},
                                "replaceText": f"{TAG_TO_APPLY} {heading}"
                            }
                        })
                    
                    batch_response = await client.post(
                        f"{GSUITE_SERVER_URL}/invoke-tool",
                        json={"tool_name": "docs_batch_update", "params": {
                            "document_id": DOCUMENT_ID,
                            "requests": requests
                        }}
                    )
                    
                    if batch_response.status_code == 200 and batch_response.json().get("result", {}).get("success"):
                        print(f"    ✅ Партія {i//BATCH_SIZE + 1} успішно оброблена")
                    else:
                        print(f"    ❌ Помилка партії {i//BATCH_SIZE + 1}")
                        return
                        
                    await asyncio.sleep(1)
            
            print("✅✅✅ ЗАВДАННЯ УСПІШНО ЗАВЕРШЕНО!")
            
        except Exception as e:
            print(f"❌❌❌ КРИТИЧНА ПОМИЛКА! {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🔄 Стратегія відновлення після помилок

### Якщо виникли дублікати:
1. Використай діагностичний скрипт для підрахунку копій
2. Створи скрипт очищення з `replaceAllText` для видалення зайвих копій
3. Перезапусти основний процес

### Якщо batch операції не працюють:
1. Зменши `BATCH_SIZE` до 2 або 1
2. Додай більше пауз між партіями (`await asyncio.sleep(2)`)
3. Перевір розмір документа - великі документи потребують менших партій

### Якщо API повертає помилки:
1. Спробуй простий тест з діагностичного шаблону
2. Перевір URL сервера та його доступність
3. Перевір формат параметрів API

---

## 📊 Рекомендації з продуктивності

- **Малі документи (<20KB):** BATCH_SIZE = 5
- **Середні документи (20-50KB):** BATCH_SIZE = 3  
- **Великі документи (>50KB):** BATCH_SIZE = 2, збільш паузи

---

## 🎯 Приклади використання

### Приклад 1: Повний Roll-Up
```python
TASK_TYPE = "FULL_ROLLUP"
CONTENT_TO_APPEND = """Підсумок 2-го рівня..."""
L1_HEADINGS_TO_TAG = ["Файл: abc.txt", "Файл: def.txt"]
TAG_TO_APPLY = "[Узагальнено в підсумку: L2-2025-01-01]"
```

### Приклад 2: Тільки тегування
```python
TASK_TYPE = "BATCH_TAG_L1_RECORDS"
L1_HEADINGS_TO_TAG = ["Файл: abc.txt", "Файл: def.txt"]
TAG_TO_APPLY = "[Обробець: Bot-2025]"
```

---

## 📝 Changelog

- **v4 (2025-01-XX):** Додано партійну обробку, діагностику, стратегію відновлення
- **v3:** Використання безпечного insertText (застарілий)
- **v2:** Попередні версії (застарілі)
 