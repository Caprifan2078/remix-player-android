const fs=require('fs'),vm=require('vm'),assert=require('assert');
const script=fs.readFileSync(__dirname+'/lyrics-extract.js','utf8');
function node(innerText,hidden=false,children=[]){return {innerText,hidden,contains(n){return children.includes(n)},getClientRects(){return hidden?[]:[{}]}}}
function run(nodes){return vm.runInNewContext(script,{document:{querySelectorAll(){return nodes}},window:{getComputedStyle(n){return {visibility:n.hidden?'hidden':'visible',display:n.hidden?'none':'block'}}}})}
const verse='These are five or more visible words\nA second fictional line';
assert.strictEqual(run([node(verse)]),verse);
assert.strictEqual(run([node(verse,true)]),'');
const child=node(verse);assert.strictEqual(run([node(verse,false,[child]),child]),verse);
assert.strictEqual(run([node(verse),node(verse)]),verse);
assert.strictEqual(run([node('menu')]),'');
assert.strictEqual(run([node('word '.repeat(16000))]),'');
assert.strictEqual(run([]),'');
console.log('PASS: 7 structured visible lyric extraction checks');
