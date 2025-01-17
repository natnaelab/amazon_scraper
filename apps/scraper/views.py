from django.shortcuts import render, redirect
from django.http import JsonResponse
from celery.result import AsyncResult
from .tasks import start_amazon_scraping

def index(request):
    return render(request, 'scraper/index.html')

def start_scraping(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        max_pages = int(request.POST.get('max_pages', 3))
        
        if query:
            task = start_amazon_scraping.delay(query, max_pages)
            return render(request, 'scraper/index.html', {
                'task_id': task.id,
                'message': f'Started scraping for query: {query}'
            })
        else:
            return render(request, 'scraper/index.html', {
                'error': True,
                'message': 'Please provide a search query'
            })
    
    return redirect('index')

def task_status(request, task_id):
    task_result = AsyncResult(task_id)
    return JsonResponse({
        'status': task_result.status,
        'result': task_result.result if task_result.successful() else None
    })
