const test=require('node:test');
const assert=require('node:assert/strict');
const {validId,differences}=require('../ControladorGastos/wwwroot/js/historico-utils.js');
test('valida IDs antes de consultar a API',()=>{
  assert.equal(validId('2147483647'),2147483647);
  for(const value of ['0','-1','1.2','1/2','2147483648','abc',''])assert.throws(()=>validId(value));
});
test('mostra somente campos alterados, inclusive valores nulos e zero',()=>{
 const result=differences('{"Descricao":"A","Valor":1,"DataPagamento":"2026-01-01"}','{"Descricao":"A","Valor":0,"DataPagamento":null}');
 assert.deepEqual(result,[{field:'Valor',from:'1',to:'0'},{field:'Pagamento',from:'2026-01-01',to:'—'}]);
});
test('criação e conteúdo textual não são interpretados como HTML',()=>{
 const result=differences(null,'{"Descricao":"<img src=x onerror=bad()>"}');
 assert.deepEqual(result,[{field:'Descrição',from:'—',to:'<img src=x onerror=bad()>'}]);
 assert.throws(()=>differences('[]','{}'));
});
