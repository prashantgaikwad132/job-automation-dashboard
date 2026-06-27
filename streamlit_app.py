"""
🚀 Job Automation Dashboard - Production Ready
Beautiful, responsive dashboard for mobile & desktop
Auto-syncs with backend API for jobs, emails, and statistics
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import time
import logging
from pathlib import Path
import json
import os

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="QA Job Finder - Prashant Gaikwad",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",  # Better for mobile
    menu_items={
        'About': "Job Automation Dashboard for QA Automation Engineers"
    }
)

# ==================== CUSTOM CSS (Mobile Optimized) ====================
st.markdown("""
<style>
    /* Global Styles */
    :root {
        --primary: #0066cc;
        --success: #00cc66;
        --warning: #ffaa00;
        --danger: #ff6666;
        --light: #f8f9fa;
        --dark: #1a1a1a;
    }
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* Main content */
    .main {
        padding: 0.5rem;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        min-height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .metric-card h3 {
        font-size: 0.9em;
        opacity: 0.9;
        margin-bottom: 0.5rem;
    }
    
    .metric-card .number {
        font-size: 2.5em;
        font-weight: bold;
    }
    
    /* Job Cards */
    .job-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 5px solid #0066cc;
        transition: all 0.3s ease;
    }
    
    .job-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    
    .job-card.high-match {
        border-left-color: #00cc66;
        background: linear-gradient(to right, rgba(0,204,102,0.05), white);
    }
    
    .job-card.medium-match {
        border-left-color: #ffaa00;
        background: linear-gradient(to right, rgba(255,170,0,0.05), white);
    }
    
    .job-card.low-match {
        border-left-color: #ff6666;
        background: linear-gradient(to right, rgba(255,102,102,0.05), white);
    }
    
    .job-title {
        font-size: 1.2em;
        font-weight: 600;
        color: #0066cc;
        margin-bottom: 0.5rem;
    }
    
    .job-company {
        font-size: 1.05em;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.3rem;
    }
    
    .job-meta {
        font-size: 0.9em;
        color: #666;
        margin-bottom: 0.5rem;
    }
    
    .skills-container {
        margin: 1rem 0;
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    
    .skill-badge {
        background-color: #e3f2fd;
        color: #0066cc;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 500;
    }
    
    .match-score {
        display: inline-block;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 1.3em;
        box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
    }
    
    /* Schedule Timer */
    .schedule-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .schedule-banner h2 {
        margin-bottom: 0.5rem;
    }
    
    .schedule-time {
        font-size: 2em;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .schedule-countdown {
        font-size: 1.1em;
        opacity: 0.9;
    }
    
    /* Buttons */
    .download-btn {
        background-color: #0066cc;
        color: white;
        padding: 0.8rem 1.5rem;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        font-weight: 600;
        width: 100%;
        margin-top: 0.5rem;
    }
    
    .download-btn:hover {
        background-color: #0052a3;
    }
    
    /* Filters */
    .filter-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
    }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .main {
            padding: 0.3rem;
        }
        
        .metric-card {
            padding: 1rem;
            min-height: 80px;
        }
        
        .metric-card .number {
            font-size: 2em;
        }
        
        .job-card {
            padding: 1rem;
        }
        
        .job-title {
            font-size: 1.05em;
        }
        
        .schedule-banner {
            padding: 1.5rem;
        }
        
        .schedule-time {
            font-size: 1.6em;
        }
    }
    
    /* Links */
    a {
        color: #0066cc;
        text-decoration: none;
    }
    
    a:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# ==================== CONFIG ====================
class Config:
    TARGET_SKILLS = [
        'Python', 'Playwright', 'Pytest', 'API testing',
        'Jenkins', 'Git', 'Docker', 'QA Automation',
        'Selenium', 'Test Automation'
    ]
    TARGET_LOCATIONS = ['Pune', 'Remote', 'WFH', 'Work from home']
    SCHEDULE_TIMES = ['09:00', '15:00', '19:00']
    RECIPIENT_EMAIL = 'prashantgaikwad132@gmail.com'

# ==================== DATABASE ====================
class JobDatabase:
    def __init__(self, db_path: str = 'jobs_database.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT UNIQUE,
                title TEXT,
                company TEXT,
                location TEXT,
                job_url TEXT,
                description TEXT,
                hr_email TEXT,
                salary TEXT,
                job_type TEXT,
                posted_date TEXT,
                scraped_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                skills_matched TEXT,
                match_score INTEGER,
                source TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_job(self, job_data: dict) -> bool:
        """Add job to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO jobs (job_id, title, company, location, job_url, 
                                 description, hr_email, salary, job_type,
                                 posted_date, skills_matched, match_score, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_data.get('job_id'),
                job_data.get('title'),
                job_data.get('company'),
                job_data.get('location'),
                job_data.get('job_url'),
                job_data.get('description'),
                job_data.get('hr_email'),
                job_data.get('salary'),
                job_data.get('job_type'),
                job_data.get('posted_date'),
                ','.join(job_data.get('skills_matched', [])),
                job_data.get('match_score', 0),
                job_data.get('source', 'unknown')
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_all_jobs(self, min_score: int = 40) -> list:
        """Get all jobs"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM jobs 
            WHERE match_score >= ?
            ORDER BY match_score DESC, scraped_date DESC
        ''', (min_score,))
        
        jobs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jobs
    
    def get_recent_jobs(self, hours: int = 24) -> list:
        """Get recent jobs"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        start_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        cursor.execute('''
            SELECT * FROM jobs 
            WHERE scraped_date >= ? AND match_score >= 40
            ORDER BY match_score DESC, scraped_date DESC
        ''', (start_time,))
        
        jobs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jobs

# ==================== JOB SCRAPER ====================
class JobScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_indeed(self) -> list:
        """Scrape Indeed"""
        jobs = []
        try:
            search_terms = "QA Automation Engineer Python Playwright"
            url = f"https://in.indeed.com/jobs?q={search_terms}&l=Pune&radius=0"
            
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_cards = soup.find_all('div', class_='job_seen_beacon')
            
            for card in job_cards[:20]:
                try:
                    title_elem = card.find('h2', class_='jobTitle')
                    company_elem = card.find('span', class_='companyName')
                    
                    if not all([title_elem, company_elem]):
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    company = company_elem.get_text(strip=True)
                    location = card.find('div', class_='companyLocation')
                    location = location.get_text(strip=True) if location else "Not specified"
                    
                    job_link = card.find('a', class_='jcs-ExactMatch')
                    job_url = f"https://in.indeed.com{job_link['href']}" if job_link else ""
                    
                    snippet = card.find('div', class_='job-snippet')
                    description = snippet.get_text(strip=True) if snippet else ""
                    
                    match_score = self.calculate_score(title, description)
                    skills = self.extract_skills(title, description)
                    
                    if match_score > 40:
                        jobs.append({
                            'job_id': f"indeed_{title}_{company}",
                            'title': title,
                            'company': company,
                            'location': location,
                            'job_url': job_url,
                            'description': description,
                            'hr_email': '',
                            'salary': '',
                            'job_type': 'Permanent',
                            'posted_date': datetime.now().isoformat(),
                            'skills_matched': skills,
                            'match_score': match_score,
                            'source': 'Indeed'
                        })
                except:
                    continue
        except Exception as e:
            st.error(f"Error scraping Indeed: {e}")
        
        return jobs
    
    def scrape_naukri(self) -> list:
        """Scrape Naukri"""
        jobs = []
        try:
            url = "https://www.naukri.com/jobs-in-pune-qa-automation-engineer"
            
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_cards = soup.find_all('article', class_='jobCard')
            
            for card in job_cards[:20]:
                try:
                    title_elem = card.find('a', class_='jobTitle')
                    company_elem = card.find('a', class_='subTitle')
                    
                    if not all([title_elem, company_elem]):
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    company = company_elem.get_text(strip=True)
                    location = card.find('span', class_='jobCardLocation')
                    location = location.get_text(strip=True) if location else "Not specified"
                    
                    job_url = title_elem.get('href', '')
                    snippet = card.find('div', class_='job-desc')
                    description = snippet.get_text(strip=True) if snippet else ""
                    
                    match_score = self.calculate_score(title, description)
                    skills = self.extract_skills(title, description)
                    
                    if match_score > 40:
                        jobs.append({
                            'job_id': f"naukri_{title}_{company}",
                            'title': title,
                            'company': company,
                            'location': location,
                            'job_url': job_url,
                            'description': description,
                            'hr_email': '',
                            'salary': '',
                            'job_type': 'Permanent',
                            'posted_date': datetime.now().isoformat(),
                            'skills_matched': skills,
                            'match_score': match_score,
                            'source': 'Naukri'
                        })
                except:
                    continue
        except Exception as e:
            st.error(f"Error scraping Naukri: {e}")
        
        return jobs
    
    def calculate_score(self, title: str, description: str) -> int:
        """Calculate match score"""
        score = 0
        text = f"{title} {description}".lower()
        
        if any(kw in text for kw in ['qa', 'automation', 'test automation']):
            score += 30
        else:
            return 0
        
        if 'python' in text:
            score += 20
        
        if any(kw in text for kw in ['playwright', 'selenium']):
            score += 20
        
        for skill in ['pytest', 'api', 'jenkins', 'docker', 'ci/cd', 'git']:
            if skill in text:
                score += 5
        
        if any(loc in text for loc in ['pune', 'remote', 'wfh']):
            score += 10
        
        if any(kw in text for kw in ['java', 'c#', '.net']):
            score -= 20
        
        return max(0, min(100, score))
    
    def extract_skills(self, title: str, description: str) -> list:
        """Extract skills"""
        text = f"{title} {description}".lower()
        matched = []
        
        for skill in Config.TARGET_SKILLS:
            if skill.lower() in text:
                matched.append(skill)
        
        return list(set(matched))

# ==================== UI COMPONENTS ====================
def get_next_schedule_time():
    """Get next scheduled email"""
    now = datetime.now()
    schedule_times = [9, 15, 19]
    
    for hour in schedule_times:
        if hour > now.hour:
            next_time = now.replace(hour=hour, minute=0, second=0)
            return next_time
    
    next_time = now.replace(hour=9, minute=0, second=0) + timedelta(days=1)
    return next_time

def render_job_card(job: dict):
    """Render job card HTML"""
    score = job.get('match_score', 0)
    
    if score >= 80:
        card_class = "high-match"
    elif score >= 60:
        card_class = "medium-match"
    else:
        card_class = "low-match"
    
    skills = job.get('skills_matched', '')
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(',') if s.strip()]
    
    skills_html = ''.join([f'<span class="skill-badge">{s}</span>' for s in skills])
    
    job_url = job.get('job_url', '')
    hr_email = job.get('hr_email', '')
    
    url_btn = f'<a href="{job_url}" target="_blank">📲 Apply Now</a>' if job_url else "No URL"
    
    html = f"""
    <div class="job-card {card_class}">
        <div style="display: flex; gap: 1rem; justify-content: space-between; align-items: start;">
            <div style="flex: 1;">
                <div class="job-title">{job.get('title', 'N/A')}</div>
                <div class="job-company">{job.get('company', 'N/A')}</div>
                <div class="job-meta">📍 {job.get('location', 'N/A')} • {job.get('source', 'Unknown')}</div>
                <div class="skills-container">
                    {skills_html}
                </div>
                <div style="margin-top: 1rem; font-size: 0.9em;">
                    {url_btn}
                    {'<br/>' + f'📧 {hr_email}' if hr_email else ''}
                </div>
            </div>
            <div style="text-align: center;">
                <div class="match-score">{score}</div>
            </div>
        </div>
    </div>
    """
    return html

# ==================== MAIN APP ====================
def main():
    # Initialize database
    db = JobDatabase()
    
    # Load jobs
    all_jobs = db.get_all_jobs(min_score=40)
    recent_jobs = db.get_recent_jobs(hours=24)
    high_match = [j for j in all_jobs if j['match_score'] >= 80]
    
    # Header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #0066cc; margin: 0;">🎯 QA Automation Job Finder</h1>
        <p style="color: #666; margin: 0.5rem 0 0 0;">Personalized job alerts for Prashant Gaikwad</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Schedule Banner
    next_schedule = get_next_schedule_time()
    time_until = next_schedule - datetime.now()
    hours = time_until.seconds // 3600
    minutes = (time_until.seconds % 3600) // 60
    
    st.markdown(f"""
    <div class="schedule-banner">
        <h2>⏰ Next Email Download</h2>
        <div class="schedule-time">{next_schedule.strftime('%I:%M %p')}</div>
        <div class="schedule-countdown">in {hours}h {minutes}m</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 Total Jobs</h3>
            <div class="number">{len(all_jobs)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🆕 Last 24h</h3>
            <div class="number">{len(recent_jobs)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🎯 High Match</h3>
            <div class="number">{len(high_match)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg = sum(j['match_score'] for j in all_jobs) / len(all_jobs) if all_jobs else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>⚡ Avg Score</h3>
            <div class="number">{avg:.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filters Section
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.subheader("🔍 Search & Filter")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        min_score = st.slider("Min Score", 0, 100, 40, key="min_score")
    
    with col2:
        sources = sorted(set([j['source'] for j in all_jobs]))
        selected_sources = st.multiselect("Source", sources, default=sources, key="sources")
    
    with col3:
        search = st.text_input("Search by company/title", key="search")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply filters
    filtered_jobs = all_jobs.copy()
    filtered_jobs = [j for j in filtered_jobs if j['match_score'] >= min_score]
    filtered_jobs = [j for j in filtered_jobs if j['source'] in selected_sources]
    
    if search:
        search_lower = search.lower()
        filtered_jobs = [j for j in filtered_jobs 
                        if search_lower in j['title'].lower() or search_lower in j['company'].lower()]
    
    # Download Excel
    if filtered_jobs:
        df = pd.DataFrame(filtered_jobs)
        df_export = df[['title', 'company', 'location', 'job_url', 'hr_email', 'salary', 'match_score', 'source']]
        df_export.columns = ['Job Title', 'Company', 'Location', 'Job URL', 'HR Email', 'Salary', 'Match Score', 'Source']
        df_export = df_export.sort_values('Match Score', ascending=False)
        
        from io import BytesIO
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Jobs')
        
        buffer.seek(0)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.download_button(
                "📥 Download Excel",
                buffer.getvalue(),
                f"job_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col2:
            csv = df_export.to_csv(index=False)
            st.download_button(
                "📥 Download CSV",
                csv,
                f"job_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv",
                use_container_width=True
            )
    
    st.markdown("---")
    
    # Job Listings
    st.subheader(f"📋 Jobs Found: {len(filtered_jobs)}")
    
    if filtered_jobs:
        for job in filtered_jobs:
            st.markdown(render_job_card(job), unsafe_allow_html=True)
    else:
        st.info("✨ No jobs match your criteria. Try adjusting filters!")
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **⏰ Email Schedule:**
        - 9:00 AM Daily
        - 3:00 PM Daily
        - 7:00 PM Daily
        """)
    
    with col2:
        st.markdown("""
        **🔄 Auto Updates:**
        - Every 2 hours
        - From Indeed, Naukri
        - Smart matching
        """)
    
    with col3:
        st.markdown("""
        **👤 Your Profile:**
        - Role: QA Automation
        - Skills: Python, Playwright
        - Locations: Pune, Remote
        """)

if __name__ == '__main__':
    main()
