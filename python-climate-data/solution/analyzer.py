import pandas as pd
import json
import graphviz

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
    dot = graphviz.Digraph(comment='Climate Trends')
    for region, temp in trends.items():
        dot.node(region, region)
        dot.node(f"{temp:.2f}", f"Avg Temp: {temp:.2f}°C")
        dot.edge(region, f"{temp:.2f}")
    
    dot.render('/app/workspace/output/climate_graph', format='png', cleanup=False)

if __name__ == "__main__":
    df = milestone_1()
    trends = milestone_2(df)
    milestone_3(trends)
