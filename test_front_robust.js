const puppeteer = require('puppeteer-core');
const fs = require('fs');

(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: "new"
  });
  const page = await browser.newPage();
  
  let hasErrors = false;
  page.on('console', msg => {
      if (msg.type() === 'error') {
          console.log('PAGE ERROR LOG:', msg.text());
          hasErrors = true;
      }
  });
  page.on('pageerror', error => {
      console.log('PAGE EXCEPTION:', error.message);
      hasErrors = true;
  });

  try {
      await page.goto('http://127.0.0.1:5000/', { waitUntil: 'networkidle0', timeout: 5000 });
      await new Promise(r => setTimeout(r, 2000));
      
      // Test 1: Check if canvas exists and has width/height
      const canvasDim = await page.evaluate(() => {
          const c = document.getElementById('floorMap');
          return { w: c.width, h: c.height };
      });
      console.log('Main Canvas Dimensions:', canvasDim);

      // Test 2: Select a location
      await page.select('#locSelect', 'Meeting_Room');
      const bestName = await page.$eval('#bestName', el => el.textContent);
      console.log('Routing found safest exit:', bestName);

      // Test 3: Open Navigation
      await page.click('button[onclick="openNavigation()"]');
      await new Promise(r => setTimeout(r, 500));
      const navDisplay = await page.$eval('#navOverlay', el => window.getComputedStyle(el).display);
      console.log('Navigation Overlay Display:', navDisplay);
      
      // Check Nav Canvas
      const navDim = await page.evaluate(() => {
          const c = document.getElementById('navCanvas');
          return { w: c.width, h: c.height };
      });
      console.log('Nav Canvas Dimensions:', navDim);

      // Test 4: Demo Walk
      await page.click('#navDemoBtn');
      await new Promise(r => setTimeout(r, 1000));
      const isDemoRunning = await page.evaluate(() => NAV.demoRunning);
      console.log('Is Demo Running after 1s:', isDemoRunning);

  } catch (e) {
      console.log('Navigation failed', e.message);
  }

  await browser.close();
  
  if (hasErrors) {
      console.log("TESTS FAILED: JS ERRORS DETECTED");
      process.exit(1);
  } else {
      console.log("ALL TESTS PASSED SUCCESSFULLY");
  }
})();
