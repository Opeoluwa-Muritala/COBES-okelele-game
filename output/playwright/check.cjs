const { chromium } = require('C:/Users/LENOVO/AppData/Local/npm-cache/_npx/31e32ef8478fbf80/node_modules/playwright');
(async () => {
  const browser = await chromium.launch({headless: true, executablePath: "C:/Users/LENOVO/AppData/Local/ms-playwright/chromium_headless_shell-1208/chrome-headless-shell-win64/chrome-headless-shell.exe"});
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  for (const [name, width, height] of [['desktop', 1280, 800], ['mobile', 390, 844]]) {
    await page.setViewportSize({width, height});
    for (const [screen, path] of [['select', '/'], ['you-guess', '/computer-thinks'], ['computer-guesses', '/player-thinks']]) {
      await page.goto('http://127.0.0.1:5055' + path);
      if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)) throw new Error('Overflow: ' + screen);
      await page.screenshot({path: `output/playwright/${name}-${screen}.png`, fullPage: true});
    }
  }
  await page.getByRole('button', {name: 'Mine is higher'}).click();
  await page.getByText('75', {exact:true}).waitFor();
  await page.getByRole('button', {name: "That's my number"}).click();
  await page.getByRole('heading', {name: 'Number found!'}).waitFor();
  await page.getByRole('link', {name: 'Choose another game'}).click();
  await page.getByRole('link', {name: 'Start guessing'}).click();
  await page.getByLabel('Your guess').fill('50');
  await page.getByLabel('Your guess').press('Enter');
  await page.waitForFunction(() => document.getElementById('attempts-label').textContent === 'Guesses: 1');
  if (errors.length) throw new Error(errors.join('\n'));
  console.log('PASS: six desktop/mobile captures, no overflow or JS errors, selection, clue, win, keyboard guess flows');
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });

