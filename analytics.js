(() => {
  if (navigator.globalPrivacyControl === true || navigator.doNotTrack === '1') return;
  try {
    if (localStorage.getItem('arkaya-analytics-optout') === '1') return;
  } catch {
    return;
  }
  const beacon = document.createElement('script');
  beacon.src = 'https://static.cloudflareinsights.com/beacon.min.js';
  beacon.setAttribute('data-cf-beacon', '{"token": "__CF_BEACON_TOKEN__"}');
  beacon.defer = true;
  document.body.appendChild(beacon);
})();
