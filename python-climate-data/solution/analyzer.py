import pandas as pd
import json
import graphviz

def milestone_1():
    # Load data
    df = pd.read_csv('/app/workspace/data/climate.csv')
    with open('/app/workspace/data/metadata.json', 'r') as f:
        meta = json.load(f)
    
    # Map region names
    df['region'] = df['region_id'].astype(str).map(meta)
    
    # Save cleaned data
    cleaned = df.to_dict(orient='records')
    with open('/app/workspace/data/cleaned.json', 'w') as f:
        json.dump(cleaned, f, indent=4)
    return df

def milestone_2(df):
    # Calculate trends
    trends = df.groupby('region')['temperature'].mean().to_dict()
    
    # Save trends
    with open('/app/workspace/data/trends.json', 'w') as f:
        json.dump(trends, f, indent=4)
    return trends

def milestone_3(trends):
    # Visualize with Graphviz
    dot = graphviz.Digraph(comment='Climate Trends')
    for region, temp in trends.items():
        dot.node(region, region)
        dot.node(f"{temp:.2f}", f"Avg Temp: {temp:.2f}°C")
        dot.edge(region, f"{temp:.2f}")
    
    # Render (outputs to climate_graph.png)
    dot.render('/app/workspace/output/climate_graph', format='png', cleanup=False)

if __name__ == "__main__":
    df = milestone_1()
    trends = milestone_2(df)
    milestone_3(trends)