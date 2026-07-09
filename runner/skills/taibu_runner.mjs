#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../..');
const profile = JSON.parse(fs.readFileSync(path.join(ROOT, 'inputs/profile.json'), 'utf8'));
const outDir = path.join(ROOT, 'outputs');
fs.mkdirSync(outDir, { recursive: true });
const date = process.env.RUN_DATE || new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Taipei', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());

function symbolic(error, importedKeys = []) {
  return {
    skill: 'taibu',
    status: importedKeys.length ? 'partial' : 'degraded',
    mode: importedKeys.length ? 'E2_TAIBU_CORE_IMPORT_SMOKE' : 'E3_TAIBU_SYMBOLIC_RUNNER',
    date,
    external_error: error,
    imported_keys: importedKeys,
    warning: '未啟動 taibu-mcp stdio server；本輸出為太卜/太乙象意 Runner，不聲稱已調用 MCP 工具。',
    divination: {
      main_symbol: '火土壓盤，外部風險擾動',
      change_symbol: '科技線有修復，但油價與利率預期壓制風險偏好',
      risk_symbol: '衝高無量易回落，防假突破',
      action_symbol: '等二次確認，不追第一波',
      stop_symbol: '破開盤價 + 破 VWAP + 放量，停止加倉',
      bazi_anchor: profile.person.bazi,
      favorable_elements: profile.person.favorable_elements
    }
  };
}

async function main() {
  let payload;
  try {
    const core = await import('taibu-core');
    const keys = Object.keys(core).sort();
    payload = symbolic(null, keys);
  } catch (err) {
    payload = symbolic(String(err?.stack || err), []);
  }
  fs.writeFileSync(path.join(outDir, `taibu-${date}.json`), JSON.stringify(payload, null, 2), 'utf8');
  console.log(JSON.stringify(payload));
}

main().catch(err => {
  const payload = symbolic(String(err?.stack || err), []);
  fs.writeFileSync(path.join(outDir, `taibu-${date}.json`), JSON.stringify(payload, null, 2), 'utf8');
  console.log(JSON.stringify(payload));
  process.exit(0);
});
