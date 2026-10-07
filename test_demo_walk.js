const puppeteer = require('puppeteer-core');

(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: "new"
  });
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', err => console.log('PAGE ERROR:', err.toString()));

  await page.goto('http://127.0.0.1:5000/', { waitUntil: 'networkidle0' });
  await page.select('#locSelect', 'Library');
  await new Promise(r => setTimeout(r, 500));
  
  await page.click('button[onclick="openNavigation()"]');
  await new Promise(r => setTimeout(r, 500));
  
  console.log("Clicking Start Demo Walk");
  await page.click('#navDemoBtn');
  await new Promise(r => setTimeout(r, 2000)); // wait for walk to happen
  
  await browser.close();
})();
