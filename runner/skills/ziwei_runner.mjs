#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../..');
const profile = JSON.parse(fs.readFileSync(path.join(ROOT, 'inputs/profile.json'), 'utf8'));
const outDir = path.join(ROOT, 'outputs');
fs.mkdirSync(outDir, { recursive: true });

const date =
  process.env.RUN_DATE ||
  new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Taipei',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(new Date());

function fallback(error) {
  return {
    skill: 'ziwei',
    status: 'degraded',
    mode: 'E3_ZIWEI_SKELETON',
    date,
    external_error: error,
    warning:
      '未能真實調用 iztro 生成完整紫微盤；不輸出未驗證十二宮主星、完整四化落宮或大限宮位。',
    skeleton: {
      gender: profile.person.gender,
      birth_solar: profile.person.birth_solar,
      true_solar_time: profile.person.true_solar_time,
      birth_place: profile.person.birth_place,
      bazi: profile.person.bazi,
      day_master: profile.person.day_master,
      favorable_elements: profile.person.favorable_elements,
      unfavorable_elements: profile.person.unfavorable_elements,
      layers: {
        career: '利 IPO 審計底稿核對、披露差異與證據鏈整理',
        wealth: '有交易欲，但不宜重倉搏方向；僅做計劃內 T',
        health_emotion: '火土旺，眼壓、焦躁、心火偏高',
        migration_external: '外部科技修復與油價壓制並存',
        learning: '利 IFRS17 / SOA-FSA / IPO 規則框架化',
      },
    },
  };
}

// iztro bySolar 第二參數是時辰序號 0~12，不是 24 小時制。
// 17:01 真太陽時 = 酉時；常用序號：子=0，丑=1，寅=2，卯=3，辰=4，巳=5，午=6，未=7，申=8，酉=9，戌=10，亥=11，晚子=12。
const BIRTH_SOLAR_DATE = '1992-2-10';
const BIRTH_TIME_INDEX = 9;
const BIRTH_GENDER = '女';

async function main() {
  let payload;

  try {
    const { astro } = await import('iztro');

    const astrolabe = astro.bySolar(
      BIRTH_SOLAR_DATE,
      BIRTH_TIME_INDEX,
      BIRTH_GENDER,
      true,
      'zh-CN'
    );

    payload = {
      skill: 'ziwei',
      status: 'success',
      mode: 'E1_IZTRO_ZIWEI',
      date,
      input: {
        solar_date: BIRTH_SOLAR_DATE,
        time_index: BIRTH_TIME_INDEX,
        time_branch: '酉時',
        gender: BIRTH_GENDER,
        language: 'zh-CN',
        note: '真太陽時 17:01，正入酉時；iztro bySolar 使用 timeIndex=9，而非 hour=17。',
      },
      chart: astrolabe,
    };
  } catch (err) {
    payload = fallback(String(err?.stack || err));
  }

  fs.writeFileSync(
    path.join(outDir, `ziwei-${date}.json`),
    JSON.stringify(payload, null, 2),
    'utf8'
  );

  console.log(JSON.stringify(payload));
}

main().catch((err) => {
  const payload = fallback(String(err?.stack || err));
  fs.writeFileSync(
    path.join(outDir, `ziwei-${date}.json`),
    JSON.stringify(payload, null, 2),
    'utf8'
  );
  console.log(JSON.stringify(payload));
  process.exit(0);
});
