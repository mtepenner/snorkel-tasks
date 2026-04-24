import os

def test_m2_ui_files_exist():
    """1 pt: drop the main html into /app/workspace/src/templates/index.html."""
    assert os.path.exists('/app/workspace/src/templates/index.html'), "index.html missing"

def test_m2_ui_content():
    """1 pt: build a basic dashboard layout with config form and chart area."""
    with open('/app/workspace/src/templates/index.html', 'r') as f:
        content = f.read().lower()
        
    # STRENGTHENED assertions
    assert 'sidebar' in content or 'nav' in content, "Missing sidebar/nav element"
    assert 'data' in content and 'model' in content and 'inference' in content, "Sidebar must have data prep, model config, inference links"
    assert '<select' in content, "Missing model selection dropdown"
    assert 'range' in content or 'slider' in content, "Missing hyperparameter sliders"
    assert '<canvas' in content or '<svg' in content or 'chart' in content, "Missing chart element"
    assert 'viewport' in content, "Missing responsive viewport meta tag"
