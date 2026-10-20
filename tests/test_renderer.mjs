import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const area=path.join(root,'output','renderer-tests');
fs.mkdirSync(area,{recursive:true});
test('报告渲染将来源HTML作为文字，拒绝脚本链接',()=>{
  const folder=fs.mkdtempSync(path.join(area,'safe-'));
  const source=path.join(folder,'source.md'),output=path.join(folder,'report.html');
  fs.writeFileSync(source,'# 报告\n\n<script>alert(1)</script>\n\n[点击](javascript:alert(1))');
  const result=spawnSync(process.execPath,[path.join(root,'scripts','render-report.mjs'),source,output],{encoding:'utf8'});
  assert.equal(result.status,0,result.stderr);
  const html=fs.readFileSync(output,'utf8');
  assert.ok(html.includes('&lt;script&gt;'));
  assert.ok(!/<script\b/i.test(html));
  assert.ok(!/href=["']javascript:/i.test(html));
});
test('已有报告不被覆盖',()=>{
  const folder=fs.mkdtempSync(path.join(area,'preserve-'));
  const source=path.join(folder,'source.md'),output=path.join(folder,'report.html');
  fs.writeFileSync(source,'# 新稿');fs.writeFileSync(output,'保留原稿');
  const result=spawnSync(process.execPath,[path.join(root,'scripts','render-report.mjs'),source,output],{encoding:'utf8'});
  assert.equal(result.status,1);
  assert.equal(fs.readFileSync(output,'utf8'),'保留原稿');
});

