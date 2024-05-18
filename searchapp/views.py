import os
import json
import boto3
from django.shortcuts import render
from .models import OrganicResult
from serpapi import GoogleSearch

API_KEY = os.environ.get('API_KEY')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION')
BUCKET_NAME = os.environ.get('BUCKET_NAME')

def fetch_results(query):
    params = {
        "engine": "google_scholar",
        "q": query,
        "api_key": API_KEY
    }
    search = GoogleSearch(params)
    try:
        response = search.get_dict()
        print("API response:", response)  # 전체 응답 출력
        results = response.get("organic_results", [])
        if not results:
            print("No organic results found.")
    except Exception as e:
        print("An error occurred while fetching results:", e)
        results = []
    return results

def upload_to_s3(data, file_name):
    if not data:
        print("No data to upload.")
        return

    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    temp_file_path = f"/tmp/{file_name}"
    try:
        with open(temp_file_path, 'w') as file:
            json.dump(data, file)

        s3.upload_file(temp_file_path, BUCKET_NAME, file_name)
        print(f"File uploaded successfully to s3://{BUCKET_NAME}/{file_name}")
    except Exception as e:
        print(f"An error occurred while uploading to S3: {e}")


def index_view(request):
    return render(request, 'template/searchapp/index.html')

def search_view(request):
    if request.method == 'GET':
        query = request.GET.get('query')
        if not query:
            return render(request, 'template/searchapp/index.html', {'error': 'Query parameter is required'})

        results = fetch_results(query)
        for result in results:
            OrganicResult.objects.create(
                title=result.get('title'),
                authors=result.get('authors'),
                link=result.get('link'),
                snippet=result.get('snippet'),
                publication_info=result.get('publication_info', {}).get('summary', '')
            )

        upload_to_s3(results, f"{query}_results.json")
        return render(request, 'template/results.html', {'results': results, 'query': query})
    return render(request, 'template/searchapp/index.html', {'error': 'Invalid request method'})