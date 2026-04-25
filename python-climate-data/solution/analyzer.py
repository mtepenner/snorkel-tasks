import pandas as pd
import json
import subprocess
import os

def milestone_1():
    df = pd.read_csv('/app/workspace/data/climate.csv')
    with open('/app/workspace/data/metadata.json', 'r') as f:
        meta = json.load(f)
    
    df['region'] = df['region_id'].astype(str).map(meta)
    
    df = df[df['year'] >= 2021]
    
    cleaned = df.to_dict(orient='records')
    with open('/app/workspace/data/cleaned.json', 'w') as f:
        json.dump(cleaned, f, indent=4)
    return df

def milestone_2(df):
    trends = df.groupby('region')['temperature'].mean().to_dict()
    with open('/app/workspace/data/trends.json', 'w') as f:
        json.dump(trends, f, indent=4)
    return trends

def milestone_3(trends):
    os.makedirs('/app/workspace/output', exist_ok=True)

    # Build DOT source manually — avoids any graphviz library version quirks
    lines = ['digraph {']
    for region, temp in trends.items():
        temp_str = f"{temp:.2f}"
        lines.append(f'    "{region}" [label="{region}"]')
        lines.append(f'    "{temp_str}" [label="Avg Temp: {temp_str}C"]')
        lines.append(f'    "{region}" -> "{temp_str}"')
    lines.append('}')
    dot_source = '\n'.join(lines) + '\n'

    dot_file = '/app/workspace/output/climate_graph.gv'
    png_file = '/app/workspace/output/climate_graph.png'

    with open(dot_file, 'w', encoding='utf-8') as f:
        f.write(dot_source)

    subprocess.run(['dot', '-Tpng', dot_file, '-o', png_file], check=True)

if __name__ == "__main__":
    df = milestone_1()
    trends = milestone_2(df)
    milestone_3(trends)
