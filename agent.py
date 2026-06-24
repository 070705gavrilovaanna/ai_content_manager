from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from datetime import datetime
import os
import json
from config import config

base_llm = ChatOpenAI(
    base_url='https://openrouter.ai/api/v1',
    api_key=config.OPENROUTER_API_KEY,
    model=config.OPENROUTER_MODEL,
    temperature=config.TEMPERATURE
)


@tool
def generate_ideas(topic: str) -> str:
    '''Генерирует 5 идей для контента'''
    prompt = f"Придумай 5 идей для контента на тему '{topic}'. Идеи должны быть практичными и разного формата. Добавь 5 хештегов. Ответ напиши в виде списка цифрами."
    result = base_llm.invoke(prompt).content
    return f"ИДЕИ ПО ТЕМЕ '{topic.upper()}':\n\n{result}"

@tool
def create_plan(topic: str, days: int = 7) -> str:
    '''Создает контент-план'''
    prompt = f"Создай контент-план на тему '{topic}' на {days} дней. Для каждого дня укажи формат, тему и ключевую мысль. Ответ напиши в виде списка по дням."
    return base_llm.invoke(prompt).content

@tool
def write_article(topic: str, style: str = 'профессиональный') -> str:
    '''Пишет статью и сохраняет в черновики'''
    prompt = f"Напиши экспертную статью на тему '{topic}'. Стиль: {style}. Добавь заголовок, вступление, основную часть, заключение и FAQ."
    result = base_llm.invoke(prompt).content
    
    os.makedirs(config.DRAFTS_DIR, exist_ok=True)
    filename = f"{config.DRAFTS_DIR}/{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(result)
    
    return result + f'\n\nАвтоматически сохранено в черновики: {filename}'

@tool
def write_post(topic: str, platform: str = 'Instagram') -> str:
    '''Пишет пост и сохраняет в черновики'''
    prompt = f"Напиши пост для {platform} на тему '{topic}'. Добавь заголовок, историю, основную мысль и призыв к действию. Добавь хештеги."
    result = base_llm.invoke(prompt).content
    
    os.makedirs(config.DRAFTS_DIR, exist_ok=True)
    filename = f"{config.DRAFTS_DIR}/post_{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(result)
    
    return result + f'\n\nАвтоматически сохранено в черновики: {filename}'

@tool
def save_ideas(topic: str, ideas: str) -> str:
    '''Сохраняет идеи в файл'''
    if os.path.exists(config.IDEAS_FILE):
        with open(config.IDEAS_FILE, 'r', encoding='utf-8') as f:
            all_ideas = json.load(f)
    else:
        all_ideas = {}
    all_ideas[topic] = ideas.split('\n')
    with open(config.IDEAS_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_ideas, f, ensure_ascii=False, indent=2)
    return f"Идеи по теме '{topic}' сохранены"

@tool
def get_saved_ideas(topic: str) -> str:
    '''Получает сохраненные идеи'''
    if not os.path.exists(config.IDEAS_FILE):
        return 'Нет сохраненных идей'
    with open(config.IDEAS_FILE, 'r', encoding='utf-8') as f:
        all_ideas = json.load(f)
    if topic not in all_ideas:
        return f"Нет идей по теме '{topic}'"
    ideas = all_ideas[topic]
    result = f"СОХРАНЕННЫЕ ИДЕИ ПО ТЕМЕ '{topic.upper()}':\n\n"
    for i, idea in enumerate(ideas, 1):
        if idea.strip():
            result += f"{i}. {idea}\n"
    return result

@tool
def add_idea(topic: str, idea: str) -> str:
    '''Добавляет идею вручную'''
    if not os.path.exists(config.IDEAS_FILE):
        all_ideas = {}
    else:
        with open(config.IDEAS_FILE, 'r', encoding='utf-8') as f:
            all_ideas = json.load(f)
    if topic not in all_ideas:
        all_ideas[topic] = []
    all_ideas[topic].append(idea)
    with open(config.IDEAS_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_ideas, f, ensure_ascii=False, indent=2)
    return f"Идея добавлена по теме '{topic}'"

@tool
def list_topics() -> str:
    '''Показывает все темы с идеями'''
    if not os.path.exists(config.IDEAS_FILE):
        return 'Нет сохраненных идей'
    with open(config.IDEAS_FILE, 'r', encoding='utf-8') as f:
        all_ideas = json.load(f)
    if not all_ideas:
        return 'Нет сохраненных идей'
    result = 'ТЕМЫ С ИДЕЯМИ:\n\n'
    for topic, ideas in all_ideas.items():
        result += f"- {topic} ({len(ideas)} идей)\n"
    return result

@tool
def save_local(title: str, content: str, status: str = 'draft') -> str:
    '''Сохраняет контент локально'''
    save_dir = config.PUBLISHED_DIR if status == 'published' else config.DRAFTS_DIR
    os.makedirs(save_dir, exist_ok=True)
    filename = f"{save_dir}/{title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return f"Сохранено локально: {filename}"

@tool
def publish_local(title: str) -> str:
    '''Публикует черновик'''
    for file in os.listdir(config.DRAFTS_DIR):
        if title in file and file.endswith('.md'):
            src = f"{config.DRAFTS_DIR}/{file}"
            dst = f"{config.PUBLISHED_DIR}/{file}"
            with open(src, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(dst, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Опубликовано: {file}"
    return f"Черновик '{title}' не найден"

@tool
def search_local(query: str) -> str:
    '''Ищет контент в локальных файлах'''
    results = []
    for search_dir in [config.DRAFTS_DIR, config.PUBLISHED_DIR]:
        if os.path.exists(search_dir):
            for file in os.listdir(search_dir):
                if file.endswith('.md'):
                    with open(f"{search_dir}/{file}", 'r', encoding='utf-8') as f:
                        content = f.read()
                        if query.lower() in content.lower():
                            results.append(f"Файл: {file}\n{content[:300]}...\n")
    return "\n".join(results[:5]) if results else 'Ничего не найдено'

@tool
def get_stats() -> str:
    '''Показывает статистику'''
    drafts = len([f for f in os.listdir(config.DRAFTS_DIR) if f.endswith('.md')]) if os.path.exists(config.DRAFTS_DIR) else 0
    published = len([f for f in os.listdir(config.PUBLISHED_DIR) if f.endswith('.md')]) if os.path.exists(config.PUBLISHED_DIR) else 0
    ideas_count = 0
    if os.path.exists(config.IDEAS_FILE):
        with open(config.IDEAS_FILE, 'r', encoding='utf-8') as f:
            all_ideas = json.load(f)
            ideas_count = sum(len(ideas) for ideas in all_ideas.values())
    return f"""
## Статистика контента

| Показатель | Значение |
|------------|----------|
| **Черновики** | {drafts} |
| **Опубликовано** | {published} |
| **Всего материалов** | {drafts + published} |
| **Сохранённых идей** | {ideas_count} |
"""

def run_agent(user_input: str, session_id: str = 'default'):
    input_lower = user_input.lower()
    
    if input_lower.startswith('идея '):
        return generate_ideas.invoke({'topic': user_input[5:].strip()})
    
    elif input_lower.startswith('сохранить идеи '):
        topic = user_input[15:].strip()
        ideas = generate_ideas.invoke({'topic': topic})
        save_ideas.invoke({'topic': topic, 'ideas': ideas})
        return f"{ideas}\n\nИдеи сохранены!"
    
    elif input_lower.startswith('мои идеи '):
        return get_saved_ideas.invoke({'topic': user_input[9:].strip()})
    
    elif input_lower.startswith('добавить идею '):
        parts = user_input[13:].split(' ', 1)
        if len(parts) == 2:
            return add_idea.invoke({'topic': parts[0], 'idea': parts[1]})
        return 'Используй: добавить идею [тема] [идея]'
    
    elif input_lower == 'темы':
        return list_topics.invoke({})
    
    elif input_lower.startswith('план '):
        parts = user_input[5:].split()
        if len(parts) >= 2 and parts[-1].isdigit():
            topic = ' '.join(parts[:-1])
            days = int(parts[-1])
            return create_plan.invoke({'topic': topic, 'days': days})
        return create_plan.invoke({'topic': user_input[5:].strip()})
    
    elif input_lower.startswith('статья '):
        return write_article.invoke({'topic': user_input[7:].strip()})
    
    elif input_lower.startswith('пост '):
        return write_post.invoke({'topic': user_input[5:].strip()})
    
    elif input_lower.startswith('сохранить '):
        parts = user_input[10:].split(' ', 1)
        if len(parts) == 2:
            return save_local.invoke({'title': parts[0], 'content': parts[1]})
        return 'Используй: сохранить [название] [текст]'
    
    elif input_lower.startswith('опубликовать '):
        return publish_local.invoke({'title': user_input[13:].strip()})
    
    elif input_lower.startswith('поиск '):
        return search_local.invoke({'query': user_input[6:].strip()})
    
    elif input_lower == 'статистика':
        return get_stats.invoke({})
    
    else:
        prompt = f"Пользователь спросил: '{user_input}'. Ответь как полезный AI-помощник."
        return base_llm.invoke(prompt).content


if __name__ == '__main__':
    print('\nAI Контент-Менеджер')
    print('=' * 40)
    print('Команды: идея, план, статья, пост, статистика, поиск, опубликовать, exit\n')
    while True:
        user_input = input('Вы: ')
        if user_input.lower() in ['exit', 'выход']:
            print('До свидания!')
            break
        response = run_agent(user_input)
        print(f'\nБот: {response}\n')