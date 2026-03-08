import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


def fetch_github_trending(languages: List[str] = None, time_range: str = "weekly", topics: List[str] = None) -> List[Dict]:
    """
    获取 GitHub Trending 项目
    
    Args:
        languages: 编程语言列表
        time_range: 时间范围 (daily, weekly, monthly)
        topics: topic 列表
    
    Returns:
        趋势项目列表
    """
    projects = []
    seen = set()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    params = {
        "since": time_range
    }
    
    if languages is None:
        languages = ["Python", "TypeScript"]
    
    if languages:
        for lang in languages:
            params["spoken_language_code"] = ""
            
            try:
                url = f"https://github.com/trending/{lang}"
                logger.info(f"Fetching GitHub Trending: {url}")
                
                response = requests.get(url, params=params, headers=headers, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "lxml")
                articles = soup.select("article.Box-row")
                
                for article in articles[:10]:
                    try:
                        title_elem = article.select_one("h2 a")
                        if not title_elem:
                            continue
                        
                        full_name = title_elem.get("href", "").strip("/")
                        if full_name in seen:
                            continue
                        seen.add(full_name)
                        
                        desc_elem = article.select_one("p")
                        description = desc_elem.text.strip() if desc_elem else ""
                        
                        stars_elem = article.select_one("span.d-inline-block.float-sm-right")
                        stars = stars_elem.text.strip() if stars_elem else "0"
                        
                        lang_elem = article.select_one("span[itemprop='programmingLanguage']")
                        language = lang_elem.text.strip() if lang_elem else lang
                        
                        projects.append({
                            "full_name": full_name,
                            "description": description,
                            "stars": stars,
                            "language": language,
                            "url": f"https://github.com/{full_name}"
                        })
                    except Exception as e:
                        logger.warning(f"Error parsing project: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error fetching GitHub Trending for {lang}: {e}")
    
    if topics:
        for topic in topics:
            try:
                url = f"https://github.com/topics/{topic}"
                logger.info(f"Fetching GitHub Topics: {url}")
                
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "lxml")
                articles = soup.select("article.border.rounded")
                
                for article in articles[:10]:
                    try:
                        title_elem = article.select_one("h3 a.Link.text-bold")
                        if not title_elem:
                            continue
                        
                        full_name = title_elem.get("href", "").strip("/")
                        if full_name in seen:
                            continue
                        seen.add(full_name)
                        
                        desc_elem = article.select_one("p.color-fg-muted")
                        description = desc_elem.text.strip() if desc_elem else ""
                        
                        stars_elem = article.select_one("span.Counter")
                        stars = stars_elem.text.strip() if stars_elem else "0"
                        
                        lang_elem = article.select_one("span[itemprop='programmingLanguage']")
                        language = lang_elem.text.strip() if lang_elem else "Unknown"
                        
                        projects.append({
                            "full_name": full_name,
                            "description": description,
                            "stars": stars,
                            "language": language,
                            "url": f"https://github.com/{full_name}"
                        })
                    except Exception as e:
                        logger.warning(f"Error parsing topic project: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error fetching GitHub Topics for {topic}: {e}")
    
    logger.info(f"Fetched {len(projects)} projects from GitHub Trending")
    return projects


def format_project_for_ai(project: Dict) -> str:
    """
    格式化项目信息用于 AI 摘要
    """
    return f"""项目: {project['full_name']}
Stars: {project['stars']}
描述: {project['description'][:200]}"""
