"""Optional UI check: install playwright==1.51.0 and its Chromium browser."""
import csv
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]

def main():
    data=json.loads((ROOT/'reports/analysis.json').read_text())
    errors=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1440,'height':1100},accept_downloads=True)
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto((ROOT/'dashboard/index.html').as_uri())
        assert page.locator('#trips').inner_text()==f"{data['summary']['trips']:,}"
        checks=0
        for borough in ['All boroughs','Manhattan','Brooklyn','Queens','Bronx','Staten Island']:
            for day in ['All days','Weekday','Weekend']:
                page.select_option('#borough',label=borough)
                page.select_option('#day',label=day)
                expected=sum(r['trips'] for r in data['exports']['cube'] if (borough=='All boroughs' or r['borough']==borough) and (day=='All days' or r['day_type']==day))
                assert page.locator('#trips').inner_text()==f'{expected:,}'
                assert page.locator('#zones tr').count()<=10
                assert page.locator('svg').count()==2
                assert page.locator('svg').evaluate_all("els=>els.every(e=>!e.innerHTML.includes('NaN'))")
                checks+=1
        page.select_option('#measure','fare_revenue')
        assert 'Base fare revenue' in page.locator('#daily svg').get_attribute('aria-label')
        with page.expect_download() as info:
            page.click('#export')
        download=info.value
        assert download.suggested_filename=='taxi-filtered-aggregates.csv'
        with open(download.path()) as handle:
            exported=list(csv.DictReader(handle))
        assert sum(int(r['trips']) for r in exported)==expected
        page.select_option('#borough',label='All boroughs');page.select_option('#day',label='All days')
        # QA screenshots are transient, outside the repository/deliverable.
        page.screenshot(path=str(ROOT.parent/'dashboard-desktop-qa.png'),full_page=True)
        page.set_viewport_size({'width':390,'height':844})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(ROOT.parent/'dashboard-mobile-qa.png'),full_page=True)
        assert not errors,errors
        browser.close()
    print(f'PASS: {checks} filter combinations, measure switch, CSV reconciliation, mobile overflow, no page errors')

if __name__=='__main__':
    main()
