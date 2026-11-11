(() => {
  if (navigator.globalPrivacyControl === true || navigator.doNotTrack === '1') return;
  try {
    if (localStorage.getItem('arkaya-analytics-optout') === '1') return;
  } catch {
    return;
  }
  const beacon = document.createElement('script');
  beacon.src = 'https://static.cloudflareinsights.com/beacon.min.js';
  beacon.setAttribute('data-cf-beacon', '{"token": "46eab74577aa4822aa03045caac50e8a"}');
  beacon.defer = true;
  document.body.appendChild(beacon);
})();
