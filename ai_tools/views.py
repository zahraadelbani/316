from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
import logging
import re
import nltk
from nltk.tokenize import sent_tokenize

# Set up logging
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Remove the global model initialization
summarizer = None

def chunk_text(text, max_words=1000):
    """Split text into chunks of approximately max_words words while keeping sentences intact."""
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence_length = len(sentence.split())
        if current_length + sentence_length > max_words and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_length = sentence_length
        else:
            current_chunk.append(sentence)
            current_length += sentence_length
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

@login_required
def ai_tools_page(request):
    return render(request, 'ai_tools/ai_tools.html')

@csrf_exempt
@login_required
def generate_summary(request):
    if request.method == 'POST':
        try:
            global summarizer
            if summarizer is None:
                from transformers import pipeline
                summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            
            data = json.loads(request.body)
            text = data.get('text', '')
            
            if not text.strip():
                return JsonResponse({
                    'success': False,
                    'error': 'Please provide text to summarize'
                })

            # Split text into chunks if it's too long
            chunks = chunk_text(text)
            
            # Generate summary for each chunk
            chunk_summaries = []
            for chunk in chunks:
                summary = summarizer(chunk, max_length=130, min_length=30, do_sample=False)
                chunk_summaries.append(summary[0]['summary_text'])
            
            # If we have multiple chunks, combine their summaries and generate a final summary
            if len(chunk_summaries) > 1:
                combined_summary = ' '.join(chunk_summaries)
                final_summary = summarizer(combined_summary, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
            else:
                final_summary = chunk_summaries[0]
            
            return JsonResponse({
                'success': True,
                'summary': final_summary
            })
        except Exception as e:
            logger.error(f"Error in generate_summary: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
@login_required
def generate_citation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('text', '').strip()
            
            if not query:
                return JsonResponse({
                    'success': False,
                    'error': 'Please provide a search query'
                })
            
            # Query Semantic Scholar API
            try:
                # First search for the paper
                search_url = f'https://api.semanticscholar.org/graph/v1/paper/search'
                search_params = {
                    'query': query,
                    'limit': 1,
                    'fields': 'title,authors,year,venue,url,abstract'
                }
                
                response = requests.get(
                    search_url,
                    params=search_params,
                    timeout=10,
                    headers={
                        'User-Agent': 'ResearchApp/1.0',
                    }
                )
                
                if response.status_code != 200:
                    return JsonResponse({
                        'success': False,
                        'error': f'Search API error (Status {response.status_code}). Please try again later.'
                    })
                
                data = response.json()
                if not data.get('data'):
                    return JsonResponse({
                        'success': False,
                        'error': 'No matching papers found. Try refining your search.'
                    })
                
                paper = data['data'][0]
                
                # Create citation in various formats
                authors = [f"{author.get('name', '')}" for author in paper.get('authors', [])]
                author_text = ' and '.join(authors) if authors else 'Unknown Author'
                
                # Create APA citation
                year = paper.get('year', 'n.d.')
                title = paper.get('title', '')
                venue = paper.get('venue', '')
                url = paper.get('url', '')
                
                apa_citation = f"{author_text} ({year}). {title}."
                if venue:
                    apa_citation += f" {venue}."
                if url:
                    apa_citation += f" Retrieved from {url}"
                
                return JsonResponse({
                    'success': True,
                    'citation': {
                        'apa': apa_citation,
                        'title': title,
                        'authors': author_text,
                        'year': year,
                        'venue': venue,
                        'url': url,
                        'abstract': paper.get('abstract', '')
                    }
                })
                
            except requests.exceptions.RequestException as e:
                logger.error(f"API request error: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to connect to citation service. Please try again later.'
                })
                
        except Exception as e:
            logger.error(f"Unexpected error in generate_citation: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'An unexpected error occurred: {str(e)}'
            })
            
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })
