const test=require('node:test');
const assert=require('node:assert/strict');
const {periodQuery,dateLabel,dayRows,bucketRows}=require('../ControladorGastos/wwwroot/js/financeiro-utils.js');
test('período valida formato e limites',()=>{
  assert.equal(periodQuery('2026-05').toString(),'ano=2026&mes=05');
  for(const value of ['','1999-12','2201-01','2026-13','2026-1'])assert.throws(()=>periodQuery(value));
});
test('datas não mudam de dia por fuso horário',()=>assert.equal(dateLabel('2026-05-10'),'10/05/2026'));
test('linhas preservam valores e identificam faixas',()=>{
  const rows=dayRows([{data:'2026-05-10',receitas:0.3,despesas:0.01,saldo:0.29,quantidade:3}]);
  assert.equal(rows[0][0],'10/05/2026');
  assert.match(rows[0][3],/0,29/);
  assert.equal(rows[0][4],'3');
  assert.equal(bucketRows([{nome:'ATE_7_DIAS',aReceber:10,aPagar:2,saldoPrevisto:8,quantidade:1}])[0][0],'1 a 7 dias');
  assert.deepEqual(dayRows([]),[]);
});
