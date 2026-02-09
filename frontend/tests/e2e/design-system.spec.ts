import { test, expect } from '@playwright/test';

test.describe('Design System Page', () => {
    test.beforeEach(async ({ page }) => {
        // Navigate to the design system page
        await page.goto('http://localhost:5173/design-system');
        console.log('Current URL:', page.url());
        await page.screenshot({ path: 'design-system-debug.png' });
    });

    test('should render the design system header', async ({ page }) => {
        const header = page.getByRole('heading', { name: 'Design System', exact: true });
        await expect(header).toBeVisible({ timeout: 15000 });
        await expect(page.getByText('Apple-inspired atomic components')).toBeVisible({ timeout: 15000 });
    });

    test('should show correct brand colors', async ({ page }) => {
        // Check if the ColorCard for Brand Blue is visible and has the correct hex text
        const blueCard = page.getByText('Brand Blue');
        await expect(blueCard).toBeVisible();
        await expect(page.getByText('#0071e3')).toBeVisible();
    });

    test('should render buttons with correct styles', async ({ page }) => {
        const primaryButton = page.getByRole('button', { name: 'Default Button' });
        await expect(primaryButton).toBeVisible({ timeout: 15000 });

        // Log classes and computed style for debugging
        const classes = await primaryButton.getAttribute('class');
        const computedStyle = await primaryButton.evaluate((el) => {
            const style = window.getComputedStyle(el);
            return {
                borderRadius: style.borderRadius,
                backgroundColor: style.backgroundColor,
                display: style.display
            };
        });

        const radiusValue = parseFloat(computedStyle.borderRadius);
        expect(radiusValue).toBeGreaterThan(15);
    });

    test('should render score rings with correct values', async ({ page }) => {
        // We have a score ring with 85
        const score85 = page.getByText('85', { exact: true });
        await expect(score85).toBeVisible({ timeout: 15000 });

        // Check if it has the success color (brand-success)
        // Correcting evaluation to find the progress circle
        const color = await score85.evaluate((el) => {
            const container = el.parentElement;
            if (!container) return null;
            const svg = container.querySelector('svg');
            if (!svg) return null;
            const circles = svg.querySelectorAll('circle');
            if (circles.length < 2) return null;
            return window.getComputedStyle(circles[1]).stroke;
        });
        // #34c759 roughly corresponds to rgb(52, 199, 89)
        expect(color).toContain('rgb(52, 199, 89)');
    });

    test('should render badges with correct variants', async ({ page }) => {
        const successBadge = page.getByText('Genuine');
        await expect(successBadge).toBeVisible({ timeout: 15000 });

        const bgColor = await successBadge.evaluate((el) => window.getComputedStyle(el).backgroundColor);
        // Tailwind 4 might return oklab/oklch. Let's check for the alpha value at least.
        expect(bgColor).toMatch(/0\.1\)$/);
    });

    test('should render progress bars', async ({ page }) => {
        await expect(page.getByText('Aesthetic Match')).toBeVisible({ timeout: 15000 });
        const aestheticValue = page.getByText('85%', { exact: true });
        await expect(aestheticValue).toBeVisible({ timeout: 15000 });
    });
});
