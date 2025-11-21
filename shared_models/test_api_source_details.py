"""
Test script to verify the API returns source details correctly
"""
import sys
import os

# Direct import from current directory
from db import get_session
from repositories.cluster_repository import ClusterRepository

def test_cluster_details():
    """Test that cluster details include source bias and other info"""
    with get_session() as session:
        cluster_repo = ClusterRepository(session)
        
        # Get the first cluster
        clusters = cluster_repo.get_recent_clusters(limit=1)
        if not clusters:
            print("No clusters found in database")
            return
        
        cluster_id = clusters[0].id
        cluster = cluster_repo.get_cluster_details(cluster_id)
        
        if cluster and cluster['articles']:
            print(f"Cluster ID: {cluster['id']}")
            print(f"Cluster Title: {cluster['title']}")
            print(f"Number of Articles: {len(cluster['articles'])}")
            print("\nFirst Article Details:")
            article = cluster['articles'][0]
            print(f"  Headline: {article['headline'][:50]}...")
            print(f"  Source Name: {article['source_name']}")
            print(f"  Source URL: {article['source_url']}")
            print(f"  Source Bias: {article.get('source_bias', 'NOT FOUND')}")
            print(f"  Source Owner: {article.get('source_owner', 'NOT FOUND')}")
            print(f"  Source Founded: {article.get('source_founded_at', 'NOT FOUND')}")
            print(f"  Source HQ: {article.get('source_hq_location', 'NOT FOUND')}")
            
            print("\n" + "="*80)
            print("SUCCESS! Source details are being returned from database.")
        else:
            print("No articles found in cluster")

if __name__ == "__main__":
    test_cluster_details()
