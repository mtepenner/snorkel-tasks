import { readFileSync, existsSync } from 'fs';
import { resolve } from 'path';
import { describe, it, expect } from 'vitest';

describe("Static Architecture Checks", () => {
  it("creates index.html with react cdns, file picker, and analysis output", () => {
    const filePath = resolve('/app/index.html');
    expect(existsSync(filePath)).toBe(true);

    const htmlContent = readFileSync(filePath, 'utf-8');
    
    expect(htmlContent).toMatch(/vendor\/[^"']*react[^"']*\.js/i);
    expect(htmlContent).toMatch(/vendor\/[^"']*react-dom[^"']*\.js/i);
    expect(htmlContent).toMatch(/vendor\/[^"']*babel[^"']*\.js/i);
    expect(htmlContent).toMatch(/vendor\/[^"']*pdf[^"']*\.js/i);

    expect(htmlContent).toMatch(/type=["']file["']/i);
    expect(htmlContent).toMatch(/accept=["'][^"']*\.md[^"']*\.markdown[^"']*\.pdf[^"']*["']/i);
    expect(htmlContent).toMatch(/id=["']analysis-output["']/);
    expect(htmlContent).toMatch(/Citation Frequency/i);
    expect(htmlContent).toMatch(/Keyword Density/i);
    expect(htmlContent).toMatch(/Section Summaries/i);
  });
});
