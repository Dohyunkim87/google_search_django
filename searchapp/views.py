import os
import json
import time
import boto3
from django.shortcuts import render
from .models import OrganicResult
from serpapi import GoogleSearch
from accounts.decorators import login_required

API_KEY = os.environ.get('API_KEY')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION')
BUCKET_NAME = os.environ.get('BUCKET_NAME')

def fetch_results(query, start_year=None, end_year=None, max_results=200):
    params = {
        "engine": "google_scholar",
        "q": query,
        "api_key": API_KEY,
        "num": 100,
    }

    if start_year:
        params["as_ylo"] = start_year
    if end_year:
        params["as_yhi"] = end_year

    results = []
    total_results = 0 # float('inf')

    while total_results < max_results:
        search = GoogleSearch(params)
        try:
            response = search.get_dict()
            print("API response:", response)  # 전체 응답 출력
            new_results = response.get("organic_results", [])
            if not new_results:
                print("No organic results found.")
                break
            results.extend(new_results)
            # total_results = response.get("search_information", {}).get("total_results", 0)
            total_results += len(new_results)
            if total_results >= max_results:
                results = results[:max_results]
                break
            # print(f"Total results: {total_results}")
            params["start"] = total_results + 1
        except Exception as e:
            print("An error occurred while fetching results:", e)
            break
        time.sleep(0.5)
    return results

def summarize_text(text):
    summary = summarizer(text, max_length=130, min_length=20, do_sample=False)
    return summary[0]['summary_text']

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
        print(f"Data successfully written to {temp_file_path}")

        s3.upload_file(temp_file_path, BUCKET_NAME, file_name)
        print(f"File uploaded successfully to s3://{BUCKET_NAME}/{file_name}")
    except Exception as e:
        print(f"An error occurred while uploading to S3: {e}")


def index_view(request):
    results = OrganicResult.objects.all()
    return render(request, 'template/searchapp/index.html', {'results': results})

@login_required
def search_view(request):
    if request.method == 'GET':
        query = request.GET.get('query')
        start_year = request.GET.get('start_year')
        end_year = request.GET.get('end_year')

        if not query:
            return render(request, 'template/searchapp/index.html', {'error': 'Query parameter is required'})

        results = fetch_results(query, start_year, end_year)
        if not results:
            return render(request, 'template/searchapp/index.html', {'error': 'No results found for the given query'})
        for result in results:
            OrganicResult.objects.create(
                title=result.get('title', ''),
                authors=result.get('authors', ''),
                link=result.get('link', ''),
                snippet=result.get('snippet', ''),
                publication_info=result.get('publication_info', {}).get('summary', '')
            )

        upload_to_s3(results, f"{query}_results.json")
        return render(request, 'template/results.html', {'results': results, 'query': query})
    return render(request, 'template/searchapp/index.html', {'error': 'Invalid request method'})