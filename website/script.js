(function(){
  const DEFAULT_URL = 'http://localhost:8512';
  const params = new URLSearchParams(window.location.search);
  const override = params.get('dashboard');
  const url = override ? override : DEFAULT_URL;

  const top = document.getElementById('demoBtnTop');
  const bot = document.getElementById('demoBtnBottom');
  const path = document.getElementById('demoPath');
  if (top) top.href = url;
  if (bot) bot.href = url;
  if (path) path.querySelector('code').textContent = url;

  const year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();
})();

