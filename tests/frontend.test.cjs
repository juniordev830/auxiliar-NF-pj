const test = require('node:test');
const assert = require('node:assert/strict');
const {localDate, latestRequest} = require('../ControladorGastos/wwwroot/js/utils.js');
test('data local é calculada no instante informado, inclusive após meia-noite',()=>{
  assert.equal(localDate(new Date(2026,10,24,23,59)), '2026-11-24');
  assert.equal(localDate(new Date(2026,10,25,0,1)), '2026-11-25');
});
test('consulta nova invalida a anterior; logout invalida a atual',()=>{
  const requests = latestRequest();
  const first = requests.begin(), second = requests.begin();
  assert.equal(first.signal.aborted,true);
  assert.equal(first.current(),false);
  assert.equal(second.current(),true);
  requests.cancel();
  assert.equal(second.current(),false);
});
