(() => {
 const $=id=>document.getElementById(id);
 const {latestRequest}=globalThis.PjUtils,{validId,differences}=globalThis.HistoricoUtils;
 const requests=latestRequest(),limit=10;
 let token='',timer,page=1,total=0,activeId=null;
 const initial=new URLSearchParams(location.search).get('id');
 if(initial!==null){try{$('id').value=validId(initial);}catch{}}
 function status(message){$('status').textContent=message;}
 function clear(){ $('results').hidden=true;$('entries').replaceChildren();$('page').textContent='';total=0;}
 function logout(message='Sessão encerrada.'){token='';activeId=null;page=1;requests.cancel();clearTimeout(timer);$('token').value='';clear();status(message);}
 function append(parent,tag,text){const el=document.createElement(tag);el.textContent=text;parent.append(el);return el;}
 function render(items){
   const target=$('entries');target.replaceChildren();
   if(!items.length)append(target,'p','Nenhuma alteração registrada.');
   for(const item of items){
     const block=document.createElement('section');block.className='panel';block.style.margin='12px 0';
     append(block,'h2',String(item.acao));
     append(block,'p',String(item.ocorridoEm)+' (UTC)');
     try{
       const changes=differences(item.antes,item.depois);
       if(!changes.length)append(block,'p','Nenhuma diferença nos campos exibidos.');
       for(const change of changes)append(block,'p',change.field+': '+change.from+' → '+change.to);
     }catch{append(block,'p','Não foi possível interpretar os campos desta alteração.');}
     target.append(block);
   }
 }
 async function load(reset=false){
   if(!token){status('Informe o token de leitura.');return;}
   const current=requests.begin();clear();status('Carregando…');
   clearTimeout(timer);timer=setTimeout(()=>logout('Sessão encerrada por inatividade.'),15*60*1000);
   try{
     const id=validId($('id').value);
     if(reset||id!==activeId)page=1;
     activeId=id;
     const response=await fetch('/api/pj/lancamentos/'+id+'/historico?'+new URLSearchParams({page,limit}),{headers:{Authorization:'Bearer '+token},signal:current.signal});
     if(!current.current())return;
     if(response.status===401){logout('Token inválido.');return;}
     if(!response.ok)throw new Error('Falha na consulta ('+response.status+').');
     const data=await response.json();
     if(!current.current())return;
     total=data.total;
     const last=Math.max(1,Math.ceil(total/limit));
     if(page>last){page=last;return load();}
     render(data.items);$('page').textContent='Página '+page+' de '+last;
     $('previous').disabled=page<=1;$('next').disabled=page>=last;
     $('results').hidden=false;status(total+' alteração(ões) encontrada(s).');
   }catch(e){if(current.current()&&e.name!=='AbortError'){clear();status(e.message);}}
 }
 $('access').addEventListener('click',()=>{const value=$('token').value.trim();logout('');token=value;load(true);});
 $('token').addEventListener('keydown',e=>{if(e.key==='Enter')$('access').click();});
 $('logout').addEventListener('click',()=>logout());
 $('refresh').addEventListener('click',()=>load(true));
 $('id').addEventListener('change',()=>load(true));
 $('previous').addEventListener('click',()=>{if(page>1){page--;load();}});
 $('next').addEventListener('click',()=>{if(page*limit<total){page++;load();}});
 window.addEventListener('pagehide',()=>logout());
})();
