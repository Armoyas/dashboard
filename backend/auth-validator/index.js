// auth-validator/index.js
// Simple validator for nginx auth_request — checks Casdoor subscriptions as source of truth
const express = require('express');
const { Pool } = require('pg');

const app = express();

const PORT = process.env.PORT || 3210;
const UPSTREAM_SESSION_URL =
  process.env.UPSTREAM_SESSION_URL || 'http://network-service:3210/api/auth/get-session';
const UPSTREAM_SESSION_HOST = process.env.UPSTREAM_SESSION_HOST || '';

const CASDOOR_ENDPOINT = (process.env.CASDOOR_ENDPOINT || 'https://auth.smart98.ir').replace(/\/$/, '');
const CASDOOR_OWNER = (process.env.CASDOOR_OWNER || 'smart98').trim();
const CASDOOR_CLIENT_ID = (process.env.CASDOOR_CLIENT_ID || '').trim();
const CASDOOR_CLIENT_SECRET = (process.env.CASDOOR_CLIENT_SECRET || '').trim();

const DB_URL = process.env.DATABASE_URL || 'postgresql://postgres:postgres@lobe-postgres:5432/dbsmart98';
const pool = new Pool({ connectionString: DB_URL });

const fetchFn =
  typeof fetch === 'function'
    ? fetch
    : (...args) => import('node-fetch').then((m) => m.default(...args));

function log(...args) {
  console.log(new Date().toISOString(), ...args);
}

/**
 * Normalize plan string to 'paid-user' or 'normal-user'
 */
function normalizePlan(value) {
  return String(value ?? '').trim().toLowerCase() === 'paid-user' ? 'paid-user' : 'normal-user';
}

/**
 * Check if a subscription is truly active.
 * ONLY 'active' state counts — not pending, upcoming, expired, suspended.
 * Also checks endTime is not in the past.
 */
function isActiveSubscription(sub) {
  if (!sub || typeof sub !== 'object') return false;
  const state = String(sub.state || sub.status || sub.phase || sub.kind || '').trim().toLowerCase();
  // Only 'active' is a usable state
  if (state !== 'active') return false;
  const endRaw = sub.endTime || sub.end_time || sub.end || sub.expiredAt || '';
  const endDate = endRaw ? new Date(endRaw) : null;
  if (!endDate || Number.isNaN(endDate.getTime())) return true; // no end date = perpetual = active
  return endDate >= new Date();
}

async function fetchJson(url, opts = {}) {
  const resp = await fetchFn(url, opts);
  const rawText = await resp.text();
  let body = null;
  try {
    body = rawText ? JSON.parse(rawText) : null;
  } catch {
    body = null;
  }
  return { resp, body, rawText };
}

function extractSessionUser(sessionBody) {
  if (!sessionBody) return null;
  return sessionBody.user || sessionBody.session?.user || sessionBody;
}

/**
 * UUID regex pattern (case-insensitive)
 */
const UUID_REGEX = /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/;

/**
 * Extract Casdoor UUID from user object.
 * Checks full_name, email, and direct UUID fields.
 */
function extractCasdoorUuid(user) {
  if (!user) return '';

  // 1. Check if full_name is a UUID (LobeChat stores Casdoor UUID in full_name for Casdoor users)
  const fullName = String(user.full_name || user.fullName || '').trim();
  if (fullName && UUID_REGEX.test(fullName)) {
    return fullName;
  }

  // 2. Check email for casdoor-<UUID>@ pattern
  const email = String(user.email || '').trim();
  if (email) {
    const match = email.match(/casdoor-([0-9a-fA-F-]{36})@/);
    if (match) return match[1];
  }

  // 3. Check externalId — some setups store UUID here
  const externalId = String(user.externalId || user.external_id || '').trim();
  if (externalId && UUID_REGEX.test(externalId)) {
    return externalId;
  }

  // 4. Direct username/name — return if it looks like a UUID
  const direct = [user.username, user.name];
  for (const v of direct) {
    const val = String(v ?? '').trim();
    if (val && UUID_REGEX.test(val)) return val;
  }

  // 5. Fallback to id (LobeChat DB ID like user_xxx — not a UUID but may be Casdoor username)
  return String(user.id || '').trim();
}

/**
 * GET the Casdoor username to use for API lookups.
 * For Casdoor users, this should be the UUID (stored in full_name).
 * For regular users, it may be a username string.
 */
function getCasdoorUsername(user) {
  if (!user) return '';

  // Build a list of possible identifiers in priority order
  // For Casdoor-authenticated users, we want the UUID, not the LobeChat DB ID
  const identifiers = [
    user?.username,
    user?.name,
    user?.externalId,
    user?.external_id,
  ];

  // Check if any direct identifier is a UUID
  for (const v of identifiers) {
    const val = String(v ?? '').trim();
    if (val && UUID_REGEX.test(val)) {
      return val;
    }
  }

  // Extract UUID from full_name or email
  const uuid = extractCasdoorUuid(user);
  if (uuid && UUID_REGEX.test(uuid)) {
    return uuid;
  }

  // If no UUID found, return the first non-empty identifier
  for (const v of identifiers) {
    const val = String(v ?? '').trim();
    if (val.length > 0) return val;
  }

  // Fallback to id
  return String(user?.id ?? '').trim();
}

/**
 * Get Casdoor user object and its type field.
 * This is a CACHED value — may be stale if the pay service hasn't run its expiry loop yet.
 * Always treat subscriptions as authoritative; use this only as fallback.
 */
async function resolveCasdoorUser(casdoorUsername) {
  if (!CASDOOR_CLIENT_ID || !CASDOOR_CLIENT_SECRET || !casdoorUsername) return null;
  try {
    const url =
      `${CASDOOR_ENDPOINT}/api/get-user?` +
      new URLSearchParams({
        id: `${CASDOOR_OWNER}/${casdoorUsername}`,
        clientId: CASDOOR_CLIENT_ID,
        clientSecret: CASDOOR_CLIENT_SECRET,
      }).toString();
    log('[auth-validator] querying casdoor user:', url.replace(CASDOOR_CLIENT_SECRET, '***'));
    const { resp, body, rawText } = await fetchJson(url, {
      method: 'GET',
      headers: { Accept: 'application/json' },
    });
    log('[auth-validator] get-user status:', resp.status);
    if (resp.status !== 200 || !body) return null;
    const casdoorUser = body.data || body;
    if (!casdoorUser || typeof casdoorUser !== 'object') return null;
    const userType = normalizePlan(
      casdoorUser.type || casdoorUser.role || casdoorUser.status || casdoorUser.plan || ''
    );
    return { user: casdoorUser, userType };
  } catch (error) {
    log('[auth-validator] get-user failed:', error?.message || error);
    return null;
  }
}

/**
 * Check if the user has ANY active subscription.
 * Scoped to the specific user — not all subscriptions for the owner.
 * Also tries fallback username lookup if UUID-based lookup returns nothing.
 */
async function resolveActiveSubscription(casdoorUsername) {
  if (!CASDOOR_CLIENT_ID || !CASDOOR_CLIENT_SECRET || !casdoorUsername) return false;
  try {
    // First try with the resolved username/UUID
    const params = new URLSearchParams({
      owner: CASDOOR_OWNER,
      user: casdoorUsername,
      clientId: CASDOOR_CLIENT_ID,
      clientSecret: CASDOOR_CLIENT_SECRET,
    });
    const url = `${CASDOOR_ENDPOINT}/api/get-subscriptions?${params.toString()}`;
    log('[auth-validator] querying subscriptions:', url.replace(CASDOOR_CLIENT_SECRET, '***'));
    const { resp, body, rawText } = await fetchJson(url, {
      method: 'GET',
      headers: { Accept: 'application/json' },
    });
    log('[auth-validator] get-subscriptions status:', resp.status);

    let subs = [];
    if (resp.status === 200 && body) {
      subs = Array.isArray(body?.data) ? body.data : Array.isArray(body) ? body : [];
    }

    // If no results, try fetching all subscriptions and filtering locally
    if (subs.length === 0) {
      log('[auth-validator] no results with user param, trying local filter...');
      const allParams = new URLSearchParams({
        owner: CASDOOR_OWNER,
        clientId: CASDOOR_CLIENT_ID,
        clientSecret: CASDOOR_CLIENT_SECRET,
      });
      const allUrl = `${CASDOOR_ENDPOINT}/api/get-subscriptions?${allParams.toString()}`;
      const allResult = await fetchJson(allUrl, {
        method: 'GET',
        headers: { Accept: 'application/json' },
      });
      if (allResult.resp.status === 200 && allResult.body) {
        const allSubs = Array.isArray(allResult.body?.data) ? allResult.body.data : Array.isArray(allResult.body) ? allResult.body : [];
        // Filter by user field matching our username OR UUID
        const uuid = extractCasdoorUuid({ id: casdoorUsername, full_name: casdoorUsername });
        subs = allSubs.filter((sub) => {
          const subUser = String(sub.user || sub.userId || '').trim();
          return subUser === casdoorUsername || (uuid && subUser === uuid);
        });
      }
    }

    log('[auth-validator] subscriptions for', casdoorUsername, ':', subs.length);
    // Only count subscriptions that are active
    return subs.some((sub) => isActiveSubscription(sub));
  } catch (error) {
    log('[auth-validator] get-subscriptions failed:', error?.message || error);
    return false;
  }
}

/**
 * Sync the plan in LobeChat's users table if it differs from reality.
 */
async function syncUserPlan(userId, currentPlan, realPlan) {
  if (realPlan === currentPlan) return;
  try {
    log('[auth-validator] Plan mismatch: session=', currentPlan, ', real=', realPlan, '. Updating DB...');
    // Match by id OR full_name OR email containing the user_id (which may be a UUID)
    const uuidMatch = UUID_REGEX.test(userId);
    if (uuidMatch) {
      await pool.query(
        'UPDATE users SET plan = $1 WHERE id = $2 OR full_name = $2 OR email LIKE $3',
        [realPlan, userId, `%${userId}%`]
      );
    } else {
      await pool.query('UPDATE users SET plan = $1 WHERE id = $2', [realPlan, userId]);
    }
    log('[auth-validator] Database updated successfully');
  } catch (err) {
    log('[auth-validator] Failed to update plan in DB:', err.message);
  }
}

// ---------------------------------------------------------------------------
// Main auth endpoint — called by nginx auth_request
// ---------------------------------------------------------------------------
app.get('/api/auth/validate-paid', async (req, res) => {
  try {
    log('=============================');
    log('=== auth-validate request ===');
    log('remote ip:', req.ip);

    const cookieHeader = req.get('cookie');
    if (!cookieHeader) {
      return res.status(401).json({ error: 'Authentication required', userType: 'normal-user' });
    }

    const hostHeader =
      UPSTREAM_SESSION_HOST ||
      req.get('x-original-host') ||
      req.get('host') ||
      (() => { try { return new URL(UPSTREAM_SESSION_URL).host; } catch { return ''; } })();

    // 1. Fetch session from upstream network service
    const sessionResult = await fetchJson(UPSTREAM_SESSION_URL, {
      method: 'GET',
      headers: {
        Cookie: cookieHeader,
        Accept: 'application/json',
        ...(hostHeader ? { Host: hostHeader } : {}),
      },
    });

    if (sessionResult.resp.status !== 200) {
      return res.status(401).json({ error: 'Invalid session', userType: 'normal-user' });
    }

    const user = extractSessionUser(sessionResult.body);
    if (!user) {
      return res.status(401).json({ error: 'User not found', userType: 'normal-user' });
    }

    // Log user keys for debugging
    log('[auth-validator] session user keys:', Object.keys(user).join(', '));
    log('[auth-validator] session user.id:', user.id);
    log('[auth-validator] session user.full_name:', user.full_name || user.fullName);
    log('[auth-validator] session user.email:', user.email);
    log('[auth-validator] session user.username:', user.username);
    log('[auth-validator] session user.name:', user.name);

    const casdoorUsername = getCasdoorUsername(user);
    if (!casdoorUsername) {
      return res.status(401).json({ error: 'Casdoor username missing', userType: 'normal-user' });
    }
    log('[auth-validator] casdoor username:', casdoorUsername);

    const currentPlan = normalizePlan(user.plan || user.userType || 'normal-user');

    // 2. AUTHORITATIVE CHECK: subscriptions first
    let realPlan = 'normal-user';
    const hasActiveSubscription = await resolveActiveSubscription(casdoorUsername);
    if (hasActiveSubscription) {
      realPlan = 'paid-user';
      log('[auth-validator] user has active subscription → paid-user');
    } else {
      // Fallback: check Casdoor user.type
      const casdoorUserResult = await resolveCasdoorUser(casdoorUsername);
      if (casdoorUserResult?.userType === 'paid-user') {
        realPlan = 'paid-user';
        log('[auth-validator] casdoor user.type says paid-user (fallback)');
      } else {
        log('[auth-validator] no active subscription and casdoor type is not paid-user → normal-user');
        if (casdoorUserResult) {
          log('[auth-validator] casdoor user.type:', casdoorUserResult.userType);
        }
      }
    }

    // 3. Sync LobeChat DB if needed
    await syncUserPlan(user.id, currentPlan, realPlan);

    // 4. Respond
    res.set('X-User-Type', realPlan);
    res.set('X-User-Plan', realPlan);
    res.set('X-User-Id', casdoorUsername);
    res.set('X-User-Sub', casdoorUsername);

    if (realPlan === 'paid-user') {
      return res.status(200).json({ ok: true, userType: 'paid-user' });
    }
    return res.status(403).json({ error: 'Paid subscription required', userType: 'normal-user' });
  } catch (err) {
    console.error('[auth-validator] unexpected error:', err);
    return res.status(500).json({ error: 'Auth validator error', details: String(err) });
  }
});

app.listen(PORT, () => {
  console.log(`auth-validator listening on ${PORT}`);
});
