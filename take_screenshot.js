const puppeteer = require('puppeteer-core');
const fs = require('fs');

(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: "new"
  });
  const page = await browser.newPage();
  
  // Set viewport to mobile size
  await page.setViewport({ width: 390, height: 844 }); // iPhone 12 Pro size

  try {
      await page.goto('http://127.0.0.1:5000/', { waitUntil: 'networkidle0', timeout: 5000 });
      await new Promise(r => setTimeout(r, 1000));
      
      // Select location
      await page.select('#locSelect', 'Library');
      await new Promise(r => setTimeout(r, 1000));
      
      // Open Navigation
      await page.click('button[onclick="openNavigation()"]');
      await new Promise(r => setTimeout(r, 1000));
      
      // Take screenshot
      if (!fs.existsSync('scratch')) {
          fs.mkdirSync('scratch');
      }
      await page.screenshot({ path: 'scratch/nav_mobile.png' });
      console.log("Screenshot saved to scratch/nav_mobile.png");

  } catch (e) {
      console.log('Navigation failed', e.message);
  }

  await browser.close();
})();
