from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
import uvicorn
from agent import run_agent
import os
import json
from config import config

app=FastAPI(title='AI Контент-менеджер')

templates = Jinja2Templates(directory='templates')

@app.get('/', response_class=HTMLResponse)
async def home(request: Request):
    '''главная страница'''
    return templates.TemplateResponse('index.html', {'request': request})

@app.post('/chat', response_class=HTMLResponse)
async def chat(request: Request, user_input: str = Form(...), session_id: str = Form('default')):
    '''обработка сообщения'''
    response = run_agent(user_input, session_id)
    stats = run_agent('статистика', session_id)
    
    ideas=[]
    if os.path.exists(config.IDEAS_FILE):
        with open(config.IDEAS_FILE, 'r', encoding='utf-8') as f:
            all_ideas = json.load(f)
            for topic, idea_list in all_ideas.items():
                ideas.append({'topic': topic, 'count': len(idea_list)})
    
    return templates.TemplateResponse(
        'index.html',
        {
            'request': request,
            'user_input': user_input,
            'response': response,
            'stats': stats,
            'ideas': ideas,
            'session_id': session_id
        }
    )

@app.get('/stats', response_class=HTMLResponse)
async def stats(request: Request):
    '''страница со статистикой'''
    stats = run_agent('статистика', 'default')
    drafts=[]
    published=[]
    
    if os.path.exists(config.DRAFTS_DIR):
        drafts=[f for f in os.listdir(config.DRAFTS_DIR) if f.endswith('.md')]
    
    if os.path.exists(config.PUBLISHED_DIR):
        published = [f for f in os.listdir(config.PUBLISHED_DIR) if f.endswith('.md')]
    
    return templates.TemplateResponse(
        'stats.html',
        {
            'request': request,
            'stats': stats,
            'drafts': drafts,
            'published': published
        }
    )

@app.get('/ideas', response_class=HTMLResponse)
async def show_ideas(request: Request):
    '''страница с идеями'''
    all_ideas={}
    if os.path.exists(config.IDEAS_FILE):
        with open(config.IDEAS_FILE, 'r', encoding='utf-8') as f:
            all_ideas = json.load(f)
    
    return templates.TemplateResponse(
        'ideas.html',
        {
            'request': request,
            'all_ideas': all_ideas
        }
    )

@app.post('/add_idea')
async def add_idea(request: Request, topic: str = Form(...), idea: str = Form(...)):
    '''добавляет идею вручную'''
    if os.path.exists(config.IDEAS_FILE):
        with open(config.IDEAS_FILE, 'r', encoding='utf-8') as f:
            all_ideas = json.load(f)
    else:
        all_ideas = {}
    
    if topic not in all_ideas:
        all_ideas[topic]=[]
    all_ideas[topic].append(idea)
    
    with open(config.IDEAS_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_ideas, f, ensure_ascii=False, indent=2)
    
    return {'status': 'success', 'message': f"Идея добавлена по теме '{topic}'"}

@app.get('/view_file/{file_type}/{filename}')
async def view_file(file_type: str, filename: str):
    '''просмотр содержимого файла'''
    if file_type=='drafts':
        filepath = f'{config.DRAFTS_DIR}/{filename}'
    elif file_type=='published':
        filepath = f'{config.PUBLISHED_DIR}/{filename}'
    else:
        return {'error': 'Неверный тип'}
    
    if not os.path.exists(filepath):
        return {'error': 'Файл не найден'}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return {'content': content}

@app.post('/publish')
async def publish_file(filename: str = Form(...)):
    '''публикует черновик и перенаправляет на /stats'''
    src = f"{config.DRAFTS_DIR}/{filename}"
    dst = f"{config.PUBLISHED_DIR}/{filename}"
    
    if not os.path.exists(src):
        return {"error": "Файл не найден"}
    
    with open(src, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(content)
        
    return RedirectResponse(url="/stats", status_code=303)


if __name__ == '__main__':
    print('Сервер запущен. Отрыть в браузере http://localhost:8000')
    uvicorn.run(app, host='0.0.0.0', port=8000)
