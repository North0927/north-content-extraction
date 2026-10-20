import fs from 'node:fs';
import path from 'node:path';
import MarkdownIt from 'markdown-it';
const args=process.argv.slice(2).filter(x=>x!=='--');
if(args.length!==2){console.error('用法：npm run report -- 输入.md 输出.html');process.exit(2)}
const [input,output]=args;
const body=new MarkdownIt({html:false,linkify:false,typographer:false}).render(fs.readFileSync(input,'utf8'));
fs.mkdirSync(path.dirname(path.resolve(output)),{recursive:true});
const doc='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>内容提炼报告</title><style>body{max-width:960px;margin:40px auto;padding:0 24px;font:16px/1.9 "Microsoft YaHei",sans-serif;color:#25322e}h2{margin-top:36px;border-top:1px solid #ddd;padding-top:18px}table{border-collapse:collapse;width:100%;display:block;overflow:auto}td,th{border:1px solid #ddd;padding:8px;text-align:left}th{background:#f2f6f4}a{color:#167668;overflow-wrap:anywhere}pre{background:#f2f4f3;padding:14px;overflow:auto}img{max-width:100%}</style></head><body>'+body+'</body></html>';
try{fs.writeFileSync(output,doc,{encoding:'utf8',flag:'wx'});console.log('已生成：'+output)}catch(error){console.error(error.code==='EEXIST'?'目标已存在，请用新版本文件名；未覆盖原文件。':error.message);process.exit(1)}
