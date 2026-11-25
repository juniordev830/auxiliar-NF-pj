(function(root) {
  function localDate(now = new Date()) {
    return [now.getFullYear(), String(now.getMonth()+1).padStart(2,'0'), String(now.getDate()).padStart(2,'0')].join('-');
  }
  function latestRequest() {
    let controller;
    return {
      begin() {
        controller?.abort();
        const current = new AbortController();
        controller = current;
        return {signal:current.signal,current:()=>controller===current&&!current.signal.aborted};
      },
      cancel() { controller?.abort(); controller=undefined; }
    };
  }
  const api = {localDate, latestRequest};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.PjUtils = api;
})(globalThis);
