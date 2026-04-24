import { describe, it, expect } from "vitest";
import { screen } from "@testing-library/dom";
import { userEvent } from "@testing-library/user-event";

/**
 * Example unit test using Vitest + Testing Library (DOM).
 * Works with no framework; for React add @testing-library/react, for Vue add @testing-library/vue.
 */
describe("Unit (Vitest)", () => {
  it("can assert on DOM", () => {
    document.body.innerHTML = `<h1>Hello, UI task</h1>`;
    const heading = screen.getByRole("heading", { name: /hello, ui task/i });
    expect(heading).toBeTruthy();
    expect(heading.textContent).toBe("Hello, UI task");
  });

  it("can use Testing Library userEvent", async () => {
    document.body.innerHTML = `<button>Click me</button>`;
    const button = screen.getByRole("button", { name: /click me/i });
    const user = userEvent.setup();
    await user.click(button);
    expect(document.activeElement).toBe(button);
  });
});
