const puppeteer = require('puppeteer-core');
const fs = require('fs');

(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', // Assuming Windows Chrome
    headless: "new"
  });
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));

  try {
      await page.goto('http://127.0.0.1:5000/', { waitUntil: 'networkidle0', timeout: 5000 });
      await page.waitForTimeout(1000);
      console.log("Success loading page!");
  } catch (e) {
      console.log('Navigation failed', e.message);
  }

  await browser.close();
})();
