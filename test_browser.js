const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
  page.on('requestfailed', request => console.log('PAGE REQUEST FAILED:', request.url(), request.failure().errorText));

  try {
      await page.goto('http://127.0.0.1:5000/');
      await page.waitForTimeout(2000);
  } catch (e) {
      console.log('Navigation failed', e);
  }

  await browser.close();
})();
