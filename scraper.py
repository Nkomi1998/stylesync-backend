from playwright.async_api import async_playwright
from PIL import Image as PILImage
from colorthief import ColorThief
from urllib.parse import urlparse
from typing import Dict, Any
import re
import io
import asyncio

async def scrape_site(url: str) -> Dict[str, Any]:
    """Extract design tokens from website using headless browser."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        try:
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Extract CSS computed styles
            styles = await page.evaluate("""
                () => {
                    const token_map = {
                        colors: new Set(),
                        fonts: new Set(),
                        fontSizes: new Set(),
                        spacings: new Set()
                    };
                    
                    Array.from(document.querySelectorAll('*')).forEach(el => {
                        const cs = window.getComputedStyle(el);
                        
                        // Colors
                        ['color', 'background-color', 'border-color'].forEach(prop => {
                            const val = cs[prop];
                            if (val && val !== 'rgba(0, 0, 0, 0)' && val !== 'transparent') {
                                token_map.colors.add(val);
                            }
                        });
                        
                        // Typography
                        token_map.fonts.add(cs.fontFamily);
                        token_map.fontSizes.add(cs.fontSize);
                        
                        // Spacing
                        ['margin', 'padding', 'gap'].forEach(side => {
                            ['top', 'right', 'bottom', 'left'].forEach(dir => {
                                const prop = `${side}-${dir}`;
                                const val = cs[prop];
                                if (val && val !== '0px') token_map.spacings.add(val);
                            });
                        });
                    });
                    
                    return token_map;
                }
            """)
            
            # Image palette extraction
            palette = []
            images = await page.locator('img').all()
            for img in images[:5]:
                try:
                    src = await img.get_attribute('src')
                    if src and not src.startswith('data:'):
                        resp = await context.request.fetch(src, timeout=5000)
                        img_data = await resp.body()
                        color_thief = ColorThief(io.BytesIO(img_data))
                        dominant = color_thief.get_color(quality=1)
                        palette.append(f'rgb({dominant[0]},{dominant[1]},{dominant[2]})')
                except Exception:
                    continue
            
            await browser.close()
            
            return {
                'url': url,
                'status': 'success',
                'colors': list(styles['colors'])[:20],
                'typography': {
                    'fonts': list(styles['fonts'])[:10],
                    'sizes': sorted(list(styles['fontSizes']))[:8]
                },
                'spacing': sorted(list(styles['spacings']))[:12],
                'image_palette': list(set(palette))[:8]
            }
        except Exception as e:
            await browser.close()
            return {
                'url': url,
                'status': f'error: {str(e)}',
                'colors': [],
                'typography': {},
                'spacing': [],
                'image_palette': []
            }

if __name__ == '__main__':
    asyncio.run(scrape_site('https://vercel.com'))

