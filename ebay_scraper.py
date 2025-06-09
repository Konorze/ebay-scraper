import aiohttp
import asyncio
import argparse
import sys
import random
import time
from bs4 import BeautifulSoup
import itertools

def banner():
    print("eBay Scraper v1.3")
    print("")
    print("github.com/Konorze\n")

def get_price(text):
    if not text:
        return None
    text = text.replace(',', '').replace('$', '').replace('£', '').replace('€', '').strip()
    if 'to' in text:
        text = text.split('to')[0].strip()
    if 'from' in text:
        text = text.split('from')[1].strip()
    try:
        return float(text)
    except:
        return None

def load_proxies():
    try:
        with open("proxies.txt", "r") as f:
            prx = []
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if ':' in line:
                        prx.append(line)
            return prx
    except:
        return []

def get_ua():
    uas = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
    ]
    return {
        "User-Agent": random.choice(uas),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive"
    }

async def spin():
    chars = ['|', '/', '-', '\\']
    while True:
        for c in chars:
            sys.stdout.write('\rscanning... ' + c)
            sys.stdout.flush()
            await asyncio.sleep(0.2)

async def check_prx(prx):
    try:
        conn = aiohttp.TCPConnector(ssl=False, limit=10)
        timeout = aiohttp.ClientTimeout(total=3)
        async with aiohttp.ClientSession(connector=conn, timeout=timeout) as session:
            async with session.get("https://httpbin.org/ip", proxy=f"http://{prx}", ssl=False) as resp:
                return resp.status == 200
    except:
        return False

async def fetch_page(url, headers, prx_list=None, force_prx=False):
    if force_prx and not prx_list:
        return None
    
    if prx_list:
        random.shuffle(prx_list)
        for prx in prx_list[:]:
            try:
                conn = aiohttp.TCPConnector(ssl=False, limit=10)
                timeout = aiohttp.ClientTimeout(total=20)
                async with aiohttp.ClientSession(connector=conn, timeout=timeout, headers=headers) as session:
                    async with session.get(url, proxy=f"http://{prx}", ssl=False) as resp:
                        if resp.status == 200:
                            return await resp.text()
                        elif resp.status in [403, 429]:
                            prx_list.remove(prx)
                            continue
            except:
                try:
                    prx_list.remove(prx)
                except:
                    pass
                continue
    
    if not force_prx:
        try:
            conn = aiohttp.TCPConnector(ssl=False, limit=10)
            timeout = aiohttp.ClientTimeout(total=20)
            async with aiohttp.ClientSession(connector=conn, timeout=timeout, headers=headers) as session:
                async with session.get(url, ssl=False) as resp:
                    if resp.status == 200:
                        return await resp.text()
        except:
            pass
    
    return None

async def scrape_ebay(query, min_p, max_p, prx_list=None, force_prx=False, max_pages=3):
    headers = get_ua()
    items = []
    seen_urls = set()
    
    for page in range(1, max_pages + 1):
        url = (f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}"
               f"&_udlo={min_p}&_udhi={max_p}&LH_BIN=1&_sop=10&_ipg=60&rt=nc&_pgn={page}")
        
        html = await fetch_page(url, headers, prx_list, force_prx)
        
        if not html:
            continue
        
        try:
            soup = BeautifulSoup(html, "html.parser")
            results = soup.select(".s-item")
            if not results:
                results = soup.select("[data-testid='item-card']")
            
            for item in results:
                title_el = item.select_one(".s-item__title")
                if not title_el:
                    title_el = item.select_one("h3")
                
                price_el = item.select_one(".s-item__price")
                if not price_el:
                    price_el = item.select_one("[data-testid='price']")
                
                link_el = item.select_one(".s-item__link")
                if not link_el:
                    link_el = item.select_one("a")
                
                if title_el and price_el and link_el:
                    title = title_el.get_text(strip=True)
                    if "New Listing" in title:
                        title = title.replace("New Listing", "").strip()
                    
                    price_txt = price_el.get_text(strip=True)
                    price = get_price(price_txt)
                    
                    link = link_el.get('href', '')
                    if link.startswith('/'):
                        link = "https://www.ebay.com" + link
                    
                    if (price is not None and 
                        min_p <= price <= max_p and 
                        len(title) > 10 and
                        "ebay.com" in link and
                        link not in seen_urls):
                        
                        items.append({
                            "title": title[:100],
                            "price": price,
                            "link": link.split('?')[0]
                        })
                        seen_urls.add(link.split('?')[0])
        
        except:
            continue
    
    return items[:15]

async def send_tg(token, chat, msg):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        'chat_id': chat, 
        'text': msg,
        'parse_mode': 'HTML',
        'disable_web_page_preview': False
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, timeout=10) as resp:
                return resp.status == 200
    except:
        return False

async def main(args):
    seen = set()
    use_prx = args.proxy.lower() == "true"
    
    banner()
    
    working_prx = []
    if use_prx:
        all_prx = load_proxies()
        if not all_prx:
            print("no proxies found, exiting")
            sys.exit(1)
        else:
            print("testing proxies...")
            
            tasks = [check_prx(prx) for prx in all_prx]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for prx, result in zip(all_prx, results):
                if result is True:
                    working_prx.append(prx)
            
            if not working_prx:
                print("no working proxies found, exiting")
                sys.exit(1)
            else:
                print(f"found {len(working_prx)} working proxies")
    
    spinner = asyncio.create_task(spin())
    start = time.time()
    
    try:
        while True:
            now = time.time()
            
            if args.duration > 0 and (now - start) > args.duration:
                break
            
            prx_to_use = working_prx if use_prx else None
            products = await scrape_ebay(args.query, args.min, args.max, prx_to_use, use_prx, max_pages=3)
            
            if use_prx and prx_to_use is not None and len(prx_to_use) == 0:
                print("\nno more proxies available, exiting")
                break
            
            new_items = []
            for p in products:
                if p["link"] not in seen:
                    new_items.append(p)
                    seen.add(p["link"])
            
            if new_items:
                print(f"\nfound {len(new_items)} new items")
                if use_prx and prx_to_use:
                    print(f"proxies left: {len(prx_to_use)}")
                
                for i, item in enumerate(new_items[:args.max_send]):
                    msg = f"<b>{item['title']}</b>\n\n"
                    msg += f"<b>Price:</b> ${item['price']:.2f}\n"
                    msg += f"<b>Link:</b> {item['link']}"
                    
                    ok = await send_tg(args.token, args.chat, msg)
                    if ok:
                        print(f"sent item: ${item['price']:.2f}")
                    else:
                        print(f"failed to send item")
                    
                    if i < len(new_items) - 1:
                        await asyncio.sleep(1)
            else:
                print(f"\nno new items found at {time.strftime('%H:%M:%S')}")
            
            if args.duration == 0 or (now - start) < args.duration:
                await asyncio.sleep(args.interval)
    
    finally:
        spinner.cancel()
        sys.stdout.write('\rdone.                     \n')
        print(f"total unique items found: {len(seen)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', required=True)
    parser.add_argument('--min', type=float, required=True)
    parser.add_argument('--max', type=float, required=True)
    parser.add_argument('--interval', type=int, default=60)
    parser.add_argument('--duration', type=int, default=0)
    parser.add_argument('--token', required=True)
    parser.add_argument('--chat', required=True)
    parser.add_argument('--max_send', type=int, default=3)
    parser.add_argument('--proxy', choices=["true", "false"], required=True)
    
    args = parser.parse_args()
    
    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        print("\nstopped")
    except Exception as e:
        print(f"error: {e}")
