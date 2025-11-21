"""
Script to populate source details including bias information.
"""
import sqlite3
import json

# Source details mapping
source_details = [
    {
        "Source_name": "Sudanile",
        "website_url": "https://sudanile.com/",
        "Bias": "Neutral",
        "owner": None,
        "founded_at": None,
        "hq_location": None
    },
    {
        "Source_name": "Dabanga Sudan",
        "website_url": "https://www.dabangasudan.org/ar",
        "Bias": "Oppose-SAF",
        "owner": None,
        "founded_at": None,
        "hq_location": None
    },
    {
        "Source_name": "Radio Tamazuj",
        "website_url": "https://www.radiotamazuj.org/ar",
        "Bias": "Neutral",
        "owner": None,
        "founded_at": None,
        "hq_location": None
    },
    {
        "Source_name": "Al Taghyeer News",
        "website_url": "https://www.altaghyeer.info/ar",
        "Bias": "Oppose-SAF",
        "owner": None,
        "founded_at": None,
        "hq_location": None
    },
    {
        "Source_name": "Suda.news",
        "website_url": "https://suda.news",
        "Bias": "Neutral",
        "owner": None,
        "founded_at": None,
        "hq_location": None
    },
    {
        "Source_name": "Tasamuh News",
        "website_url": "https://tasamuhnews.com",
        "Bias": "Neutral",
        "owner": None,
        "founded_at": None,
        "hq_location": None
    },
    {
        "Source_name": "Sudaninet.net",
        "website_url": "https://www.sudaninet.net",
        "Bias": "Neutral",
        "owner": None,
        "founded_at": None,
        "hq_location": None
    },
    {
        "Source_name": "Alnilin",
        "website_url": "https://www.alnilin.com",
        "Bias": "Neutral",
        "owner": None,
        "founded_at": None,
        "hq_location": None
    },
    {
        "Source_name": "Almashhad.news",
        "website_url": "https://www.almashhad.news",
        "Bias": "Neutral",
        "owner": None,
        "founded_at": None,
        "hq_location": None
    },
    {
        "Source_name": "Kushnews.net",
        "website_url": "https://kushnews.net",
        "Bias": "Neutral",
        "owner": None,
        "founded_at": None,
        "hq_location": None
    },
    {
        "Source_name": "Sudafax.com",
        "website_url": "https://sudafax.com",
        "Bias": "Neutral",
        "owner": None,
        "founded_at": None,
        "hq_location": None
    },
    {
        "Source_name": "Tagpress.net",
        "website_url": "https://www.tagpress.net",
        "Bias": "Neutral",
        "owner": None,
        "founded_at": None,
        "hq_location": None
    },
    {
        "Source_name": "CNN Arabic",
        "website_url": "https://arabic.cnn.com",
        "Bias": "Neutral",
        "owner": "Warner Bros. Discovery",
        "founded_at": "2002",
        "hq_location": "Dubai, UAE"
    },
    {
        "Source_name": "Sudan Tribune",
        "website_url": "https://sudantribune.net",
        "Bias": "Oppose-SAF",
        "owner": None,
        "founded_at": None,
        "hq_location": "Paris, France"
    },
    {
        "Source_name": "Darfur 24",
        "website_url": "https://www.darfur24.com",
        "Bias": "Oppose-SAF",
        "owner": None,
        "founded_at": None,
        "hq_location": None
    },
    {
        "Source_name": "Sudani.news",
        "website_url": "https://www.sudani.news",
        "Bias": "Neutral",
        "owner": None,
        "founded_at": None,
        "hq_location": None
    },
    {
        "Source_name": "Al-Sahafa",
        "website_url": "https://www.alsahafa.net",
        "Bias": "Pro-SAF",
        "owner": None,
        "founded_at": None,
        "hq_location": "Khartoum, Sudan"
    },
    {
        "Source_name": "Al Jazeera Network",
        "website_url": "https://www.aljazeera.net",
        "Bias": "Neutral",
        "owner": "Al Jazeera Media Network",
        "founded_at": "1996",
        "hq_location": "Doha, Qatar"
    },
    {
        "Source_name": "Sky News Arabia",
        "website_url": "https://www.skynewsarabia.com",
        "Bias": "Neutral",
        "owner": "Abu Dhabi Media Investment Corporation",
        "founded_at": "2012",
        "hq_location": "Abu Dhabi, UAE"
    },
    {
        "Source_name": "France 24 Arabic",
        "website_url": "https://www.france24.com",
        "Bias": "Neutral",
        "owner": "France Médias Monde",
        "founded_at": "2006",
        "hq_location": "Paris, France"
    },
    {
        "Source_name": "Euronews Arabic",
        "website_url": "https://arabic.euronews.com",
        "Bias": "Neutral",
        "owner": "Media Globe Networks",
        "founded_at": "2008",
        "hq_location": "Lyon, France"
    },
    {
        "Source_name": "Alalam News Network",
        "website_url": "https://alalam.ir",
        "Bias": "Oppose-SAF",
        "owner": "Islamic Republic of Iran Broadcasting",
        "founded_at": "2003",
        "hq_location": "Tehran, Iran"
    },
    {
        "Source_name": "RT Arabic",
        "website_url": "https://arabic.rt.com",
        "Bias": "Pro-SAF",
        "owner": "TV-Novosti",
        "founded_at": "2007",
        "hq_location": "Moscow, Russia"
    },
    {
        "Source_name": "Alsumaria TV",
        "website_url": "https://www.alsumaria.tv",
        "Bias": "Neutral",
        "owner": None,
        "founded_at": "2004",
        "hq_location": "Baghdad, Iraq"
    },
    {
        "Source_name": "Al-Hiwar TV",
        "website_url": "https://alhiwar.tv",
        "Bias": "Neutral",
        "owner": None,
        "founded_at": None,
        "hq_location": "London, UK"
    },
    {
        "Source_name": "Al-Masry Al-Youm",
        "website_url": "https://www.almasryalyoum.com",
        "Bias": "Neutral",
        "owner": None,
        "founded_at": "2004",
        "hq_location": "Cairo, Egypt"
    },
    {
        "Source_name": "El Khabar",
        "website_url": "https://www.elkhabar.com",
        "Bias": "Neutral",
        "owner": None,
        "founded_at": "1990",
        "hq_location": "Algiers, Algeria"
    }
]

def populate_sources():
    """Populate source details in the database."""
    conn = sqlite3.connect('news_aggregator.db')
    cursor = conn.cursor()
    
    updated_count = 0
    not_found = []
    
    for source in source_details:
        url = source['website_url']
        
        # Check if source exists
        cursor.execute("SELECT id, name FROM sources WHERE url = ?", (url,))
        result = cursor.fetchone()
        
        if result:
            source_id = result[0]
            current_name = result[1]
            
            # Update the source with details
            cursor.execute("""
                UPDATE sources 
                SET name = ?, 
                    bias = ?, 
                    owner = ?, 
                    founded_at = ?, 
                    hq_location = ?
                WHERE id = ?
            """, (
                source['Source_name'],
                source['Bias'],
                source['owner'],
                source['founded_at'],
                source['hq_location'],
                source_id
            ))
            
            updated_count += 1
            print(f"[OK] Updated: {source['Source_name']} (was: {current_name})")
        else:
            not_found.append(url)
            print(f"[!!] Not found: {source['Source_name']} ({url})")
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*50}")
    print(f"Updated {updated_count} sources")
    if not_found:
        print(f"Not found: {len(not_found)} sources")
        for url in not_found:
            print(f"  - {url}")
    print(f"{'='*50}")

if __name__ == "__main__":
    populate_sources()
