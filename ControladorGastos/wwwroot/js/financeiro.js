(() => {
  const $ = id => document.getElementById(id);
  const {localDate,latestRequest}=globalThis.PjUtils;
  const {periodQuery,money,dayRows,bucketRows}=globalThis.FinanceiroUtils;
  const requests=latestRequest();
  let token='', timer;
  $('month').value=localDate().slice(0,7);
  $('reference').value=localDate();
  function status(text){$('status').textContent=text;}
  function clear(){ $('results').hidden=true; for(const id of ['income','expense','balance','count','receivable','payable','days','buckets']) $(id).replaceChildren(); }
  function logout(message='Sessão encerrada.'){ token=''; $('token').value=''; requests.cancel(); clearTimeout(timer); clear(); status(message); }
  function render(id,rows){
    const target=$(id); target.replaceChildren();
    for(const values of rows){const tr=document.createElement('tr'); for(const value of values){const td=document.createElement('td'); td.textContent=value; tr.append(td);} target.append(tr);}
    if(!rows.length){const tr=document.createElement('tr'),td=document.createElement('td');td.colSpan=5;td.textContent='Sem movimentações.';tr.append(td);target.append(tr);}
  }
  async function load(){
    if(!token){status('Informe o token de leitura.');return;}
    const current=requests.begin();
    clear();status('Carregando…');
    clearTimeout(timer);timer=setTimeout(()=>logout('Sessão encerrada por inatividade.'),15*60*1000);
    async function get(url){
      const response=await fetch(url,{signal:current.signal,headers:{Authorization:'Bearer '+token}});
      if(!current.current()) throw new DOMException('Consulta cancelada','AbortError');
      if(response.status===401){logout('Token inválido.');throw new DOMException('Sessão encerrada','AbortError');}
      if(!response.ok)throw new Error('Falha na consulta ('+response.status+').');
      return response.json();
    }
    try{
      const month=periodQuery($('month').value);
      if(!$('reference').value||!$('reference').checkValidity()) throw new Error('Selecione uma data de referência válida.');
      const due=new URLSearchParams({referencia:$('reference').value});
      const [cash,bills]=await Promise.all([get('/api/pj/fluxo-caixa?'+month),get('/api/pj/contas-a-vencer?'+due)]);
      if(!current.current())return;
      for(const [id,value] of [['income',cash.receitas],['expense',cash.despesas],['balance',cash.saldo],['receivable',bills.aReceber],['payable',bills.aPagar]]) $(id).textContent=money(value);
      $('count').textContent=String(cash.quantidade);
      render('days',dayRows(cash.dias));render('buckets',bucketRows(bills.faixas));
      $('results').hidden=false;status('Consulta atualizada.');
    }catch(e){if(current.current()&&e.name!=='AbortError'){clear();status(e.message);}}
  }
  $('access').addEventListener('click',()=>{const value=$('token').value.trim();logout('');token=value;load();});
  $('token').addEventListener('keydown',e=>{if(e.key==='Enter')$('access').click();});
  $('logout').addEventListener('click',()=>logout());
  $('refresh').addEventListener('click',load);
  $('month').addEventListener('change',load);
  $('reference').addEventListener('change',load);
  window.addEventListener('pagehide',()=>logout());
})();
