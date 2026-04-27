import os
from bs4 import BeautifulSoup

def test_m2_ui_files_exist():
    """Verify that the required index.html file is present at the expected path."""
    assert os.path.exists('/app/workspace/src/templates/index.html'), "index.html missing"

def test_m2_ui_content():
    """Verify dashboard layout includes config form, chart area, navigation, dropdown, slider, and viewport meta tag."""
    with open('/app/workspace/src/templates/index.html', 'r') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
    nav = soup.find(['nav', 'aside', 'div'], id=lambda x: x in ['sidebar', 'nav'] if x else False) or soup.find(['nav', 'aside'])
    assert nav is not None, "Missing sidebar/nav element"
    
    nav_text = nav.get_text().lower()
    assert 'data' in nav_text and 'model' in nav_text and 'inference' in nav_text, "Sidebar must have data prep, model config, inference links"

    form = soup.find('form')
    assert form is not None, "Missing model configuration <form>"
    
    select = form.find('select')
    assert select is not None and len(select.find_all('option')) >= 2, "Missing model selection dropdown with >=2 options"
    
    slider = form.find('input', {'type': 'range'})
    assert slider is not None, "Missing hyperparameter sliders"
    
    chart = soup.find(['canvas', 'svg']) or soup.find(id=lambda x: x and 'chart' in x.lower())
    assert chart is not None, "Missing chart element"
    
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    assert viewport is not None, "Missing responsive viewport meta tag"
