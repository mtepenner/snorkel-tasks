import { readFileSync, existsSync } from 'fs';
import { resolve } from 'path';
import { describe, it, expect } from 'vitest';

describe("Static Architecture Checks", () => {
  it("creates index.html with correct CDNs and output tag", () => {
    const filePath = resolve('/app/index.html');
    expect(existsSync(filePath)).toBe(true);

    const htmlContent = readFileSync(filePath, 'utf-8');
    
    // Check for React & Babel imports
    expect(htmlContent).toMatch(/react/i);
    expect(htmlContent).toMatch(/babel/i);
    
    // Ensure the output ID requirement is respected
    expect(htmlContent).toMatch(/id=["']stats-output["']/);
  });
});
