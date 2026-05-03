import { test, expect } from "@playwright/test";

const markdownPaper = `# Abstract

Quantum entanglement lets quantum systems share information across experiments [1]. Quantum sensors rely on entanglement [2].

# Results

Our quantum measurement pipeline tracks entanglement in repeated trials [3].

# Conclusion

Entanglement improves the final quantum estimate [4].
`;

const pdfExtractedText = `Introduction
Quantum entanglement appears in the introduction [1].
Conclusion
Entanglement stabilizes the quantum result [2].`;

function analyzeText(text: string) {
  const citations = (text.match(/\[\d+\]/g) || []).length;
  const totalWords = (text.match(/\b[\w'-]+\b/g) || []).length;
  const density = (keyword: string) => {
    const count = (text.match(new RegExp(`\\b${keyword}\\b`, "gi")) || []).length;
    return { count, density: totalWords ? Number((count / totalWords).toFixed(3)) : 0 };
  };

  return {
    citations,
    totalWords,
    keywordDensity: {
      quantum: density("quantum"),
      entanglement: density("entanglement"),
    },
  };
}

test("markdown upload analyzes citations, keyword density, and section summaries", async ({ page }) => {
  await page.goto("/");

  await page.setInputFiles('input[type="file"]', '/app/test-fixtures/paper.md');

  const output = page.locator('#analysis-output');
  await expect(output).toBeVisible({ timeout: 15000 });

  let analysis: any;
  await expect
    .poll(async () => {
      const text = await output.textContent();
      if (!text) return "";
      try {
        analysis = JSON.parse(text);
        return analysis.fileType;
      } catch {
        return "";
      }
    }, { timeout: 15000 })
    .toBe('markdown');

  const expected = analyzeText(markdownPaper);
  expect(analysis.citations).toBe(expected.citations);
  expect(analysis.totalWords).toBe(expected.totalWords);
  expect(analysis.keywordDensity.quantum).toEqual(expected.keywordDensity.quantum);
  expect(analysis.keywordDensity.entanglement).toEqual(expected.keywordDensity.entanglement);

  expect(analysis.sectionSummaries).toEqual([
    {
      title: 'Abstract',
      summary: 'Quantum entanglement lets quantum systems share information across experiments [1].',
    },
    {
      title: 'Results',
      summary: 'Our quantum measurement pipeline tracks entanglement in repeated trials [3].',
    },
    {
      title: 'Conclusion',
      summary: 'Entanglement improves the final quantum estimate [4].',
    },
  ]);

  await expect(page.getByRole('heading', { name: 'Citation Frequency' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Keyword Density' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Section Summaries' })).toBeVisible();
  await expect(page.locator('.sections strong').filter({ hasText: 'Abstract' })).toBeVisible();
});

test("pdf upload parses text-based pdf files and updates the dashboard", async ({ page }) => {
  await page.goto("/");

  await page.setInputFiles('input[type="file"]', '/app/test-fixtures/paper.pdf');

  const output = page.locator('#analysis-output');
  let analysis: any;
  await expect
    .poll(async () => {
      const text = await output.textContent();
      if (!text) return "";
      try {
        analysis = JSON.parse(text);
        return analysis.fileType;
      } catch {
        return "";
      }
    }, { timeout: 15000 })
    .toBe('pdf');

  const expected = analyzeText(pdfExtractedText);
  expect(analysis.citations).toBe(expected.citations);
  expect(analysis.totalWords).toBe(expected.totalWords);
  expect(analysis.keywordDensity.quantum).toEqual(expected.keywordDensity.quantum);
  expect(analysis.keywordDensity.entanglement).toEqual(expected.keywordDensity.entanglement);
  expect(analysis.sectionSummaries).toEqual([
    {
      title: 'Introduction',
      summary: 'Quantum entanglement appears in the introduction [1].',
    },
    {
      title: 'Conclusion',
      summary: 'Entanglement stabilizes the quantum result [2].',
    },
  ]);
});
