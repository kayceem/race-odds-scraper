import os
import csv
import time
import httpx
import random
import asyncio
from dataclasses import dataclass, asdict
from playwright.async_api import async_playwright
from utils import convert_to_aest, get_headers, get_random_user_agent, get_today_str, setup_logger

@dataclass
class RaceDataRow:
    HorseName: str
    HorseNum: int
    Barrier: int
    JockeyName: str
    JockeyWeight: str
    RaceTrack: str
    RaceNum: int
    Distance: str
    TrackCond: str
    ClassInfo: str
    Prize: str
    Weather: str
    RaceTime: str
    BestOdds: float
    OddsSource: str

class URLs:
    BASE_URL = "https://www.odds.com.au/horse-racing/"
    EVENT_INFO_URL = "https://www.odds.com.au/api/web/public/Event/getEventHeaderCacheable/"
    EVENTS_URL = "https://www.odds.com.au/api/web/public/Meetings/getDataByRangeCacheable/"
    ODDS_URL = "https://www.punters.com.au/api/web/public/Odds/getOddsComparisonCacheable/"

logger = setup_logger("odds_scraper")

async def fetch_events():
    au_nz_events, api_key = [], None
    try:
        logger.info("Fetching events from odds.com.au")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()

            page = await context.new_page()
            await page.set_extra_http_headers({
                "User-Agent": get_random_user_agent(),
                "Accept-Language": "en-US,en;q=0.9",
            })
            async def on_response(response):
                nonlocal au_nz_events, api_key
                if response.url.startswith(URLs.EVENTS_URL) and response.status == 200:
                    try:
                        api_key = response.url.split("APIKey=")[-1].split("&")[0]
                        json_data = await response.json()
                        events = json_data.get('events', [])
                        au_nz_events = [r for r in events if r.get('regionName', None) == 'Australia' or r.get('regionName', None) == '1']
                    except Exception as e:
                        print(f"Error handling counties response: {e}")
                        
            page.on("response", on_response)
            await page.goto(URLs.BASE_URL, timeout=60000)
            await page.wait_for_selector("div.racing-meeting-rows__main", timeout=60000)
            await page.wait_for_timeout(2000)
            logger.info("Events fetched successfully")
    except Exception as e:
            logger.error(f"Error fetching events: {e}")
    return au_nz_events, api_key

async def fetch_race_odds(event, api_key):
    try:
        rows = []
        event_url = event.get('url', '')
        event_id = event.get('id', '')
        if not event_url or not event_id:
            return
        logger.info(f"Fetching odds for event: {event.get('name', '')}")
        params = {
            "allowGet": "true",
            "APIKey": api_key,
            "eventId": event_id,
        }
        race_headers = get_headers("race")
        event_headers = get_headers("event")

        async with httpx.AsyncClient(http2=True, headers=race_headers, timeout=30) as client:
            response = await client.get(URLs.ODDS_URL, params={**params, "betType": "FixedWin"})
            response.raise_for_status()
            race_data = response.json()

        async with httpx.AsyncClient(http2=True, headers=event_headers, timeout=30) as client:
            response = await client.get(URLs.EVENT_INFO_URL, params=params)
            response.raise_for_status()
            event_data = response.json()

        race_track = event_data.get('venueName', '')
        race_num = race_data.get('eventName', '').split(" ")[-1] if race_data.get('eventName', '') else ''
        distance = event_data.get('distance', '')
        track_cond = event_data.get('distanceTrackCondition', '').split(", ")[-1] if event_data.get('distanceTrackCondition', '') else ''
        class_info = event_data.get('groupType', '')
        prize = event_data.get('prizeMoney', '')
        weather = event_data.get('weather', '')
        race_time = convert_to_aest(race_data.get('startTime', ''))

        for participant in race_data.get('selections', []):
            try:
                horse_name = participant.get('name', '')
                horse_num = participant.get('competitorNumber', 0)
                barrier = participant.get('barrierNumber', 0)
                jockey_name = participant.get('jockeyName', '')
                jockey_weight = participant.get('weight', '')

                best_odds_obj = max(
                    filter(
                        lambda x: (
                            not (x.get("bookmakerLower") == "betfair" and x.get("exchangeSuffix") == "_lay")
                            and x.get("odds") is not None
                        ),
                        participant.get("prices", [])
                    ),
                    key=lambda x: x.get("odds"),
                    default=None
                )
                best_odds = best_odds_obj.get("odds", 0.0) if best_odds_obj else 0.0
                odds_source = best_odds_obj.get("bookmaker", "") if best_odds_obj else ""

                rows.append(
                    RaceDataRow(
                        HorseName = horse_name,
                        HorseNum = horse_num,
                        Barrier = barrier,
                        JockeyName = jockey_name,
                        JockeyWeight = jockey_weight,
                        RaceTrack = race_track,
                        RaceNum = race_num,
                        Distance = distance,
                        TrackCond = track_cond,
                        ClassInfo = class_info,
                        Prize = prize,
                        Weather = weather,
                        RaceTime = race_time,
                        BestOdds = best_odds,
                        OddsSource = odds_source
                    )
                )
            except Exception as e:
                logger.error(f"Error processing participant {participant.get('name', '')}: {e}")
                continue
        return rows
    except Exception as e:
        logger.error(f"Error fetching odds for event {event.get('name', '')}: {e}")
        return None
        
def save_to_csv(rows, output_dir):
    output_path = f"{output_dir}/{get_today_str()}.csv"
    try:
        if not rows:
            return
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].__dataclass_fields__.keys())
            writer.writeheader()
            writer.writerows([asdict(row) for row in rows])
    except Exception as e:
        logger.error(f"Error saving to CSV: {e}")
        return None    

async def scrape():
    try:
        output_dir = os.getenv("OUTPUT_DIR", "odds_csv")
        os.makedirs(output_dir, exist_ok=True)

        events, api_key = await fetch_events()
        if not events or not api_key:
            return
        rows = []
        for event in events:
            event_rows = await fetch_race_odds(event, api_key)
            if not event_rows:
                continue
            rows.extend(event_rows)
            save_to_csv(rows, output_dir)
            time.sleep(random.uniform(1, 5))
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        return

                    
async def main():
    logger.info("Starting odds scraper")
    await scrape()
    logger.info("Scraping completed")

if __name__ == "__main__":
    asyncio.run(main())
