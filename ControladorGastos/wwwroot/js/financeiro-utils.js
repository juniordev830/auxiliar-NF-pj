(function(root) {
  const labels = Object.freeze({ATRASADO:'Vencido', HOJE:'Hoje', ATE_7_DIAS:'1 a 7 dias', ATE_30_DIAS:'8 a 30 dias', MAIS_DE_30_DIAS:'Mais de 30 dias', SEM_VENCIMENTO:'Sem vencimento'});
  const formatter = new Intl.NumberFormat('pt-BR', {style:'currency',currency:'BRL'});
  const money = value => formatter.format(value);
  function periodQuery(month) {
    const match = /^(\d{4})-(0[1-9]|1[0-2])$/.exec(month);
    if (!match || Number(match[1]) < 2000 || Number(match[1]) > 2200) throw new Error('Selecione um mês válido.');
    return new URLSearchParams({ano:match[1],mes:match[2]});
  }
  function dateLabel(date) {
    const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(date);
    if (!match) return date;
    return [match[3],match[2],match[1]].join('/');
  }
  function dayRows(days) { return days.map(d=>[dateLabel(d.data),money(d.receitas),money(d.despesas),money(d.saldo),String(d.quantidade)]); }
  function bucketRows(rows) { return rows.map(d=>[Object.hasOwn(labels,d.nome)?labels[d.nome]:d.nome,money(d.aReceber),money(d.aPagar),money(d.saldoPrevisto),String(d.quantidade)]); }
  const api={periodQuery,dateLabel,money,dayRows,bucketRows};
  if(typeof module!=='undefined'&&module.exports) module.exports=api;
  else root.FinanceiroUtils=api;
})(globalThis);
