(function(){
  const year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();

  // Cursor glow: updates CSS vars for radial gradient center
  let raf;
  const root = document.documentElement;
  window.addEventListener('mousemove', (e)=>{
    if (raf) cancelAnimationFrame(raf);
    raf = requestAnimationFrame(()=>{
      root.style.setProperty('--mx', e.clientX + 'px');
      root.style.setProperty('--my', e.clientY + 'px');
    });
  }, {passive:true});
})();
