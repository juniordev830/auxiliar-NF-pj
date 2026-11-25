    (() => {
      const $ = id => document.getElementById(id);
      const money = value => new Intl.NumberFormat('pt-BR', {style:'currency',currency:'BRL'}).format(Number(value || 0));
      const { localDate, latestRequest } = globalThis.PjUtils;
      $('periodo').value = localDate().slice(0, 7);
      $('competencia').value = localDate();
      let page = 1, total = 0, limit = 10;
      let accessToken = ''; // Apenas em memória; nunca salvo em localStorage.
      let editId = null;
      let editVersion = null;
      let sessionVersion = 0;
      const loads = latestRequest();
      let sessionTimer;
      function resetForm() {
        editId = null;
        editVersion = null;
        $('form').reset();
        $('competencia').value = localDate();
        $('form-title').textContent = 'Novo lançamento';
        $('cancel-edit').hidden = true;
      }
      function clearData() {
        for (const id of ['receitas','despesas','saldo','realizado']) $(id).textContent = '—';
        $('pendencias').textContent = 'Pagamentos registrados';
        $('tabela').replaceChildren();
        $('vazio').hidden = true;
        $('paginacao').textContent = '';
        $('contagem').textContent = 'Informe seu token de acesso.';
        $('anterior').disabled = $('proximo').disabled = true;
        page = 1; total = 0;
      }
      function logout(message = 'Sessão encerrada.') {
        accessToken = ''; sessionVersion++; loads.cancel();
        clearTimeout(sessionTimer);
        $('access-token').value = '';
        clearData(); resetForm(); notify(message);
      }
      function touchSession() {
        clearTimeout(sessionTimer);
        if (accessToken) sessionTimer = setTimeout(() => logout('Sessão encerrada por inatividade.'), 15 * 60 * 1000);
      }
      function beginEdit(item) {
        editId = item.id;
        editVersion = item.versao;
        $('form-title').textContent = 'Editar lançamento';
        $('cancel-edit').hidden = false;
        for (const id of ['descricao','tipo','categoria','contraparte','valor'])
          $(id).value = item[id] ?? '';
        $('competencia').value = (item.competencia || '').slice(0,10);
        $('vencimento').value = (item.vencimento || '').slice(0,10);
        $('pagamento').value = (item.dataPagamento || '').slice(0,10);
        $('descricao').focus();
      }
      const period = () => { const [ano, mes] = $('periodo').value.split('-'); return {ano, mes}; };
      const qs = () => { const {ano, mes} = period(); return new URLSearchParams({ano, mes}); };
      function notify(message, error=false) {
        const el=$('notice'); el.textContent=message; el.className='notice '+(error?'error':'success');
      }
      async function request(url, options) {
        if (!accessToken) throw new Error('Informe o token de acesso antes de continuar.');
        const version = sessionVersion;
        touchSession();
        const res = await fetch(url, {
          ...options,
          headers: { ...(options?.headers || {}), Authorization: 'Bearer ' + accessToken }
        });
        if (version !== sessionVersion) throw new DOMException('Sessão alterada', 'AbortError');
        if (res.status === 401) {
          logout('Token inválido. Acesse novamente.');
          throw new DOMException('Sessão inválida', 'AbortError');
        }
        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          throw new Error(body.error || 'Não foi possível completar a operação ('+res.status+').');
        }
        if (res.status===204) return null;
        return res.json();
      }
      function cell(tr, text, cls='') {
        const td=document.createElement('td'); td.textContent=String(text??''); if(cls) td.className=cls; tr.append(td); return td;
      }
      function row(item) {
        const tr=document.createElement('tr');
        const descr=cell(tr,item.descricao,'desc');
        if(item.contraparte) {
          const sub=document.createElement('div'); sub.className='muted'; sub.textContent=item.contraparte; descr.append(sub);
        }
        cell(tr,item.tipo==='RECEITA'?'Receita':'Despesa');
        cell(tr,money(item.valor));
        const status=cell(tr,'');
        const tag=document.createElement('span'); tag.className='tag '+item.status.toLowerCase(); tag.textContent=item.status; status.append(tag);
        const action=cell(tr,'');
        const btn=document.createElement('button'); btn.type='button'; btn.className='btn small ghost';
        btn.textContent=item.status==='PAGO'?'Reabrir':'Marcar pago';
        btn.addEventListener('click',async()=>{
          btn.disabled=true;
          try {
            await request('/api/pj/lancamentos/'+item.id+'/pagamento',{
              method:'PUT',headers:{'Content-Type':'application/json'},
              body:JSON.stringify({dataPagamento:item.status==='PAGO'?null:(localDate()+'T00:00:00'),versao:item.versao})
            });
            await load();
          }catch(e){if(e.name !== 'AbortError') notify(e.message,true);}finally{btn.disabled=false;}
        });
        action.append(btn);
        const edit = document.createElement('button');
        edit.type = 'button'; edit.className = 'btn small ghost'; edit.textContent = 'Editar';
        edit.addEventListener('click', () => beginEdit(item));
        action.append(edit);
        const history = document.createElement('a');
        history.className = 'btn small ghost'; history.textContent = 'Histórico';
        history.href = '/historico.html?id=' + encodeURIComponent(item.id);
        action.append(history);
        return tr;
      }
      async function load(){
        if (!accessToken) return;
        const req = loads.begin();
        const selected = qs();
        const currentPage = page;
        try {
          const filter=$('filtro').value, params=new URLSearchParams(selected); params.set('page',currentPage); params.set('limit',limit);
          if(filter) params.set('status',filter);
          const [summary,data]=await Promise.all([
            request('/api/pj/resumo?'+selected,{signal:req.signal}),request('/api/pj/lancamentos?'+params,{signal:req.signal})
          ]);
          if (!req.current()) return;
          $('receitas').textContent=money(summary.receitasPrevistas);
          $('despesas').textContent=money(summary.despesasPrevistas);
          $('saldo').textContent=money(summary.saldoPrevisto);
          $('realizado').textContent=money(summary.saldoRealizado);
          $('pendencias').textContent=summary.quantidadeAtrasada+' compromisso(s) em atraso';
          total=data.total;
          const last = Math.max(1, Math.ceil(total/limit));
          if (currentPage > last) { page = last; return load(); }
          $('tabela').replaceChildren(...data.items.map(row));
          $('contagem').textContent=total+' lançamento(s) encontrado(s)';
          $('vazio').hidden=total!==0;
          $('anterior').disabled=page<=1;
          $('proximo').disabled=page*limit>=total;
          $('paginacao').textContent='Página '+page+' de '+Math.max(1,Math.ceil(total/limit));
          $('exportar').href='/api/pj/exportar.csv?'+qs();
        }catch(e){if(req.current() && e.name !== 'AbortError'){clearData(); notify(e.message,true);$('contagem').textContent='Falha ao carregar';}}
      }
      $('authorize').addEventListener('click', () => {
        const candidate = $('access-token').value.trim();
        logout('');
        if (!candidate) { notify('Informe um token de acesso válido.', true); return; }
        accessToken = candidate; touchSession(); load();
      });
      $('access-token').addEventListener('keydown', event => {
        if (event.key === 'Enter') { event.preventDefault(); $('authorize').click(); }
      });
      $('logout').addEventListener('click', () => logout());
      $('cancel-edit').addEventListener('click', resetForm);
      $('exportar').addEventListener('click', async event => {
        event.preventDefault();
        if (!accessToken) { notify('Informe o token antes de exportar.', true); return; }
        try {
          const version = sessionVersion;
          touchSession();
          const response = await fetch('/api/pj/exportar.csv?' + qs(), { headers: { Authorization: 'Bearer ' + accessToken } });
          if (version !== sessionVersion) return;
          if (response.status === 401) { logout('Token inválido.'); return; }
          if (!response.ok) throw new Error('Exportação não autorizada (' + response.status + ').');
          const blob = await response.blob();
          if (version !== sessionVersion) return;
          const fileUrl = URL.createObjectURL(blob);
          const anchor = document.createElement('a');
          anchor.href = fileUrl;
          anchor.download = 'lancamentos-pj.csv';
          document.body.append(anchor);
          anchor.click();
          anchor.remove();
          setTimeout(() => URL.revokeObjectURL(fileUrl), 1000);
        } catch (error) { notify(error.message, true); }
      });
      $('periodo').addEventListener('change',()=>{page=1; load();});
      $('filtro').addEventListener('change',()=>{page=1; load();});
      $('anterior').addEventListener('click',()=>{if(page>1){page--;load();}});
      $('proximo').addEventListener('click',()=>{if(page*limit<total){page++;load();}});
      $('form').addEventListener('submit',async e=>{
        e.preventDefault();
        const btn=$('save'); btn.disabled=true;
        const target = editId;
        const version = sessionVersion;
        const body={
          versao:editVersion,
          descricao:$('descricao').value, tipo:$('tipo').value,
          categoria:$('categoria').value,contraparte:$('contraparte').value,
          valor:Number($('valor').value), competencia:$('competencia').value+'T00:00:00',
          vencimento:$('vencimento').value?$('vencimento').value+'T00:00:00':null,
          dataPagamento:$('pagamento').value?$('pagamento').value+'T00:00:00':null
        };
        try{
          await request('/api/pj/lancamentos'+(target===null?'':'/'+target),{method:target===null?'POST':'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
          if (version !== sessionVersion) return;
          resetForm(); page=1;
          $('periodo').value = body.competencia.slice(0,7);
          notify('Lançamento salvo com sucesso.'); await load();
        }catch(error){if(version === sessionVersion && error.name !== 'AbortError') notify(error.message,true);}finally{btn.disabled=false;}
      });
      clearData();
    })();
  