#!/usr/bin/env node
/**
 * test-tariff-change.mjs
 * Diagnostic script: checks whether UTM5 /customer_api caches
 * the subscriber profile after a tariff change.
 *
 * Usage:
 *   node test-tariff-change.mjs LOGIN PASSWORD
 *
 * It logs in, reads the current tariff, changes to an alternative,
 * reads the profile again (same session), then performs a
 * logout+login cycle and reads again.
 *
 * If the tariff changes only after relogin, the server-side cache
 * is confirmed and the auto-logout+login fix is required.
 */

const BASE = process.env.API_BASE || 'https://lk.liga-link.net/customer_api';
const [login, password] = process.argv.slice(2);

let sid = null;

async function api(method, path, body) {
  const headers = {
    Accept: 'application/json, text/plain, */*',
    'Content-Type': 'application/json',
    ...(sid ? { Cookie: `sid_customer=${sid}` } : {}),
  };
  const res = await fetch(`${BASE}${path}`, { method, headers, ...(body ? { body: JSON.stringify(body) } : {}) });
  const text = await res.text();

  // Extract sid from Set-Cookie (web) or body (RN fallback)
  const setCookie = res.headers.get('set-cookie');
  if (setCookie) {
    const m = setCookie.match(/sid_customer=([^;]+)/);
    if (m) sid = m[1];
  }
  if (text && path.includes('/login') && !path.includes('/logout')) {
    try {
      const j = JSON.parse(text);
      if (j.sid_customer) sid = j.sid_customer;
      else if (j.token) sid = j.token;
    } catch { /* not JSON */ }
  }

  return text ? JSON.parse(text) : undefined;
}

function showProfile(label, profile) {
  const account = profile?.accounts?.[0];
  const tariffIds = (account?.tariffs || []).map((t) => t.id).join(',') || 'none';
  const names = (account?.tariffs || []).map((t) => `"${t.name}"`).join(', ');
  console.log(`\n--- ${label} ---`);
  console.log(`  Account: ${account?.id || 'N/A'}  Balance: ${account?.balance ?? 'N/A'}`);
  console.log(`  Tariffs: [${tariffIds}]  Names: ${names}`);
}

(async () => {
  if (!login || !password) {
    console.error('Usage: node test-tariff-change.mjs LOGIN PASSWORD');
    console.error('Environment: API_BASE (default: https://lk.liga-link.net/customer_api)');
    process.exit(1);
  }

  // 1. Login
  await api('POST', '/login', { login, password, mobile_telephone: '' });
  if (!sid) { console.error('Login failed: no sid'); process.exit(1); }

  // 2. Profile before
  const before = await api('GET', '/auth/profile');
  showProfile('BEFORE change', before);

  // 3. Pick alternative tariff
  const all = await api('GET', '/auth/tariffs');
  const currentIds = new Set((before.accounts?.[0]?.tariffs || []).map((t) => t.id));
  const alt = all.find((t) => !currentIds.has(t.id));
  if (!alt) { console.log('\nNo alternative tariff available. Exiting.'); process.exit(0); }
  console.log(`\nTarget alternative: id=${alt.id} "${alt.name}"`);

  // 4. Change tariff
  const account = before.accounts[0];
  const linkId = account.tariffs?.[0]?.tariff_link_id;
  if (!linkId) { console.error('No tariff_link_id found'); process.exit(1); }
  await api('POST', '/auth/tariffs', {
    account_id: account.id,
    tariff_link_id: linkId,
    next_tariff_id: alt.id,
  });

  // 5. Profile after (same session)
  const afterSameSid = await api('GET', '/auth/profile');
  showProfile('AFTER change (same session)', afterSameSid);

  // 6. Logout + relogin
  sid = null;
  await api('POST', '/login', { login, password, mobile_telephone: '' });

  // 7. Profile after relogin
  const afterRelogin = await api('GET', '/auth/profile');
  showProfile('AFTER relogin', afterRelogin);

  // 8. Verdict
  const t0 = (before.accounts?.[0]?.tariffs || []).map((t) => t.id).join(',');
  const t1 = (afterSameSid.accounts?.[0]?.tariffs || []).map((t) => t.id).join(',');
  const t2 = (afterRelogin.accounts?.[0]?.tariffs || []).map((t) => t.id).join(',');

  console.log('\n========== VERDICT ==========');
  if (t1 !== t0 && t2 !== t0) {
    console.log('✅ Tariff updated in both cases — no server cache issue.');
  } else if (t1 === t0 && t2 !== t0) {
    console.log('🐛 SERVER CACHE CONFIRMED: tariff only changed after relogin.');
    console.log('   Apply the AUTO-LOGOUT+LOGIN fix in useChangeTariff.onSuccess.');
  } else if (t1 === t0 && t2 === t0) {
    console.log('❌ Tariff NOT updated AT ALL — check server or payload.');
  } else {
    console.log('❓ Partial — investigate raw API responses above.');
  }
})();
