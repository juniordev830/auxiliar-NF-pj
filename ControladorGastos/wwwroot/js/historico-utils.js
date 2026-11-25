(function(root){
  function validId(value) {
    const raw=String(value??'');
    if(!/^[1-9]\d{0,9}$/.test(raw))throw new Error('Informe um ID inteiro positivo.');
    const id=Number(raw);
    if(id>2147483647)throw new Error('ID fora do intervalo permitido.');
    return id;
  }
  const keys=['Descricao','Tipo','Categoria','Contraparte','Valor','Competencia','Vencimento','DataPagamento','ExcluidoEm','Versao'];
  const labels=['Descrição','Tipo','Categoria','Cliente / fornecedor','Valor','Competência','Vencimento','Pagamento','Exclusão','Versão'];
  function snapshot(raw){
    if(raw==null)return {};
    const parsed=JSON.parse(raw);
    if(!parsed||typeof parsed!=='object'||Array.isArray(parsed))throw new Error('Registro de histórico inválido.');
    return parsed;
  }
  function differences(before,after){
    const old=snapshot(before),now=snapshot(after);
    return keys.flatMap((key,i)=>{
      const from=old[key]??null,to=now[key]??null;
      return Object.is(from,to)?[]:[{field:labels[i],from:from===null?'—':String(from),to:to===null?'—':String(to)}];
    });
  }
  const api={validId,differences};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
  else root.HistoricoUtils=api;
})(globalThis);
